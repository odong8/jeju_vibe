# day3-cv2-camera-save.py
# 카메라 영상을 동영상 파일로 저장하기 (Picamera2 + OpenCV VideoWriter)
#   ESC 키를 누르면 녹화를 끝낸다.

import os
os.environ.setdefault("QT_QPA_PLATFORM", "xcb")

import cv2
import time
from picamera2 import Picamera2

# 카메라 프레임 크기 지정하기
width, height = 640, 480
fps = 30

# 카메라 열기
picam2 = Picamera2()
config = picam2.create_video_configuration(
    main={"size": (width, height), "format": "RGB888"}
)
picam2.configure(config)
picam2.start()
time.sleep(1)   # 카메라 밝기가 안정될 때까지 잠시 대기

# 저장 파일명 지정 (avi 또는 mp4 가능)
file = 'output.mp4'  # 'output.avi'로 바꾸면 avi로 저장됨

# 확장자에 맞는 fourcc 선택
ext = os.path.splitext(file)[1].lower()
if ext == '.avi':
    fourcc = cv2.VideoWriter_fourcc(*'DIVX')
elif ext == '.mp4':
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # 또는 'avc1'
else:
    raise ValueError("지원하지 않는 확장자입니다. .avi 또는 .mp4만 사용하세요.")

# VideoWriter 객체 생성
out = cv2.VideoWriter(file, fourcc, fps, (width, height))

try:
    while True:  # 카메라 프레임 처리
        frame = picam2.capture_array()
        if frame is None:
            print('Can not read frame!')
            break

        frame = cv2.flip(frame, 1)  # 좌우 반전

        text = 'Camera recording...'
        font = cv2.FONT_HERSHEY_DUPLEX
        cv2.putText(frame, text, (10, 40), font, 1, (0, 0, 255), 1)

        out.write(frame)
        cv2.imshow('frame', frame)

        if cv2.waitKey(10) == 27:  # ESC 키
            break

finally:
    out.release()          # 동영상 파일 마무리 (이걸 빼면 파일이 깨진다)
    picam2.stop()
    picam2.close()
    cv2.destroyAllWindows()
    print(f'{file} 저장됨')
