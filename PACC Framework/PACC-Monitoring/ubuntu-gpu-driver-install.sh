# gcc check
gcc --version

# gcc install
sudo apt-get update
sudo apt install gcc -y

# Linux Kernel Header를 설치
sudo apt-get install linux-headers-$(uname -r)

# ubuntu-driver 패키지를 설치
sudo apt install ubuntu-drivers-common -y

# 설치할 Driver 버전을 위한 Repository를 추가
distribution=$(. /etc/os-release;echo $ID$VERSION_ID | sed -e 's/\.//g')

# DIVER 설치
sudo apt-get update
ubuntu-drivers autoinstall

# 재시작
sudo reboot
