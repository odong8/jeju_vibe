# day2-mission-rgb_led.py
# RGB LED 로 여러 가지 색 만들기 (gpiozero)
#
# [핀 번호 주의]
# 기존 RPi.GPIO 코드는 GPIO.BOARD(물리 핀 번호) 모드에서 18/19/21 번을 사용했다.
# gpiozero 는 항상 BCM 번호를 쓰므로 아래와 같이 변환했다.
#   물리핀 18 -> BCM 24 (빨강)
#   물리핀 19 -> BCM 10 (초록)
#   물리핀 21 -> BCM  9 (파랑)
# 만약 실제 배선이 BCM 18/19/21 이라면 아래 pins 를 (18, 19, 21) 로 바꾸면 된다.

from gpiozero import RGBLED
import time

pins = (24, 10, 9)  # 빨강, 초록, 파랑 순서 (BCM 번호)

# 색 이름 -> (R, G, B)
RGBs = [
    (1, 1, 1),  # 0: 하양색
    (1, 0, 0),  # 1: 빨강색
    (0, 1, 0),  # 2: 초록색
    (0, 0, 1),  # 3: 파랑색
    (0, 1, 1),  # 4: 청록색
    (1, 0, 1),  # 5: 보라색
    (1, 1, 0),  # 6: 노랑색
]

# pwm=False -> 켜짐/꺼짐만 사용 (기존 코드와 동일한 동작)
# pwm=True  로 바꾸면 (0.5, 0.2, 0.0) 처럼 중간 밝기도 표현할 수 있다.
# active_high=False -> 공통 애노드(common anode) RGB LED 를 쓰는 경우
rgb_led = RGBLED(red=pins[0], green=pins[1], blue=pins[2], pwm=False)


def RGB(color, t):
    """color 번호의 색으로 t 초 동안 점등한다."""
    rgb_led.color = RGBs[color]
    time.sleep(t)
    rgb_led.off()


try:
    print("RGB Traffic Light  (종료: Ctrl + C)")
    while True:
        RGB(1, 3)  # 빨강색으로 3초 동안 점등
        time.sleep(1)
        RGB(2, 3)  # 초록색으로 3초 동안 점등
        time.sleep(1)
        RGB(3, 3)  # 파랑색으로 3초 동안 점등
        time.sleep(1)

except KeyboardInterrupt:
    print("except KeyboardInterrupt")

finally:
    rgb_led.close()  # cleanup all GPIO
