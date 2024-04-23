import threading
import pickle
import socket

BUFFER_SIZE = 60000
HEADER_SIZE = 64

class RUDP:
    def __init__(self, local_port, message_callback):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(('', local_port))
        self.packet_buffer = {}
        self.is_receiving = True
        self.message_callback = message_callback
        self.receive_thread = threading.Thread(target=self.receive_process)
        self.receive_thread.start()

    def send_message(self, message, remote_address):
        serialized_message = pickle.dumps(message)
        total_packets = (len(serialized_message) + BUFFER_SIZE - 1) // BUFFER_SIZE

        print(f"Sending {total_packets} packets to {remote_address}")

        for i in range(total_packets):
            packet_header = pickle.dumps((i, total_packets))
            packet_header = packet_header.ljust(HEADER_SIZE, b'\0')
            packet_data = serialized_message[i * BUFFER_SIZE: (i + 1) * BUFFER_SIZE]
            packet = packet_header + packet_data
            self.sock.sendto(packet, remote_address)

    def receive_process(self):
        while self.is_receiving:
            packet, addr = self.sock.recvfrom(BUFFER_SIZE + HEADER_SIZE)
            header_data = packet[:HEADER_SIZE].rstrip(b'\0')
            seq_num, total_packets = pickle.loads(header_data)
            data = packet[HEADER_SIZE:]

            print(f"Received packet {seq_num + 1}/{total_packets} from {addr}")

            if addr not in self.packet_buffer:
                self.packet_buffer[addr] = [None] * total_packets
            self.packet_buffer[addr][seq_num] = data

            if all(part is not None for part in self.packet_buffer[addr]):
                complete_data = b''.join(self.packet_buffer[addr])
                message = pickle.loads(complete_data)
                self.message_callback(message, addr)  # Call the callback function with the complete message
                del self.packet_buffer[addr]

    def handle_received_message(self, message, addr):
        # 메시지 처리 로직
        print(f"Complete message received from {addr}: {message}")
            
    def stop_receiving(self):
        self.is_receiving = False
        if threading.current_thread() != self.receive_thread:
            self.receive_thread.join()