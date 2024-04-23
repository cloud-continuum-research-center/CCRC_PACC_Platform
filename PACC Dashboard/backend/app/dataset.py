from app.extensions import db
from app.models import Dataset

def add_dataset_data():
    # Define the model data to be added
    dataset_data = [
        {
            "name": "이미지 분류 데이터",
            "description": "이 데이터셋은 MNIST 데이터셋으로 0부터 9까지의 손글씨 데이터셋입니다. 각 이미지는 28x28 픽셀의 그레이스케일 이미지입니다."
        },
        {
            "name": "주가 예측 데이터",
            "description": "이 데이터셋은 파이썬 라이브러리인 pandas-datareader에서 제공해주는 주가 예측 데이터셋입니다." },
    ]

    # 각 데이터셋을 데이터베이스에 추가합니다.
    for dataset_info in dataset_data:
        dataset = Dataset(name=dataset_info["name"], description=dataset_info["description"])
        db.session.add(dataset)
    
    db.session.commit()  # 변경사항을 커밋합니다.

# 함수 호출로 데이터셋 데이터 추가 실행
add_dataset_data()