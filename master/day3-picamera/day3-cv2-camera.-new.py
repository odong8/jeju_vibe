# day3-cv2-camera.-new.py
# Picamera2 로 카메라 영상 받아서 OpenCV 로 보여주기 (가장 기본 형태)
#   q 키를 누르면 종료

import os
# Wayland 환경에서 cv2.imshow 창이 뜨도록 (반드시 cv2 import 전에 설정)
os.environ["QT_QPA_PLATFORM"] = "xcb"

import cv2
from picamera2 import Picamera2

picam2 = Picamera2()

width = 640
height = 480

# format="RGB888" 로 지정하면 numpy 배열이 OpenCV 와 같은 BGR 순서로 나온다.
config = picam2.create_video_configuration(
    main={
        "size": (width, height),
        "format": "RGB888"
    }
)

picam2.configure(config)
picam2.start()

print("Camera started")

try:
    while True:

        frame = picam2.capture_array()

        print("Frame shape:", frame.shape)

        cv2.imshow("Camera", frame)

        key = cv2.waitKey(1) & 0xFF
        if key == ord("q"):
            break

finally:
    picam2.stop()
    picam2.close()
    cv2.destroyAllWindows()
