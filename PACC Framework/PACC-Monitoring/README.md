# BalanceOrchestrator (수정 중)

## 1. 개요
노드에서 수집된 메트릭 정보를 모니터링할 수 있다.
데이터 센터에 구축된 클러스터의 메트릭 정보를 모니터링 할 수 있다.
여러 데이터 센터에서 수집된 메트릭들을 모니터링 할 수 있다.

## 2. 사용 스택
### Exporter
노드에서 메트릭을 자동으로 수집하고 지정된 엔드포인트로 노출시키는 역할을 담당
1. Node-Exporter
2. DCGM Exporter

### Prometheus
Exporter를 통해 수집된 데이터들을 저장하는 시계열 데이터베이스

### Thanos sidecar
프로메테우스와 연결되어 프로메테우스에 저장된 데이터들을 Thanos querier에 전달

### Thanos Querier
복수의 프로메테우스에서 수집된 데이터들을 하나의 Thanos Querier를 통해 통합

### Metric Server
노드에서 수집된 데이터들을 클러스터 단위로 전환 후 지정된 엔드포인트로 노출시키는 역할을 담당

Git : https://github.com/JeonMinCheol/Metrics
Docker Image : jmc0504/metric-server

## 3. 설치 요약
1. setup.sh는 모든 노드에 공통으로 설치되야 하는 패키지를 설치하는 스크립트
2. 클러스터마다 하나의 마스터 노드를 선택하여 cluster/cluster-setup.sh 을 실행시킨다. (실행 전 config 파일 수정)
3. 데이터 센터에서 하나의 마스터 노드를 선택하여 datacenter/data_center_setup.sh 파일을 실행시킨다. (실행 전 config 파일 수정)

## 4. 주의 사항
1. GPU vendor는 nvidia만 지원
2. 드라이버가 사전에 설치되어있어야 함
3. 드라이버를 설치하기 위해선 ubuntu-gpu-driver-install.sh를 실행
