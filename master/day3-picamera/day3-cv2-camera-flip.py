# day3-cv2-camera-flip.py
# 스페이스바를 누를 때마다 영상 반전 방향 바꾸기 (Picamera2 + OpenCV)
#   ESC   : 종료
#   Space : 원본 -> 좌우 -> 상하 -> 좌우+상하 -> 원본 ...

import os
os.environ.setdefault("QT_QPA_PLATFORM", "xcb")

import sys
import cv2
from picamera2 import Picamera2

width, height = 640, 480

# 카메라 열기
picam2 = Picamera2()
config = picam2.create_video_configuration(
    main={"size": (width, height), "format": "RGB888"}   # RGB888 -> OpenCV 의 BGR 순서
)
picam2.configure(config)
picam2.start()

# 카메라 프레임 크기 출력
print('Frame width:', width)
print('Frame height:', height)

# 영상 반전을 위한 변수
flip_flag = 9   # 영상 반전 상태
flip_dict = {9: 1, 1: 0, 0: -1, -1: 9}  # 현재상태:다음상태 지정

# 카메라 프레임 처리
try:
    while True:
        frame = picam2.capture_array()
        if frame is None: break

        if flip_flag == 9:
            text = 'Original'
        else:
            text = f'Camera flip={flip_flag}'
            frame = cv2.flip(frame, flip_flag)  # 이미지 반전  1:좌우, 0:상하, -1:좌우+상하

        font = cv2.FONT_HERSHEY_DUPLEX
        cv2.putText(frame, text, (10, 30), font, 1, (0, 0, 255), 1)
        cv2.imshow('flip-frame', frame)

        key = cv2.waitKey(10)
        if key == 27:            # ESC
            break
        elif key == ord(' '):    # Space
            flip_flag = flip_dict[flip_flag]

finally:
    picam2.stop()
    picam2.close()
    cv2.destroyAllWindows()
