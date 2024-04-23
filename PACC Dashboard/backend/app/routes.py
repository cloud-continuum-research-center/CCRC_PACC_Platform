from flask import Blueprint, request, jsonify, current_app
from werkzeug.security import generate_password_hash, check_password_hash
from app.models import db, User, Model, Dataset, Project, Node
from flask_jwt_extended import create_access_token , get_jwt_identity, jwt_required
import requests
import json
from sqlalchemy.exc import SQLAlchemyError
from datetime import timedelta

main = Blueprint('main', __name__)

@main.route('/api/signup', methods=['POST'])
def signup():
    data = request.json
    name = data.get('name') 
    email = data.get('email')
    password = data.get('password')
    
    # 이미 등록된 이메일인지 확인
    user = User.query.filter_by(email=email).first()
    if user:
        return jsonify({'message': '기존의 존재하는 이메일입니다.'}), 409
    
    # 새로운 사용자 생성
    new_user = User(name=name, email=email, password_hash=generate_password_hash(password))
    db.session.add(new_user)
    db.session.commit()

    return jsonify({'message': 'User created successfully.'}), 201

@main.route('/api/signin', methods=['POST'])
def signin():
    data = request.json
    email = data.get('email')
    password = data.get('password')
    
    # 사용자 조회
    user = User.query.filter_by(email=email).first()
    
    # 사용자가 존재하고 비밀번호가 맞는 경우
    if user and check_password_hash(user.password_hash, password):
        # 토큰 생성
        expires = timedelta(hours=3)  # 만료 시간 설정 3시간 
        access_token = create_access_token(identity=email, expires_delta=expires)
        return jsonify(access_token=access_token, email=email), 200
    else:
        # 실패한 경우
        return jsonify({'message': 'Invalid credentials.'}), 401

     

@main.route('/api/create-project', methods=['POST'])
@jwt_required()
def submit_training():                                           # 프론트에서 모델 학습 요청 받아서 지승이 백엔드로 전송
    current_user_email = get_jwt_identity()
    current_user = User.query.filter_by(email=current_user_email).first()
    
    current_app.logger.info(f"유저 ID: {current_user}")
    
    if not current_user:
        return jsonify({"message": "사용자를 찾을 수 없습니다."}), 404
    
    data = request.json
    print("프론트엔드에서 받은 프로젝트 데이터:", data)
    
    model = Model.query.get(data['model'])
    dataset = Dataset.query.get(data['dataset'])
    
    current_app.logger.info(f"Model: {model}, Dataset: {dataset}")
    
    if not model or not dataset:
        return jsonify({"message": "모델 또는 데이터셋을 찾을 수 없습니다."}), 404

    try:
        new_project = Project(
            user_id=current_user.user_id,
            model_id=model.model_id,
            dataset_id=dataset.dataset_id,
            status="생성 요청",
            hyperparameters=data['hyperparameters']  # 하이퍼파라미터 추가
        )
        db.session.add(new_project)
        db.session.commit()
        
        current_app.logger.info(f"프로젝트 생성 성공: Project ID {new_project.id}")
        
        node_instances = []
        for node_name in data['nodes']:
            node = Node.query.filter_by(name=node_name).first()
            if node:
                ip_address = node.instance.split(':')[0]  # 콜론을 기준으로 분리하고 첫 번째 부분(IP 주소)만 사용
                node_instances.append(ip_address)
            else:
                node_instances.append("Unknown")  # 노드가 찾아지지 않을 경우
                
        # 노드 모니터링 데이터 가져오기
        monitoring_response = requests.get('http://13.124.158.135:20001/api/v1/metrics')
        monitoring_response.raise_for_status()
        monitoring_data = monitoring_response.json()

        node_statuses = []
        for node_name, node_info in monitoring_data.items():
            metrics = node_info['metrics']
            node_statuses.append(metrics)  # metrics 배열을 그대로 사용
            
        # 전송할 데이터 구성
        modified_data = {
            "id": new_project.id,
            "model":model.model_id,  # 여기는 정수형 ID
            "dataset": dataset.dataset_id,  # 여기는 정수형 ID
            "hyperparameters": data['hyperparameters'],
            "nodes": node_instances,  # 노드 인스턴스 정보
            "status": node_statuses
        }
        print(modified_data)
        current_app.logger.info(f"수정된 파일: {modified_data}")

        other_backend_url = "http://ec2-3-36-137-217.ap-northeast-2.compute.amazonaws.com:12345/training"
        response = requests.post(other_backend_url, json=modified_data)

        if response.status_code == 200:
            new_project.status = "학습 중"
            new_project.project_nodes = json.dumps(data['nodes'])  # 'nodes'는 노드 이름의 리스트를 JSON 문자열로 저장
            db.session.commit()
            node_names = data['nodes']  # Assuming this is a list of node names
            for node_name in node_names:
                node = Node.query.filter_by(name=node_name).first()
                if node:
                    node.status = 1  # Set status to Learning (1)
                    db.session.add(node)
            db.session.commit()
            return jsonify({"message": "다른 백엔드로 프로젝트 정보가 성공적으로 전송되었습니다.", "project_id": new_project.id}), 200
        else:
            return jsonify({"message": "다른 백엔드로 프로젝트 정보 전송에 실패하였습니다."}), response.status_code
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error during project creation: {e}")
        return jsonify({"message": "프로젝트 생성 중 오류가 발생했습니다."}), 500
    

@main.route('/api/data/models', methods=['GET'])
def get_models():
    # 데이터베이스에서 모든 모델 정보를 조회
    models = Model.query.all()
    # 조회한 모델 정보를 JSON 형식으로 변환
    models_data = [{
        'model_id': model.model_id,
        'name': model.name,
        'description': model.description
    } for model in models]
    # JSON 데이터로 응답
    return jsonify(models_data)

@main.route('/api/data/datasets', methods=['GET'])
def get_datasets():
    # 데이터베이스에서 모든 데이터셋 정보를 조회
    datasets = Dataset.query.all()
    # 조회한 데이터셋 정보를 JSON 형식으로 변환
    datasets_data = [{
        'dataset_id': dataset.dataset_id,
        'name': dataset.name,
        'description': dataset.description,
    } for dataset in datasets]
    # JSON 데이터로 응답
    return jsonify(datasets_data)

@main.route('/api/data/nodes', methods=['GET'])
def get_nodes():
    nodes = Node.query.all()  # 모든 Node 인스턴스를 데이터베이스에서 조회
    nodes_data = [{
        'node_id': node.node_id,
        'name': node.name,
        'cpu_core_count': node.cpu_core_count,
        'total_memory_mb': node.total_memory_mb,  # 단위에 주의하세요
        'total_disk_mb': node.total_disk_mb,  # 단위에 주의하세요
        'status': node.status,
        'ip': node.instance,
        'gpu_info': node.gpu_info 
    } for node in nodes]  # 조회된 Node 인스턴스들을 JSON 형식으로 변환

    return jsonify(nodes_data)  # JSON 데이터로 응답

@main.route('/api/reset-db', methods=['POST'])
def reset_database():
    try:
        # 모든 프로젝트 데이터를 삭제합니다.
        num_rows_deleted = db.session.query(Project).delete()
        db.session.commit()
        
        # 성공 메시지와 함께 삭제된 행의 수를 반환합니다.
        return jsonify({"message": "Database reset successfully.", "rows_deleted": num_rows_deleted}), 200
    except Exception as e:
        # 에러 발생 시 롤백합니다.
        db.session.rollback()
        return jsonify({"error": str(e)}), 500
    
@main.route('/api/data/projects', methods=['POST']) # 대시보드 페이지에서 학습 정보 띄울 때 가져가는 코드 
@jwt_required()
def fetch_projects():
    # 현재 로그인한 사용자의 이메일을 JWT 토큰에서 가져옵니다.
    current_user_email = get_jwt_identity()
    request_data = request.json
    email_from_request = request_data.get('email')

    # JWT 토큰에서 추출한 이메일과 요청에서 받은 이메일이 일치하는지 확인합니다.
    if current_user_email != email_from_request:
        return jsonify({"error": "Unauthorized access"}), 401

    # User 테이블에서 사용자의 이메일을 사용하여 사용자 정보를 조회합니다.
    user = User.query.filter_by(email=current_user_email).first()

    if user is None:
        return jsonify({"error": "User not found"}), 404

    # Project 테이블에서 해당 사용자의 모든 프로젝트를 조회합니다.
    projects = Project.query.filter_by(user_id=user.user_id).all()
    projects_data = []

    for project in projects:
        model = Model.query.get(project.model_id)
        dataset = Dataset.query.get(project.dataset_id)

        projects_data.append({
            "id": project.id,
            "model_name": model.name if model else "Model not found",
            "dataset_name": dataset.name if dataset else "Dataset not found",
            "status": project.status,
            "created_at": project.created_at.strftime("%Y-%m-%d %H:%M:%S") if project.created_at else "N/A",
            "result": project.result,
            "project_nodes": project.project_nodes if project.project_nodes else "No nodes assigned"  # 이제 project_nodes 정보도 포함시킵니다.
        })
    print(projects_data)
    return jsonify(projects_data)

@main.route('/api/stop-training', methods=['POST'])
@jwt_required()
def stop_training():
    current_user_email = get_jwt_identity()
    data = request.json
    project_id = data.get('projectId')

    # 프로젝트 조회
    project = Project.query.filter_by(id=project_id).first()
    if not project:
        return jsonify({"error": "Project not found"}), 404

    # 다른 백엔드로 학습 중단 요청 보내기
    try:
        response = requests.delete(f'http://ec2-3-36-137-217.ap-northeast-2.compute.amazonaws.com:12345/training/{project_id}')
        response_data = response.json()

        # Check the 'success' field in the response data
        if response.status_code == 200 and response_data.get('success'):
            # 프로젝트 상태 업데이트
            project.status = '중단됨'
            # 프로젝트에 연결된 노드들의 상태를 대기(0)로 변경
            node_names = json.loads(project.project_nodes)
            current_app.logger.info(f"Processing stop training for nodes: {node_names}")
            for node_name in node_names:
                node = Node.query.filter_by(name=node_name).first()
                if node:
                    node.status = 0  # 대기 상태로 설정
                    current_app.logger.info(f"Node {node_name} status updated to waiting")
                else:
                    current_app.logger.warning(f"No node found with the name {node_name}")    
            db.session.commit()
            return jsonify({"success": True, "message": "Training stopped successfully"}), 200
        else:
            error_message = response_data.get('message', 'Unknown error')
            return jsonify({"error": error_message}), response.status_code

    except Exception as e:
        current_app.logger.error(f"Error during stopping training: {e}")
        return jsonify({"error": str(e)}), 500
    

@main.route('/api/data/nodemonitoring', methods=['GET'])            # 현재 노드 이름이 {클러스트} + {노드 이름} 상태로 날라와서 그에 맞춰서 코드 작성됨, 추후 민철이가 보내는 형식 수정하면 다시 재 수정 필요함.
def process_node_monitoring_data():
    try:
        # 다른 백엔드에서 데이터를 가져옵니다.
        response = requests.get('http://13.124.158.135:20001/api/v1/metrics')
        response.raise_for_status()  # 상태 코드가 200이 아니면 HTTPError 예외를 발생시킵니다.
        data = response.json()

        # 가공할 데이터를 준비합니다.
        processed_data = {}

        for node_name, node_info in data.items():
            # 필요한 메트릭을 추출합니다.
            metrics = node_info['metrics']
            realTime = {
                "memoryFree": int(float(metrics[3]) / (1024 ** 2)),  # 메모리 사용 가능량 (MB 단위로 변환)
                "diskFree": int(float(metrics[4]) / (1024 ** 2))    # 디스크 사용 가능량 (MB 단위로 변환)
            }
            historical = {
                "cpuUtilization": float(metrics[1]),  # CPU 사용률
                "gpuUtilization": metrics[7] if metrics[7] is not None else 0,  # GPU 사용률 (없으면 0)
                "gpuTemperature": metrics[5] if metrics[5] is not None else 0,  # GPU 온도 (없으면 0)
                "gpuPowerUsage": metrics[6] if metrics[6] is not None else 0,   # GPU 전력 사용량 (없으면 0)
            }
            
            # 가공된 데이터를 저장합니다.
            processed_data[node_name] = {
                "realTime": realTime,
                "historical": historical
            }
        # 가공된 데이터를 반환합니다.
        return jsonify(processed_data)

    except requests.HTTPError as http_err:
        # 외부 요청 중 발생한 HTTP 에러를 처리합니다.
        return jsonify({"error": "External backend error", "details": str(http_err)}), 500
    except Exception as err:
        # 기타 예외 처리
        return jsonify({"error": "An error occurred", "details": str(err)}), 500
    
@main.route('/api/projects/<int:project_id>', methods=['GET'])         # 학습 중인 프로젝트 상태 정보 요청 후 프런트로 반환 
@jwt_required()
def get_project_info(project_id):
    try:
        url = f"http://ec2-3-36-137-217.ap-northeast-2.compute.amazonaws.com:12345/status/{project_id}"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            print(data)
            
            # Remove 불필요 정보 data fields
            data.pop('success', None)
            data.pop('id', None)
            data.pop('code', None)

            # Check if the training has completed using 'current_state'
            if data.get('current_state') == 2:  # Check for state indicating training completion
                project = Project.query.filter_by(id=project_id).first()
                if project:
                    project.status = "학습 완료"
                    db.session.commit()

                    # Update statuses of associated nodes
                    node_names = json.loads(project.project_nodes)
                    for node_name in node_names:
                        node = Node.query.filter_by(name=node_name).first()
                        if node:
                            node.status = 0
                    db.session.commit()

            print(data)
            return jsonify(data), 200
        else:
            return jsonify({"error": "Failed to retrieve project data from external backend"}), response.status_code

    except requests.exceptions.RequestException as e:
        current_app.logger.error(f"Error fetching project {project_id} from external backend: {str(e)}")
        return jsonify({"error": "An error occurred while fetching project data"}), 500