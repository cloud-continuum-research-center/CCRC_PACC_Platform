from app.extensions import db
from app.models import Model

def delete_model_data():
    # 모든 모델 데이터를 조회합니다.
    models = Model.query.all()
    for model in models:
        db.session.delete(model)  # 각 모델 데이터를 삭제합니다.
    
    db.session.commit()  # 변경사항을 커밋합니다.

# 함수 호출로 데이터 삭제 실행
delete_model_data()