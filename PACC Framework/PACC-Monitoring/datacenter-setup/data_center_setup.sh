#!/bin/bash

# 클러스터 내부 노드들의 메트릭을 수집하여 클러스터에 대한 메트릭으로 변환한 뒤 해당 메트릭을 노출하는 구성을 자동 설치하는 스크립트 파일

# 해당 스크립트를 사용하기 위해선 클러스터에 위치한 노드들의 ip가 필요
# 이를 위한 구성은 json 파일로 미리 작성되어 있어야 함

OS_INFO=$(sudo cat /etc/*release* | grep -E '^NAME=')
OS_INFO_LENGTH=${#OS_INFO}
OS_NAME=$(echo $OS_INFO | cut -c 7-$(expr $OS_INFO_LENGTH - 1))
PACKAGE_CODE=-1

# Set Package Managing Code
if [ "$OS_NAME" == "Ubuntu" ]; then 
	PACKAGE_CODE=1

elif [[ "$OS_NAME" == "CentOS Linux" || "$OS_NAME" == "Amazon Linux" ]]; then 
	PACKAGE_CODE=2
fi

# 1. 방화벽 설정
if [ $PACKAGE_CODE -eq 1 ]; then
  sudo ufw allow 9091
  sudo ufw allow 9092
  sudo ufw allow 9093
else
  sudo firewall-cmd --permanent --zone=public --remove-pore=9091/tcp
  sudo firewall-cmd --permanent --zone=public --remove-pore=9092/tcp
  sudo firewall-cmd --permanent --zone=public --remove-pore=9093/tcp
fi

# 2. prometheus 설치
docker network create --driver bridge docker_data_center_network

docker volume create data_center
docker run -d -v data_center:/etc/prometheus -p 9091:9090 --name data_center_prometheus --net docker_data_center_network prom/prometheus

# 3. /etc/prometheus/prometheus.yml 구성
# 구성 파일의 이름은 config여야 함 (메트릭 서버 ip:port 입력)
cat config > /var/lib/docker/volumes/data_center/_data/prometheus.yml
docker restart data_center_prometheus

sleep 2;

# 4. thanos sidecar 설치
HOST=$(curl icanhazip.com) # 현재 노드의 ip 가져와서 환경 변수에 저장
docker run -d -p 9092:9092 -p 9093:9093 --name datacenter_sidecar --net docker_data_center_network -u root quay.io/thanos/thanos:v0.34.0-rc.1 sidecar \
--http-address 0.0.0.0:9092 --grpc-address 0.0.0.0:9093 --prometheus.url "http://$HOST:9091"
