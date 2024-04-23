# main.py
import threading
import torch
import torch.nn as nn
import torch.optim as optim
from Node import Node, parse_address
import argparse



class SimpleModel(nn.Module):
    def __init__(self):
        super(SimpleModel, self).__init__()
        self.fc = nn.Linear(10, 1)  # 입력 크기 10, 출력 크기 1

    def forward(self, x):
        return self.fc(x)


if __name__ == '__main__':
    
    model = SimpleModel()
    loss_function = nn.MSELoss()
    optimizer = optim.SGD(model.parameters(), lr=0.01)
    data_loader = [(torch.randn(10), torch.randn(1)) for _ in range(100)]  # Random data loader

    node = Node(local_port, parent_address, child_addresses, model, data_loader, loss_function, optimizer, epochs, save_path)
    # 배치 사이즈
    # if 문으로 활성화 함수 등 외부에서 프레임워크 사용할 수 있게음
    # 민철 모니터링 파트
    # 매 에포크마다 Loss값, Acc 저장, 에포크 끝나면 리스트 출력
    # 학습 전체 끝나면 최종 Loss, Acc 출력
    node.start()

    if(node.is_running == False):
        print("Training finished. Exiting.")

    node.stop_training() # 루트 노드만 수행
           