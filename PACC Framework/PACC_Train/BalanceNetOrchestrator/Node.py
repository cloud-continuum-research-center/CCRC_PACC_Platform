from RUDP import RUDP
import torch
import threading
import io

def parse_address(address):
    if ':' in address:
        ip, port = address.split(':')
        return ip, int(port)
    return None, None

class Node:
    def __init__(self, local_port, parent_address=None, children_addresses=None, model=None,
                 data_loader=None, validation_loader=None, loss_function=None, optimizer=None,
                 epochs=10, save_path=None, batch_size=32, reset_state_function=None, retain_graph=False,
                 train_func=None, evaluate_model_func=None,):
        self.rudp = RUDP(local_port, self.handle_message)
        self.parent_address = parse_address(parent_address) if parent_address else None
        self.children_addresses = [parse_address(child) for child in children_addresses] if children_addresses else []
        
        self.data_loader = data_loader
        self.loss_function = loss_function
        self.optimizer = optimizer
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model = model.to(self.device)
        self.epochs = epochs
        self.validation_loader = validation_loader
        self.ready_children = set()
        self.last_processed_message_ids = {}
        self.received_weights = {}
        self.save_path = save_path
        self.max_processed_ids = 100
        self.train_func = train_func
        self.evaluate_model_func = evaluate_model_func
        self.children_weights_event = threading.Event()
        self.wait_for_update = threading.Event()
        self.training_thread = None
        self.update_weights_count = 0
        self.is_running = True
        self.is_Done = False
        self.testcount = 0
        self.current_state = 0
        self.reset_state_function = reset_state_function
        self.metrics = []  # 에포크별 성능 메트릭스를 저장할 리스트
        self.retain_graph = retain_graph

    def start(self):
        if not self.children_addresses:
            self.send_ready_to_parent()

    def get_metrics(self):
        organized_metrics = {}
        for metric_dict in self.metrics:
            for key, value in metric_dict.items():
                if key not in organized_metrics:
                    organized_metrics[key] = [value]
                else:
                    organized_metrics[key].append(value)
        return organized_metrics


    def send_message_to_parent(self, message):
        if self.parent_address:
            self.rudp.send_message(message, self.parent_address)

    def send_message_to_children(self, message):
        for child_address in self.children_addresses:
            self.rudp.send_message(message, child_address)

    def send_ready_to_parent(self):
        if self.parent_address:
            print("Sending ready to parent:", self.parent_address)
            ready_message = {'signal': 'ready', 'value': 'ready'}
            self.send_message_to_parent(ready_message)

    def check_children_ready(self):
        print(f"Ready children: {self.ready_children}")
        print(len(self.ready_children))
        print(len(self.children_addresses))
        if len(self.ready_children) == len(self.children_addresses):
            print("All children are ready")
            self.is_ready = True
            if self.parent_address:
                self.send_ready_to_parent()
            else:
                # 루트 노드에서 모든 자식 노드가 ready 상태일 때 학습 시작 신호를 브로드캐스트합니다.
                print("All nodes are ready, broadcasting start signal")
                self.start_training()
                self.broadcast_message('start', 'training parameters or configuration')

    def broadcast_message(self, signal, value=None):
        if signal == 'ready':
            if self.children_addresses:
                print("Reached the last child, no more broadcasting needed.")
                return
            message = {'signal': signal, 'value': value}
            print(f"Broadcasting message from {self.parent_address if self.parent_address else 'root'}")
            for child_address in self.children_addresses:
                self.rudp.send_message(message, child_address)
        
        else:
            message = {'signal': signal, 'value': value}
            print(f"Broadcasting message from {self.parent_address if self.parent_address else 'root'}: {len(value)}")
            for child_address in self.children_addresses:
                print(f"Sending message to {child_address}")
                self.rudp.send_message(message, child_address)
    
    def stop_training(self):
        if not self.parent_address:
            self.end_training()

    def start_training(self):
        self.training_thread = threading.Thread(target=self.train)
        self.training_thread.start()
        print(f"Training started at node {self.parent_address if self.parent_address else 'root'}")

    def train(self):
        
        
        print("Training started.")
        print("epochs Count  :" , self.epochs)
        for epoch in range(self.epochs):
            
            self.metrics.append(self.train_func(self))
            
            print("current  : ", epoch," / ", int(self.epochs))
            
            ########## 가중치 업데이트 ##########

            if self.children_addresses: # 중간 노드, 루트 노드
                print("Waiting for children's weights...")
                while self.is_running:
                    if len(self.received_weights) == len(self.children_addresses):

                        print("All weights received from children.")
                        self.children_weights_event.set()  # 이벤트 트리거
                        # 가중치 처리 후
                        aggregated_weights = self.aggregate_weights()
                        self.model.load_state_dict(aggregated_weights)  # 모델 가중치 업데이트

                        # 집계된 가중치를 부모 노드로 전송
                        if self.parent_address:
                            self.send_weight_to_parent(aggregated_weights)
                        else:
                            torch.save(self.model.state_dict(), self.save_path + ".pth")
                            # 루트 노드인 경우 모든 자식에게 업데이트된 가중치 전송
                            print("Broadcasting updated weights and starting next epoch training at root node.")
                            self.broadcast_update(aggregated_weights)

                        # Event 상태 초기화
                        self.children_weights_event.clear()
                        self.received_weights.clear()  # 가중치 버퍼 초기화
                        break

                print("All children's weights received.")
            else: # 자식 노드
                weights = self.model.state_dict()
                self.send_weight_to_parent(weights)

            print("current ", self.update_weights_count," / ", int(self.epochs))

            if self.parent_address:
                self.wait_for_update.wait()

            if self.is_running == False:
                print("Training finished. Exiting.")
                break
            ########## 가중치 업데이트 ##########

            #검증 세트 성능 평가

            epoch_metrics = self.evaluate_model_func(self)  # 평가 함수 실행
            self.metrics.append(epoch_metrics)  # 에포크 결과를 메트릭스 리스트에 추가
            
            #print(f"Epoch {epoch+1} - Validation Loss: {self.metrics['evaluate_loss']:.4f}, Accuracy: {self.metrics['evaluate_accuracy']:.2f}%")
            # 검증 세트 성능 평가
                
        print("Training complete.")
        if not self.parent_address:
            print("Broadcasting end training signal to all nodes.")
            self.end_training()

    '''
    def evaluate_model(self, data_loader, loss_function, device):
        self.model.eval()
        total_loss = 0
        correct_predictions = 0
        total_samples = 0

        with torch.no_grad():
            for inputs, targets in data_loader:
                inputs, targets = inputs.to(device), targets.to(device)
                outputs = self.model(inputs)
                
                loss = loss_function(outputs, targets)
                total_loss += loss.item()
                
                predicted = (outputs > 0.5).int()  # 이진 분류를 가정, 필요에 따라 수정
                correct_predictions += (predicted == targets).sum().item()
                total_samples += targets.size(0)

        avg_loss = total_loss / len(data_loader)
        accuracy = correct_predictions / total_samples * 100
        return avg_loss, accuracy
        '''

    def process_received_weights(self, weights, addr):
            print(f"Processing received weights from {addr}")
            normalized_addr = (addr[0], addr[1])
            map_location = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
            buffer = io.BytesIO(weights)
            model_weights = torch.load(buffer, map_location=map_location)
            self.received_weights[normalized_addr] = model_weights
            print(f"Weights received from child {addr}")  

    def wait_for_children_weights(self):
        # 자식 노드들로부터 모든 가중치를 수신할 때까지 대기
        self.children_weights_event.wait()

    def end_training(self):
        print("TrainingTrainingTrainingTrainingTrainingTrainingTrainingTraining ended.")
        print(self.get_metrics())
        self.current_state = 2
        if not self.parent_address:
            # 루트 노드인 경우, 모든 자식에게 학습 종료 신호 전송
            print("Broadcasting end training signal to all nodes.")
            self.broadcast_message('done', 'done')

            print(f"Model saved to {self.save_path}.")
            print("Shutting down the training program.")

            print(f"Final model weights updated at root node, saving to {self.save_path}.")
            torch.save(self.model.state_dict(), self.save_path + ".pth")
            self.is_running = False

            self.rudp.stop_receiving()
            
            exit(0)
            
        print(f"Training ended at node {self.parent_address if self.parent_address else 'root'}. Saving model...")
        # 모델 저장 로직 여기에 추가
        print("Shutting down the training program.")

        self.send_message_to_parent({'signal': 'exit', 'value': 'exit'})
        self.is_running = False
        
        self.wait_for_update.set()
        self.wait_for_update.clear()

        self.rudp.stop_receiving()
        exit(0)

    def send_weight_to_parent(self, weights):
        print(f"Sending weights to parent First {self.parent_address}")
        if self.parent_address:

            print(f"Sending weights to parent Second {self.parent_address}")
            buffer = io.BytesIO()
            torch.save(weights, buffer)
            buffer.seek(0)
            serialized_weights = buffer.getvalue()
            self.testcount += 1
            print(f"Sending weights to parent {self.testcount}")
            weight_message = {'signal': 'sendweight', 'value': serialized_weights}
            self.rudp.send_message(weight_message, self.parent_address)
            self.received_weights['weights_sent'] = True

    def handle_message(self, message, addr):
        print(f"Received message from {addr}")

        if isinstance(message, dict) and 'signal' in message:
            signal = message['signal']
            message_id = message.get('id', None)

            if addr not in self.last_processed_message_ids:
                self.last_processed_message_ids[addr] = set()

            if len(self.last_processed_message_ids[addr]) > self.max_processed_ids:
                print(f"Resetting message ID buffer for {addr}")
                self.last_processed_message_ids[addr].clear()

            # 중복 메시지 검사
            if message_id and message_id in self.last_processed_message_ids[addr]:
                print(f"Duplicated message {message_id} from {addr} ignored.")
              

            self.last_processed_message_ids[addr].add(message_id)

            print(f"Received signal from {addr}: {signal}")

            if signal == 'ready':
                normalized_addr = (addr[0], addr[1])
                self.ready_children.add(normalized_addr)
                self.check_children_ready()

            elif signal == 'exit':
                if not self.parent_address:
                    self.rudp.stop_receiving()
                    exit(0)

            elif signal == 'start':
                if not self.training_thread or not self.training_thread.is_alive():
                    self.start_training()
                self.broadcast_message(signal, message.get('value'))

            elif signal == 'sendweight':
                self.update_weights_count += 1
                self.process_received_weights(message.get('value'), addr)

            elif signal == 'updateweight':
                self.update_weights(message.get('value'))

            elif signal == 'done':
                print(f"Training complete at node {addr}.")
                self.broadcast_message('done', 'done')  # 자식 노드들에게 신호 전파
                self.rudp.stop_receiving()
                self.end_training()

            else:
                print(f"Received unknown signal from {addr}: {message}")

        else:
            print(f"Received non-dict message from {addr}: {message}")


    def broadcast_update(self, weights):
        # 직렬화된 가중치를 모든 자식 노드에게 전송
        serialized_weights = self.serialize_weights(weights)
        for child_address in self.children_addresses:
            print(f"Sending updated weights to {child_address}")
            update_message = {'signal': 'updateweight', 'value': serialized_weights}
            self.rudp.send_message(update_message, child_address)

    def aggregate_weights(self):
        # 모든 받은 가중치에 대한 평균을 계산합니다.
        aggregated_weights = {}
        count = len(self.received_weights)

        if count == 0:
            raise ValueError("No weights received from any children.")

        # received_weights의 복사본을 만들어 순회
        received_weights_copy = self.received_weights.copy()

        for weight in received_weights_copy.values():
            for k, v in weight.items():
                # 모든 텐서를 float 타입으로 변환하여 처리
                v_converted = v.to(torch.float32)
                if k not in aggregated_weights:
                    aggregated_weights[k] = v_converted.clone()  # 가중치 복제
                else:
                    aggregated_weights[k] += v_converted

        # 평균 가중치 계산
        for k in aggregated_weights.keys():
            aggregated_weights[k] /= count  # 평균 계산 시 float 타입으로 나누기

        return aggregated_weights

    def update_weights(self, value):
        print(f"Updating weights at node {self.parent_address}")
        # CUDA 사용 가능 여부 확인
        map_location = 'cuda' if torch.cuda.is_available() else 'cpu'

        # value가 이미 딕셔너리 형태의 모델 가중치라면 직접 사용
        if isinstance(value, dict):
            model_weights = value
        else:
            # value가 바이트 형태라면 역직렬화 과정 수행
            buffer = io.BytesIO(value)
            model_weights = torch.load(buffer, map_location=map_location)

        # 모델 가중치 업데이트
        self.model.load_state_dict(model_weights)
        self.wait_for_update.set()
        self.wait_for_update.clear()

        # 자식 노드들에게 업데이트된 가중치 전송
        if self.children_addresses:
            self.broadcast_update(model_weights)

    def serialize_weights(self, weights):
        buffer = io.BytesIO()
        torch.save(weights, buffer)
        buffer.seek(0)
        return buffer.getvalue()