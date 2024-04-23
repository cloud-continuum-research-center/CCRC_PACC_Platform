import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
import torch
import torch.nn as nn
import torch.optim as optim

# 예제 데이터 생성
np.random.seed(0)
days = np.arange(1, 101)  # 100일간의 데이터
prices = 50 + 2 * days + np.random.normal(0, 10, 100)  # 예측할 주식 가격, 간단한 선형 관계로 생성
data = pd.DataFrame({'Days': days, 'Price': prices})

# 데이터 확인
print(data.head())

# 학습 데이터와 검증 데이터, 테스트 데이터 분할
X = data[['Days']]
y = data['Price']
X_train, X_temp, y_train, y_temp = train_test_split(X, y, test_size=0.3, random_state=42)
X_val, X_test, y_val, y_test = train_test_split(X_temp, y_temp, test_size=0.5, random_state=42)

# PyTorch를 이용한 모델 학습 및 검증
X_train_tensor = torch.tensor(X_train.values, dtype=torch.float32)
y_train_tensor = torch.tensor(y_train.values, dtype=torch.float32).reshape(-1, 1)

X_val_tensor = torch.tensor(X_val.values, dtype=torch.float32)
y_val_tensor = torch.tensor(y_val.values, dtype=torch.float32).reshape(-1, 1)

model = nn.Linear(1, 1)
criterion = nn.MSELoss()
optimizer = optim.SGD(model.parameters(), lr=0.0001)  # 학습률을 낮춤

for epoch in range(10):
    # 학습 단계
    model.train()
    optimizer.zero_grad()
    outputs = model(X_train_tensor)
    train_loss = criterion(outputs, y_train_tensor)
    train_loss.backward()
    optimizer.step()
    
    # 검증 단계
    model.eval()
    with torch.no_grad():
        val_outputs = model(X_val_tensor)
        val_loss = criterion(val_outputs, y_val_tensor)

    print(f'Epoch {epoch+1}, Train Loss: {train_loss.item()}, Validation Loss: {val_loss.item()}')

# 테스트 데이터로 모델 평가
X_test_tensor = torch.tensor(X_test.values, dtype=torch.float32)
y_test_tensor = torch.tensor(y_test.values, dtype=torch.float32).reshape(-1, 1)

model.eval()
with torch.no_grad():
    test_outputs = model(X_test_tensor)
    test_loss = criterion(test_outputs, y_test_tensor)
print("Test Loss:", test_loss.item())

# 테스트 손실을 백분율로 변환하여 출력
min_loss = min(train_loss.item(), val_loss.item(), test_loss.item())
max_loss = max(train_loss.item(), val_loss.item(), test_loss.item())
test_loss_percent = (test_loss.item() - min_loss) / (max_loss - min_loss) * 100
print("Test Loss (Percent):", test_loss_percent)
