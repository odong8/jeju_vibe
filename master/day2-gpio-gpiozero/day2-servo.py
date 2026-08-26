# day2-servo.py
# 서보모터를 정해진 각도로 맞추기 (gpiozero)
# 배선: 서보 신호선 GPIO18, VCC 5V, GND 공통
#
# AngularServo 가 RPi.GPIO 의 GPIO.PWM(50Hz) + ChangeDutyCycle 을 대신한다.
#   듀티비  2.5% (50Hz) = 0.5ms 펄스 -> min_pulse_width=0.0005 ->   0도
#   듀티비 12.5% (50Hz) = 2.5ms 펄스 -> max_pulse_width=0.0025 -> 180도

from gpiozero import AngularServo
import time

print("# Servo motor----")
servo_pin = 18

servo = AngularServo(
    servo_pin,
    min_angle=0, max_angle=180,
    min_pulse_width=0.0005,   # 0.5ms  (0도)
    max_pulse_width=0.0025,   # 2.5ms  (180도)
)

try:
    # 서보모터를 정해진 각도로 맞추기
    degree = 0      # 0도
    # degree = 90   # 90도
    # degree = 180  # 180도
    servo.angle = degree
    print(f'각도: {degree}도')
    time.sleep(1)

    servo.detach()  # 펄스 출력 중지 (RPi.GPIO 의 ChangeDutyCycle(0.0) 와 같은 역할)

finally:
    servo.close()   # pwm 멈춤 + 자원 회수
