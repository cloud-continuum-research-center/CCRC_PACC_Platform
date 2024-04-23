# main.py
import threading
import torch
import torch.nn as nn
import torch.optim as optim
from Node import Node, parse_address
import argparse
from torchvision import datasets, transforms
from torch.utils.data import DataLoader
from torch.utils.data import Subset
import numpy as np


class SimpleCNN(nn.Module):
    def __init__(self):
        super(SimpleCNN, self).__init__()
        self.conv1 = nn.Conv2d(1, 8, kernel_size=3, padding=1)
        self.conv2 = nn.Conv2d(8, 16, kernel_size=3, padding=1)
        self.fc1 = nn.Linear(16 * 7 * 7, 64)
        self.fc2 = nn.Linear(64, 10)
        self.pool = nn.MaxPool2d(2, 2)
        self.relu = nn.ReLU()

    def forward(self, x):
        x = self.pool(self.relu(self.conv1(x)))
        x = self.pool(self.relu(self.conv2(x)))
        x = x.view(-1, 16 * 7 * 7)
        x = self.relu(self.fc1(x))
        x = self.fc2(x)
        return x

def train(node):
    node.model.train()
    total_loss = 0
    total_samples = 0

    for inputs, targets in node.data_loader:
        inputs, targets = inputs.to(node.device), targets.to(node.device)
        node.optimizer.zero_grad()
        outputs = node.model(inputs)
        loss = node.loss_function(outputs, targets)
        loss.backward()
        node.optimizer.step()

        total_loss += loss.item() * inputs.size(0)
        total_samples += inputs.size(0)

    avg_train_loss = total_loss / total_samples
    return {'train_loss': avg_train_loss}

def evaluate_model(node):
    node.model.eval()
    total_loss = 0
    total_samples = 0
    correct_predictions = 0

    with torch.no_grad():
        for inputs, targets in node.validation_loader:
            inputs, targets = inputs.to(node.device), targets.to(node.device)
            outputs = node.model(inputs)
            loss = node.loss_function(outputs, targets)

            total_loss += loss.item() * inputs.size(0)
            _, predicted = torch.max(outputs.data, 1)
            correct_predictions += (predicted == targets).sum().item()
            total_samples += inputs.size(0)

    avg_loss = total_loss / total_samples
    accuracy = 100 * correct_predictions / total_samples
    return {'evaluate_loss': avg_loss, 'accuracy': accuracy}

def parse_arguments():
    parser = argparse.ArgumentParser(description="RUDP Node Configuration")
    parser.add_argument('--local-port', type=int, required=True, help="Local port for the node")
    parser.add_argument('--parent-address', type=str, help="Parent node address in the format ip:port")
    parser.add_argument('--child-addresses', nargs='*', default=[], help="List of child node addresses in the format ip:port")
    parser.add_argument('--epochs', type=int, default=10, help="Number of training epochs")
    parser.add_argument('--save-path', type=str, default="model_weights.pth", help="Path to save the trained model")
    parser.add_argument('--batch_size', type=int, default=32, help="Batch size for training")
    args = parser.parse_args()
    return args

if __name__ == '__main__':
    args = parse_arguments()

    # Simple CNN 모델 생성
    model = SimpleCNN()
    model.to(torch.device("cuda" if torch.cuda.is_available() else "cpu"))

    # MNIST 데이터셋을 위한 변환 정의
    transform = transforms.Compose([
        transforms.ToTensor(),
        transforms.Normalize((0.5,), (0.5,))
    ])

    # MNIST 데이터셋 로드
    train_dataset = datasets.MNIST(root='./data', train=True, download=True, transform=transform)
    test_dataset = datasets.MNIST(root='./data', train=False, download=True, transform=transform)

    num_samples = 1000
    train_indices = np.random.choice(len(train_dataset), num_samples, replace=False)
    test_indices = np.random.choice(len(test_dataset), num_samples, replace=False)

    train_subset = Subset(train_dataset, train_indices)
    test_subset = Subset(test_dataset, test_indices)

    train_dataloader = DataLoader(train_subset, batch_size=args.batch_size, shuffle=True)
    val_dataloader = DataLoader(test_subset, batch_size=args.batch_size, shuffle=False)
    
    loss_function = nn.CrossEntropyLoss()
    optimizer = optim.SGD(model.parameters(), lr=0.01, momentum=0.9)

    node = Node(args.local_port, args.parent_address, args.child_addresses, model, train_dataloader, val_dataloader, loss_function, optimizer, args.epochs, args.save_path, train_func=train, evaluate_model_func=evaluate_model)
    node.start()
