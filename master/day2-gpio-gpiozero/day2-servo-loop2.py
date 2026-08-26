# day2-servo-loop2.py
# 서보모터 각도를 0 -> 90 -> 180 순서로 3번 반복하기 (gpiozero)
# 배선: 서보 신호선 GPIO18, VCC 5V, GND 공통

from gpiozero import AngularServo
import time

print("# Servo motor loop----")
servo_pin = 18

servo = AngularServo(
    servo_pin,
    min_angle=0, max_angle=180,
    min_pulse_width=0.0005,   # 0.5ms  (0도)
    max_pulse_width=0.0025,   # 2.5ms  (180도)
)

try:
    servo.detach()  # 동작 멈춤
    print('start-----------')
    time.sleep(1.0)

    # 서보모터 특정 각도로 변경하기
    degrees = [0, 90, 180]
    for i in range(3):
        for degree in degrees:
            print(f'각도: {degree}도')
            servo.angle = degree
            time.sleep(2.0)

        servo.detach()  # 동작 멈춤
        time.sleep(1.0)
        print(f'count[{i+1}]')

    servo.detach()  # 동작 멈춤

finally:
    servo.close()
