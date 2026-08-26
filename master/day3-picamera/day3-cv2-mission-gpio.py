# day3-cv2-mission-gpio.py
# [미션] 온도가 기준값을 벗어나면 자동으로 사진 찍기
#   - 온습도: adafruit_dht
#     (예전의 Adafruit_DHT 라이브러리는 더 이상 관리되지 않고 Trixie/Python 3.13 에서 설치되지 않는다.
#      sudo pip install adafruit-circuitpython-dht --break-system-packages 로 설치한다.)
#   - 카메라: Picamera2

import os
os.environ.setdefault("QT_QPA_PLATFORM", "xcb")

import cv2
import datetime
import sys
import time
import adafruit_dht
import board
from picamera2 import Picamera2

TEMP_H = 25  # threshold value for take picture
TEMP_L = 15

SAVE_DIR = '/home/pi/master/autocamera'


def nowdate():
    now = datetime.datetime.now()
    nowdate = now.strftime('%Y%m%d-%H%M%S')
    return nowdate


def checkDHT11():
    dht_pin = board.D23        # GPIO23번 핀
    dht_device = adafruit_dht.DHT11(dht_pin)
    temp = None

    for i in range(3):
        try:
            temp = dht_device.temperature
            humity = dht_device.humidity

            if humity is not None and temp is not None:
                print(f"[{i+1}] {nowdate()} Temperature={temp:0.1f}C,  Humidity={humity:0.1f}%")
            else:
                print("Read Error")

        except RuntimeError as e:
            print(f"Reading error: {e.args}")

        time.sleep(1)

    dht_device.exit()
    return temp


def takePicture():
    os.makedirs(SAVE_DIR, exist_ok=True)

    # 카메라 열기
    picam2 = Picamera2()
    config = picam2.create_still_configuration(
        main={"size": (1280, 720), "format": "RGB888"}
    )
    picam2.configure(config)
    picam2.start()
    time.sleep(2)

    try:
        frame = picam2.capture_array()
        if frame is None:
            print("Can not read frame!")
            return

        # save the frame
        file = f'{SAVE_DIR}/picture-{nowdate()}.jpg'  # photo filename
        cv2.imwrite(file, frame)
        print(f'{file} 저장됨')

    finally:
        picam2.stop()
        picam2.close()


#-------------------
# main
#-------------------

print()
print(f'{nowdate()} : [start] auto check temperature ---')

temp = checkDHT11()
if temp is not None and (temp >= TEMP_H or temp <= TEMP_L):
    takePicture()

print(f'{nowdate()} : [end  ] auto check temperature ---')
