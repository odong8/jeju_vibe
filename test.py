# 1. 홈 디렉토리로 이동 및 프로젝트 폴더 생성
cd ~
mkdir -p smart_sort/models
cd smart_sort/models

# 2. AI 모델 파일 다운로드
wget https://raw.githubusercontent.com/chuanqi305/MobileNet-SSD/master/deploy.prototxt
wget https://data.deepai.org/MobileNetSSD_deploy.caffemodel

# 3. 필수 패키지 및 라이브러리 설치
sudo apt update
sudo apt install -y python3-opencv python3-rpi.gpio python3-picamera2
pip3 install flask
