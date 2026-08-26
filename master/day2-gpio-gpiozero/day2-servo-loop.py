# day2-servo-loop.py
# 서보모터를 0도 -> 180도 -> 90도 -> 0도 순서로 3번 반복하기 (gpiozero)
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
    # 서보모터 0도 각도 맞추기
    servo.angle = 0
    time.sleep(2.0)
    print('start-----------')

    # 서보모터 특정 각도로 변경하기
    for i in range(0, 3):
        print("count = " + str(i))

        print("180도")
        servo.angle = 180
        time.sleep(2)

        print("90도")
        servo.angle = 90
        time.sleep(2)

        print("0도")
        servo.angle = 0
        time.sleep(2)

    servo.detach()  # 동작 멈춤

finally:
    servo.close()
