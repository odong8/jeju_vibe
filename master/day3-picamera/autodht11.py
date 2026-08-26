# autodht11.py
# 온도가 기준값을 벗어나면 자동으로 사진을 찍어 저장한다.
#   - 온습도: adafruit_dht (gpiozero 에는 DHT 드라이버가 없다)
#   - 카메라: Picamera2 (Trixie 부터 cv2.VideoCapture(0) 로는 CSI 카메라를 못 연다)
# cron 으로 주기 실행하는 용도 (autodht11.sh 참고)

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

SAVE_DIR = '/home/pi/master/autocamera'   # 사진 저장 폴더

DHT_PIN = board.D23  # GPIO23번 핀에 연결된 경우
dht_device = adafruit_dht.DHT11(DHT_PIN)


def nowdate():
    now = datetime.datetime.now()
    nowdate = now.strftime('%Y%m%d-%H%M%S')
    return nowdate


def checkDHT11():
    """3번 읽어서 마지막으로 성공한 온도를 돌려준다. 모두 실패하면 None."""
    temperature = None

    for i in range(3):
        try:
            # 센서로부터 온도와 습도 값 읽기
            t = dht_device.temperature
            humidity = dht_device.humidity

            if humidity is not None and t is not None:
                temperature = t
                print(f"[{i+1}] {nowdate()} Temperature={temperature:0.1f}C,  Humidity={humidity:0.1f}%")
            else:
                print("Read Error")

        except RuntimeError as e:
            # DHT 센서는 간헐적으로 오류 발생할 수 있음
            print(f"Reading error: {e.args}")

        time.sleep(1)

    return temperature


def takePicture():
    # 저장 폴더가 없으면 만들기
    os.makedirs(SAVE_DIR, exist_ok=True)

    # 카메라 열기
    picam2 = Picamera2()
    config = picam2.create_still_configuration(
        main={"size": (1280, 720), "format": "RGB888"}
    )
    picam2.configure(config)
    picam2.start()
    time.sleep(2)   # 밝기/초점이 안정될 때까지 대기

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

try:
    print(f'{nowdate()} : [start] auto check temperature ---')

    temperature = checkDHT11()

    if temperature is None:
        print('온도를 읽지 못했습니다. 사진을 찍지 않습니다.')
    else:
        temperature = int(temperature)
        if temperature >= TEMP_H or temperature <= TEMP_L:
            takePicture()

    print(f'{nowdate()} : [end  ] auto check temperature ---')

except KeyboardInterrupt:
    print("KeyboardInterrupt by user")

finally:
    # 프로그램 종료 시 센서 객체 해제
    dht_device.exit()
    print("Program terminated and resources cleaned up.")
