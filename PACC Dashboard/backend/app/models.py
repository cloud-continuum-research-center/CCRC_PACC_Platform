from .extensions import db
from datetime import datetime

class User(db.Model):
    user_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())

    def __repr__(self):
        return f'<User {self.email}>'

class Model(db.Model):
    model_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False, unique=True)
    description = db.Column(db.Text, nullable=True)
    

class Dataset(db.Model):
    dataset_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False, unique=True)
    description = db.Column(db.Text, nullable=True)


class Node(db.Model):
    node_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False,unique=True)
    cpu_core_count = db.Column(db.Integer, nullable=False)
    total_memory_mb = db.Column(db.Integer, nullable=False)  
    total_disk_mb = db.Column(db.Integer, nullable=False)  
    status = db.Column(db.Integer, nullable=False)  # 대기 : 0 , 학습 중 : 1, 학습 완료: 2/ 학습 중단 시 0으로 됨. 
    instance = db.Column(db.String(255), nullable=True)  # 인스턴스 해당 노드 ip 정보
    gpu_info = db.Column(db.String(255), nullable=True)  # GPU 정보 및 갯수

class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)
    model_id = db.Column(db.Integer, db.ForeignKey('model.model_id'), nullable=False)
    dataset_id = db.Column(db.Integer, db.ForeignKey('dataset.dataset_id'), nullable=False)
    status = db.Column(db.String(128), nullable=False)  # "학습 중", "중단 됨", "학습 완료"
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    project_nodes = db.Column(db.String, nullable=True)  # 노드 이름의 JSON 리스트를 저장하는 문자열 컬럼
    hyperparameters = db.Column(db.JSON, nullable=True)  # 하이퍼파라미터를 JSON 형식으로 저장
    result = db.Column(db.Text, nullable=True)