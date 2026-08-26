# day3-cv2-camera.py
# 라즈베리파이 카메라 영상 화면에 보여주기 (Picamera2 + OpenCV)
#
# Trixie 부터는 레거시 카메라 스택(cv2.VideoCapture(0))이 동작하지 않으므로
# Picamera2 로 프레임을 받아서 OpenCV 로 처리한다.
#   sudo apt install python3-picamera2
#   카메라 확인: rpicam-hello --list-cameras

import os
# Wayland 환경에서 cv2.imshow 창이 뜨도록 (반드시 cv2 import 전에 설정)
os.environ.setdefault("QT_QPA_PLATFORM", "xcb")

import sys
import cv2
from picamera2 import Picamera2

# 카메라 프레임 크기
width, height = 640, 480

# 카메라 열기
picam2 = Picamera2()

# format="RGB888" 로 지정하면 numpy 배열이 OpenCV 와 같은 BGR 순서로 나온다.
config = picam2.create_video_configuration(
    main={"size": (width, height), "format": "RGB888"}
)
picam2.configure(config)
picam2.start()

# 카메라 프레임 크기 출력
print('Frame width:', width)
print('Frame height:', height)

# 카메라 프레임 처리
try:
    while True:
        frame = picam2.capture_array()
        if frame is None:
            print('Can not read frame!')
            break

        # frame = cv2.flip(frame, 0)  # 이미지 반전  1:좌우, 0:상하, -1:좌우+상하
        cv2.imshow('frame', frame)

        if cv2.waitKey(10) == 27: break   # ESC 키

finally:
    picam2.stop()
    picam2.close()
    cv2.destroyAllWindows()
