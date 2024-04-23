from app.extensions import db
from app.models import Model

def add_model_data():
    # 모델 데이터 정의
    models_to_add = [
        {
            "name": "Convolutional Neural Network (CNN)",
            "description": "CNN은 데이터의 로컬 특징에 필터를 적용하는 컨볼루션 레이어를 사용하여 이미지 및 비디오 인식, 이미지 분류, 의료 이미지 분석과 같은 작업에서 효과적인 특징 추출 및 인식을 가능하게 합니다."
        },
        {
            "name": "DeeP Neural Network (DNN)",
            "description": "심층 신경망은 입력층과 출력층 사이에 여러 개의 은닉층들로 이뤄진 인공신경망입니다. 이 모델은 DNN 기반 연속적인 시계열 데이터처리 신경망 모델입니다."
        }
    ]
    # 데이터베이스에 각 모델 추가
    for model_data in models_to_add:
        model = Model(name=model_data["name"], description=model_data["description"])
        db.session.add(model)
    
    # 변경사항을 데이터베이스에 커밋
    db.session.commit()

# 함수 호출하여 데이터 추가
add_model_data()