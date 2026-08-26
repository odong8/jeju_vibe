# day3-cv2-camera-mission.py
# [미션] 카메라 영상을 5초 동안 녹화해서 파일로 저장하기 (Picamera2 + OpenCV)

import os
os.environ.setdefault("QT_QPA_PLATFORM", "xcb")

import cv2
import time
from picamera2 import Picamera2

# 1.카메라 프레임 크기 지정하기
width, height = 1024, 768
fps = 30

picam2 = Picamera2()
config = picam2.create_video_configuration(
    main={"size": (width, height), "format": "RGB888"}
)
picam2.configure(config)
picam2.start()
time.sleep(1)   # 카메라 밝기가 안정될 때까지 잠시 대기

# 5.동영상 저장파일 정보
file = 'output2.avi'
fourcc = cv2.VideoWriter_fourcc(*'DIVX')  # *'DIVX' == 'D','I','V','X'
out = cv2.VideoWriter(file, fourcc, fps, (width, height))

record = False

try:
    while True:     # 카메라 프레임 처리
        frame = picam2.capture_array()
        if frame is None:
            print('Can not read frame!')
            break

        # 2.frame flip
        frame = cv2.flip(frame, 0)

        # 3.text
        text = 'Camera recoding...'
        font = cv2.FONT_HERSHEY_DUPLEX
        cv2.putText(frame, text, (10, 20), font, 1, (0, 0, 255), 1)
        cv2.imshow('frame', frame)

        # 4.& 5.
        if record == True:
            out.write(frame)  # 프레임 저장하기
        else:  # start
            s_millis = int(round(time.time() * 1000))  # start time
            record = True
            print("녹화 중..")

        c_millis = int(round(time.time() * 1000))  # current time

        if c_millis - s_millis >= 5000:  # 5 second
            break

        if cv2.waitKey(10) == 27:
            break

finally:
    out.release()      # 동영상 파일 마무리 (이걸 빼면 파일이 깨진다)
    picam2.stop()
    picam2.close()
    cv2.destroyAllWindows()
    print(f'녹화 Finished!  ({file} 저장됨)')
