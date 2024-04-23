import requests
from app import db
from app.models import Node

def fetch_and_store_node_data():
    try:
        # 다른 백엔드에서 노드 데이터를 가져옵니다.
        response = requests.get('http://13.124.158.135:20001/api/v1/metrics')
        node_data_dict = response.json()

        for node_name, node_info in node_data_dict.items():
            # 기존에 존재하는 노드인지 확인합니다.
            existing_node = Node.query.filter_by(name=node_name).first()
            if existing_node:
                # 노드가 이미 존재하면 상태 및 기타 메트릭스를 업데이트합니다.
                existing_node.status = 0  # '대기' 상태로 설정
                existing_node.cpu_core_count = int(node_info['metrics'][0])
                existing_node.total_memory_mb = int(float(node_info['metrics'][9]) / (1024**2))
                existing_node.total_disk_mb = int(float(node_info['metrics'][10]) / (1024**2))
                existing_node.instance = node_info['instance'][0]
                existing_node.gpu_info = node_info['metrics'][11] if node_info['metrics'][11] else "None"
            else:
                # 존재하지 않는 노드라면 새로 추가합니다.
                metrics = node_info['metrics']
                new_node = Node(
                    name=node_name,
                    cpu_core_count=int(metrics[0]),
                    total_memory_mb=int(float(metrics[9]) / (1024**2)),
                    total_disk_mb=int(float(metrics[10]) / (1024**2)),
                    status=0,  # 대기: 0, 학습 중: 1, 학습 완료: 2
                    instance=node_info['instance'][0],
                    gpu_info=metrics[11] if metrics[11] else "None"
                )
                db.session.add(new_node)
        
        # 데이터베이스 변경사항을 커밋합니다.
        db.session.commit()
    except Exception as e:
        # 오류 발생 시 콘솔에 출력
        print(f"노드 데이터 가져오기 또는 저장 중 오류 발생: {e}")
