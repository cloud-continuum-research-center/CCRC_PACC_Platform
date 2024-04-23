#!/bin/bash

# 지원 OS : Ubuntu, Centos7, Amazon Linux

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


# 1. Install Docker

# Check Docker installation status
if [ "$(docker -v)" ]; then
	echo "Docker already installed."

# Ubuntu
elif [ $PACKAGE_CODE -eq 1 ]; then
	sudo apt-get update;
	sudo apt-get install apt-transport-https ca-certificates curl gnupg-agent software-properties-common dpkg -y;
	curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -;
	sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" -y;
	sudo apt-get update -y -q;
	sudo apt-get install docker-ce docker-ce-cli containerd.io -y -q;
	sudo docker run hello-world;

	sudo chmod 666 /var/run/docker.sock;
	
	echo "Docker Install Complete.";
	
# Other OS
elif [ $PACKAGE_CODE -eq 2 ]; then
	sudo yum update -y; 
	sudo yum install -y yum-utils;
	sudo yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo;
 	sudo yum install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin;
	sudo yum install docker -y;
	sudo systemctl start docker;
	sudo systemctl enable docker;

	sudo chmod 666 /var/run/docker.sock;
	
	echo "Docker Install Complete."
fi

sleep 2;

# 2. Install DCGM Exporter

# Notice 1 : Port 9400 required
# Notice 2 : GPU Driver must already be installed.
# Notice 3 : Nvidia Only!

# Check GPU
if [ -n 'lspci | grep NVIDIA' ]; then
	if [ $PACKAGE_CODE -eq 1 ]; then
		sudo apt-get install golang -y
		sudo apt-get install git -y
	
		# wget https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2004/x86_64/cuda-keyring_1.1-1_all.deb;
		# sudo dpkg -i cuda-keyring_1.1-1_all.deb;
		sudo add-apt-repository -y "deb https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2004/x86_64/ /";
	
		sudo apt-get update -y -q && sudo apt-get install -y -q datacenter-gpu-manager;
	
	elif [ $PACKAGE_CODE -eq 2 ]; then
		sudo yum install golang -y
		sudo yum install git -y

  		# sudo rpm --erase gpg-pubkey-7fa2af80*;
    		# distribution=$(. /etc/os-release;echo $ID`rpm -E "%{?rhel}%{?fedora}"`)
      		sudo dnf config-manager --add-repo http://developer.download.nvidia.com/compute/cuda/repos/$distribution/x86_64/cuda-rhel8.repo
	
		sudo dnf clean expire-cache && sudo dnf install -y datacenter-gpu-manager;
	fi
	sleep 1;
	  
	sudo systemctl --now enable nvidia-dcgm;
	sudo systemctl start nvidia-dcgm;
	
	sleep 2;
	
	sudo update-pciids

	if [ "$(cat /proc/driver/nidia/version 2>&1)" == "cat: /proc/driver/nidia/version: No such file or directory" ]; then
		# Install required packages
		if [ $PACKAGE_CODE -eq 1 ]; then
	
			if [ -z "$(sudo apt list --installed | grep nvidia-container-toolkit)" ]; then 
				distribution=$(. /etc/os-release;echo $ID$VERSION_ID) \
      				&& curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey | sudo gpg --dearmor -o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg \
			      	&& curl -s -L https://nvidia.github.io/libnvidia-container/$distribution/libnvidia-container.list | \
			        sed 's#deb https://#deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg] https://#g' | \
			        sudo tee /etc/apt/sources.list.d/nvidia-container-toolkit.list
				sudo apt-get update -y -q;
				sudo apt-get install -y -q nvidia-container-toolkit;
    				sudo nvidia-ctk runtime configure --runtime=docker;
			fi
			
		elif [ $PACKAGE_CODE -eq 2 ]; then
	
			# Install required packages
			if [ -z "$(sudo yum list installed | grep nvidia-container-toolkit)" ]; then
				curl -s -L https://nvidia.github.io/libnvidia-container/stable/rpm/nvidia-container-toolkit.repo | \
				sudo tee /etc/yum.repos.d/nvidia-container-toolkit.repo;
				sudo yum-config-manager --enable nvidia-container-toolkit-experimental;
				sudo yum install -y nvidia-container-toolkit;
			fi
		fi
	
	 	sudo systemctl restart docker;
	
	else
		cat /proc/driver/nidia/version;
		echo "GPU Driver already installed.";
	fi

	sleep 10;
 
	# Install DCGM Exporter (GPU driver needed.)
	docker run -d --gpus all --rm --name DCGM-Exporter -p 9400:9400 nvcr.io/nvidia/k8s/dcgm-exporter:3.3.3-3.3.1-ubuntu22.04 

	sudo ufw allow 9400;
 	echo "Install DCGM-Exporter";
  
	sleep 2;
fi

# 3. Install Node Exporter

# Notice : Port 9100 required

docker run -d --name node-exporter -p 9100:9100 prom/node-exporter
sudo ufw allow 9100
