#!/usr/bin/env python3
# 파일명: day3-cv2-camera-mission-photo-button-led.py
# 설명: 버튼을 누르면 LED 플래시가 터지고 사진이 저장된다.
#      카메라는 Picamera2, GPIO 는 gpiozero 를 사용한다.
#      gpiozero 의 Button 은 내부적으로 엣지 감지를 처리하므로
#      RPi.GPIO 처럼 폴링/디바운스를 직접 짤 필요가 없다.
#
# 권장 배선(BCM 번호):
# - LED: GPIO17 → 저항 → LED → GND
# - 버튼: GPIO23 ↔ GND  (내부 풀업 사용, 눌렀을 때 LOW)
#
# 필요 패키지:
#   sudo apt install python3-picamera2 python3-opencv python3-gpiozero

import os
os.environ.setdefault("QT_QPA_PLATFORM", "xcb")

import cv2
import time
from gpiozero import LED, Button
from picamera2 import Picamera2

# ---------------------- 설정 ----------------------
LED_PIN = 17
BUTTON_PIN = 23   # 충돌 적은 핀 권장: 23/24/25 등

# 카메라 해상도
CAM_WIDTH  = 640
CAM_HEIGHT = 480

# 플래시(LED) 빠르게 깜빡이는 횟수/간격
FLASH_TIMES   = 3
FLASH_ON_SEC  = 0.05
FLASH_OFF_SEC = 0.05
# --------------------------------------------------

def now_filename(prefix="photo"):
    return time.strftime(f"{prefix}_%Y%m%d_%H%M%S.jpg")

def flash_led(led, times=FLASH_TIMES, on_sec=FLASH_ON_SEC, off_sec=FLASH_OFF_SEC):
    for _ in range(times):
        led.on()
        time.sleep(on_sec)
        led.off()
        time.sleep(off_sec)

def main():
    # GPIO 초기화
    led = LED(LED_PIN)
    # bounce_time: 버튼 채터링(떨림) 방지
    button = Button(BUTTON_PIN, pull_up=True, bounce_time=0.05)

    # 카메라 초기화
    picam2 = Picamera2()
    config = picam2.create_video_configuration(
        main={"size": (CAM_WIDTH, CAM_HEIGHT), "format": "RGB888"}
    )
    picam2.configure(config)
    picam2.start()

    last_saved = ""

    try:
        while True:
            frame = picam2.capture_array()
            if frame is None:
                print("프레임을 읽을 수 없습니다.")
                break

            # 버튼이 눌렸는지 확인 (gpiozero 가 디바운스까지 처리해준다)
            if button.is_pressed:
                # 플래시 → 촬영 → 저장
                flash_led(led)
                shot = picam2.capture_array()
                if shot is None:
                    shot = frame.copy()

                filename = now_filename("photo")
                cv2.imwrite(filename, shot)
                print(f"{filename} 저장됨")
                last_saved = filename

                # 누르고 있는 동안 중복 촬영 방지
                button.wait_for_release()

            # 화면 안내
            info1 = "Press BUTTON to shoot"
            info2 = f"Saved: {last_saved}" if last_saved else "Ready..."
            cv2.putText(frame, info1, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            cv2.putText(frame, info2, (10, CAM_HEIGHT - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
            cv2.imshow("Camera", frame)

            # ESC 종료
            key = cv2.waitKey(1) & 0xFF
            if key == 27:
                break

    except KeyboardInterrupt:
        print("KeyboardInterrupt: 사용자에 의해 종료")

    finally:
        picam2.stop()
        picam2.close()
        cv2.destroyAllWindows()
        led.close()
        button.close()

if __name__ == "__main__":
    main()
