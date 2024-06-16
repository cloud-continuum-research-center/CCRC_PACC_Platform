import threading
import pickle
import socket
import time
from concurrent.futures import ThreadPoolExecutor

BUFFER_SIZE = 60000
HEADER_SIZE = 64
ACK_TIMEOUT = 2  # Timeout in seconds for retransmissions
MAX_RETRANSMITS = 5  # Maximum number of retransmissions for any packet

class RUDP:
    def __init__(self, local_port, message_callback):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(('', local_port))
        self.sock.settimeout(ACK_TIMEOUT)
        self.packet_buffer = {}
        self.is_receiving = True
        self.message_callback = message_callback
        self.send_lock = threading.Lock()
        self.ack_received = {}
        self.retransmit_count = {}
        self.thread_pool = ThreadPoolExecutor(max_workers=10)
        self.receive_thread = threading.Thread(target=self.receive_process)
        self.receive_thread.start()
        self.is_shutting_down = False  # 쓰레드 풀 종료 상태 플래그 추가

    def safe_submit_task(self, func, *args, **kwargs):
        if not self.is_shutting_down:
            self.thread_pool.submit(func, *args, **kwargs)
        else:
            print("ThreadPoolExecutor is shutting down, cannot submit new tasks.")

    def send_message(self, message, remote_address):
        with self.send_lock:
            serialized_message = pickle.dumps(message)
            total_packets = (len(serialized_message) + BUFFER_SIZE - 1) // BUFFER_SIZE

            for i in range(total_packets):
                packet_header = pickle.dumps((i, total_packets))
                packet_header = packet_header.ljust(HEADER_SIZE, b'\0')
                packet_data = serialized_message[i * BUFFER_SIZE: (i + 1) * BUFFER_SIZE]
                packet = packet_header + packet_data
                self.sock.sendto(packet, remote_address)
                self.ack_received[(remote_address, i)] = False
                self.retransmit_count[(remote_address, i)] = 0

                # 안전하게 작업 제출
                self.safe_submit_task(self.ensure_packet_delivery, packet, remote_address, i)

    def ensure_packet_delivery(self, packet, remote_address, seq_num):
        while not self.ack_received[(remote_address, seq_num)] and self.retransmit_count[(remote_address, seq_num)] < MAX_RETRANSMITS:
            time.sleep(ACK_TIMEOUT)
            if not self.ack_received[(remote_address, seq_num)]:
                self.sock.sendto(packet, remote_address)
                self.retransmit_count[(remote_address, seq_num)] += 1
                print(f"Retransmitting packet {seq_num} to {remote_address}")
        if self.retransmit_count[(remote_address, seq_num)] >= MAX_RETRANSMITS:
            print(f"Failed to deliver packet {seq_num} after {MAX_RETRANSMITS} attempts")

    def receive_process(self):
        while self.is_receiving:
            try:
                packet, addr = self.sock.recvfrom(BUFFER_SIZE + HEADER_SIZE)
                header_data = packet[:HEADER_SIZE].rstrip(b'\0')
                try:
                    seq_num, total_packets = pickle.loads(header_data)
                    seq_num = int(seq_num)
                    is_ack = False
                except ValueError:
                    is_ack, seq_num = pickle.loads(header_data)
                    if is_ack == 'ACK':
                        is_ack = True
                        seq_num = int(seq_num)

                if is_ack:
                    self.ack_received[(addr, seq_num)] = True
                    print(f"Received ACK for packet {seq_num} from {addr}")
                else:
                    data = packet[HEADER_SIZE:]
                    print(f"Received packet {seq_num + 1}/{total_packets} from {addr}")

                    if addr not in self.packet_buffer:
                        self.packet_buffer[addr] = [None] * total_packets
                    self.packet_buffer[addr][seq_num] = data

                    ack_packet = pickle.dumps(('ACK', seq_num))
                    self.sock.sendto(ack_packet, addr)

                    if all(part is not None for part in self.packet_buffer[addr]):
                        complete_data = b''.join(self.packet_buffer[addr])
                        self.process_complete_message(complete_data, addr)
                        del self.packet_buffer[addr]
            except socket.timeout:
                continue

    def process_complete_message(self, complete_data, addr):
        message = pickle.loads(complete_data)
        self.message_callback(message, addr)

    def stop_receiving(self):
        self.is_receiving = False
        self.is_shutting_down = True  # 쓰레드 풀 종료 상태로 설정
        if threading.current_thread() != self.receive_thread:
            self.receive_thread.join()
        self.thread_pool.shutdown(wait=True)
