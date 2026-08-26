# autodht11_old.py
# autodht11.py 의 단순한 형태 (예외처리 없이 흐름만 보는 버전)
#   - 온습도: adafruit_dht
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

DHT_PIN = board.D23   # GPIO23번 핀에 연결된 경우
SAVE_DIR = '/home/pi/master/autocamera'


def nowdate():
    now = datetime.datetime.now()
    nowdate = now.strftime('%Y%m%d-%H%M%S')
    return nowdate


def checkDHT11():
    dht_device = adafruit_dht.DHT11(DHT_PIN)
    temperature = None

    for i in range(3):
        # 센서로부터 온도와 습도 값 읽기
        try:
            temperature = dht_device.temperature
            humidity = dht_device.humidity
        except RuntimeError as e:
            print(f"Reading error: {e.args}")
            time.sleep(1)
            continue

        if humidity is not None and temperature is not None:
            print(f"[{i+1}] {nowdate()} Temperature={temperature:0.1f}C,  Humidity={humidity:0.1f}%")
        else:
            print("Read Error")
        time.sleep(1)

    dht_device.exit()
    return temperature


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

    frame = picam2.capture_array()
    if frame is None:
        print("Can not read frame!")
    else:
        # save the frame
        file = f'{SAVE_DIR}/picture-{nowdate()}.jpg'  # photo filename
        cv2.imwrite(file, frame)
        print(f'{file} 저장됨')

    picam2.stop()
    picam2.close()


#-------------------
# main
#-------------------

print(f'{nowdate()} : [start] auto check temperature ---')

temperature = checkDHT11()
if temperature is not None and (temperature >= TEMP_H or temperature <= TEMP_L):
    takePicture()

print(f'{nowdate()} : [end  ] auto check temperature ---')
