# day3-cv2-camera-mission-photo.py
# [미션] 화면의 흰색 사각형 영역만 잘라서 사진으로 저장하기 (Picamera2 + OpenCV)
#   Enter : 사진 저장
#   ESC   : 종료

import os
os.environ.setdefault("QT_QPA_PLATFORM", "xcb")

import cv2
from picamera2 import Picamera2

# 카메라 프레임 크기 (아래 사각형 좌표에 맞춰 640x480 으로 고정)
width, height = 640, 480

# 카메라 열기
picam2 = Picamera2()
config = picam2.create_video_configuration(
    main={"size": (width, height), "format": "RGB888"}
)
picam2.configure(config)
picam2.start()

file = 'myPhoto.jpg'
top, bottom, right, left = 50, 50, 50, 50

try:
    while True:
        frame = picam2.capture_array()
        if frame is None: break

        frame = cv2.flip(frame, 0)     # 이미지 반전  1:좌우, 0:상하

        # 1.화면에 흰색 사각형 그리기 ---------------
        font = cv2.FONT_HERSHEY_DUPLEX
        text1 = "*Press 'Enter' key!!!"
        text2 = "*File: myPhoto.jpg"
        cv2.putText(frame, text1, (left, top), font, 1, (0, 0, 255), 1)
        cv2.putText(frame, text2, (50, 450), font, 0.5, (255, 255, 255), 1)
        cv2.rectangle(frame, (180, 90), (500, 400), (255, 255, 255), 3)

        cv2.imshow("Frame", frame)

        key = cv2.waitKey(10)
        if key == 27:      # ESC키: 종료
            break

        # 2.엔터키를 누르면 박스 영역 이미지 파일로 저장하기 ---------------
        elif key == 13:    # 엔터키: 화면 저장
            img_frame = frame.copy()
            # 위 흰색 영역만큼 사이즈 잘라 저장하기 img_frame[start_y:end_y, s_x:e_x]
            img_size = img_frame[90:400, 180:500]
            cv2.imwrite(file, img_size)
            print(file, ' 저장됨')

finally:
    picam2.stop()
    picam2.close()
    cv2.destroyAllWindows()
