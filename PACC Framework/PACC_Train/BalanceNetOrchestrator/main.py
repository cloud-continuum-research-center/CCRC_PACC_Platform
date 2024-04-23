import threading
import torch
import torch.nn as nn
import torch.optim as optim
import argparse
import yfinance as yf
from Node import Node, parse_address
from torch.utils.data import DataLoader, TensorDataset
from sklearn.preprocessing import MinMaxScaler
import numpy as np

class SimpleTimeSeriesModel(nn.Module):
    def __init__(self, seq_length, num_features, feature_length, hidden_size, output_size=1):
        super(SimpleTimeSeriesModel, self).__init__()
        total_input_size = seq_length * num_features * feature_length  # 10 * 5 * 10 = 500
        self.flatten = nn.Flatten()
        self.fc1 = nn.Linear(total_input_size, hidden_size)
        self.relu = nn.ReLU()
        self.fc2 = nn.Linear(hidden_size, hidden_size // 2)
        self.fc3 = nn.Linear(hidden_size // 2, output_size)

    def forward(self, x):
        x = self.flatten(x)
        x = self.relu(self.fc1(x))
        x = self.relu(self.fc2(x))
        x = self.fc3(x)
        return x

    
# Adjusted synthetic data generation to return data in shape (batch, channels, seq_length)
def generate_synthetic_data(seq_length, num_sequences, num_features):
    np.random.seed(42)  # For reproducibility
    time = np.arange(0, seq_length * num_sequences)
    data = []
    for i in range(num_features):
        data.append(np.sin(time * (i + 1) / 50.0) + np.random.normal(0, 0.5, size=(seq_length * num_sequences)))
    data = np.array(data).T  # Transpose to get the shape (num_sequences*seq_length, num_features)
    data = data.reshape(num_sequences, num_features, seq_length)  # Reshape for convolutional input
    return data

def create_sequences(data, seq_length):
    X, y = [], []
    for i in range(data.shape[0] - seq_length):
        X.append(data[i:i + seq_length, :, :])  # Adding all features
        y.append(data[i + seq_length, 0, -1])  # Selecting last element of the target sequence
    return np.array(X), np.array(y)


def parse_arguments():
    parser = argparse.ArgumentParser(description="RUDP Node Configuration")
    parser.add_argument('--local-port', type=int, required=True, help="Local port for the node")
    parser.add_argument('--parent-address', type=str, help="Parent node address in the format ip:port")
    parser.add_argument('--child-addresses', nargs='*', default=[], help="List of child node addresses in the format ip:port")
    parser.add_argument('--epochs', type=int, default=10, help="Number of training epochs")
    parser.add_argument('--save-path', type=str, default="model_weights.pth", help="Path to save the trained model")
    parser.add_argument('--batch-size', type=int, default=32, help="Batch size for training")
    args = parser.parse_args()
    return args

def download_stock_data(symbol, start_date, end_date):
    data = yf.download(symbol, start=start_date, end=end_date)
    return data['Close'].values.reshape(-1, 1)



#######################################

def normalize_rmse_percentage(rmse_percentage):
    # Normalize RMSE percentage to range [0, 100]
    normalized_rmse_percentage = (rmse_percentage - min_rmse_percentage) / (max_rmse_percentage - min_rmse_percentage) * 100
    return normalized_rmse_percentage

# Evaluate model function 수정 (MAE를 백분율로 변환)
def evaluate_model(node):
    node.model.eval()
    total_loss = 0
    total_samples = 0
    total_absolute_error = 0

    with torch.no_grad():
        for inputs, targets in node.validation_loader:
            inputs, targets = inputs.to(node.device), targets.to(node.device)
            outputs = node.model(inputs)
            loss = node.loss_function(outputs, targets)
            total_loss += loss.item() * targets.size(0)
            total_absolute_error += torch.abs(outputs - targets).sum().item()
            total_samples += targets.size(0)

    avg_loss = total_loss / total_samples
    mae = total_absolute_error / total_samples
    
    # MAE를 백분율로 변환하여 반환
    min_mae = 0  # 최소 MAE 값
    max_mae = 24  # 최대 MAE 값 (예시)
    normalized_mae = ((mae - min_mae) / (max_mae - min_mae)) * 100  # MAE를 0~100%로 정규화

    return {'evaluate_loss': avg_loss, 'mae_percentage': normalized_mae}




# 학습 중 출력되는 로스 계산도 이에 맞게 수정
def train(node):
    node.model.to(node.device)
    node.model.train()
    total_loss = 0
    total_samples = 0
    for inputs, targets in node.data_loader:
        inputs, targets = inputs.to(node.device), targets.to(node.device)
        node.optimizer.zero_grad()
        outputs = node.model(inputs)
        loss = node.loss_function(outputs, targets)
        loss.backward(retain_graph=node.retain_graph)
        node.optimizer.step()

        total_loss += loss.item() * targets.size(0)
        total_samples += targets.size(0)

    epoch_loss = total_loss / total_samples
    return {'train_loss': epoch_loss}




if __name__ == '__main__':
    args = parse_arguments()
    seq_length = 5
    num_features =3  # Ensure this matches how you're generating or preprocessing your data

    # Generate synthetic data
    synthetic_data = generate_synthetic_data(seq_length, 1000, num_features)
    X, y = create_sequences(synthetic_data, seq_length)

    # Print shapes to confirm
    print("Shape of X:", X.shape)
    print("Expected input shape to fc1:", num_features * seq_length)

    # Create datasets and data loaders
    dataset = TensorDataset(torch.from_numpy(X).float(), torch.from_numpy(y).float())
    train_size = int(0.8 * len(dataset))
    val_size = len(dataset) - train_size
    train_dataset, val_dataset = torch.utils.data.random_split(dataset, [train_size, val_size])
    train_dataloader = DataLoader(train_dataset, batch_size=args.batch_size, shuffle=True)
    val_dataloader = DataLoader(val_dataset, batch_size=args.batch_size, shuffle=False)

    # Instantiate and use the model
    model = SimpleTimeSeriesModel(seq_length=5, num_features=3, feature_length=5, hidden_size=100, output_size=1)
    optimizer = optim.Adam(model.parameters(), lr=0.01)
    loss_function = nn.MSELoss()
    scheduler = optim.lr_scheduler.StepLR(optimizer, step_size=5, gamma=0.1)


    # Node 초기화 및 시작
    node = Node(args.local_port, args.parent_address, args.child_addresses, model, train_dataloader, val_dataloader, loss_function, optimizer, args.epochs, args.save_path, retain_graph=True, evaluate_model_func=evaluate_model, train_func=train, batch_size=args.batch_size)
    node.start()

