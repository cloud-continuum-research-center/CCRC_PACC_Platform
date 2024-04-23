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

# 1. prometheus 설치
if [ $PACKAGE_CODE -eq 1 ]; then
  sudo ufw allow 9090
  sudo ufw allow 9096
  sudo ufw allow 19000
  sudo ufw allow 19001
  sudo ufw allow 20000
  sudo ufw allow 20001
else
  sudo firewall-cmd --permanent --zone=public --remove-pore=9090/tcp
  sudo firewall-cmd --permanent --zone=public --remove-pore=9096/tcp
  sudo firewall-cmd --permanent --zone=public --remove-pore=19000/tcp
  sudo firewall-cmd --permanent --zone=public --remove-pore=19001/tcp
  sudo firewall-cmd --permanent --zone=public --remove-pore=20000/tcp
  sudo firewall-cmd --permanent --zone=public --remove-pore=20001/tcp
fi
docker volume create cluster
docker network create docker_cluster_network
docker run -d -v cluster:/etc/prometheus -p 9090:9090 --net docker_cluster_network --name node_prometheus prom/prometheus

# 2. /etc/prometheus/prometheus.yml 구성
# 구성 파일의 이름은 config여야 함
cat config > /var/lib/docker/volumes/cluster/_data/prometheus.yml
docker restart node_prometheus

sleep 2;

# 3. metric-server 설치 (localhost X)
HOST=$(curl icanhazip.com) # 현재 노드의 ip 가져와서 환경 변수에 저장
docker run -p 20000:20000 --name metric-server --net docker_cluster_network -dit jmc0504/metric-server:latest --prometheus-address=$HOST --prometheus-port=9090

# 4. thanos sidecar 설치 (노드 매트릭 수집용)
docker run -d -p 19000:19000 -p 19001:19001 --name node_metric_sidecar --net docker_cluster_network -u root quay.io/thanos/thanos:v0.34.0-rc.1 sidecar \
--http-address 0.0.0.0:19000 --grpc-address 0.0.0.0:19001 --prometheus.url "http://$HOST:9090"
