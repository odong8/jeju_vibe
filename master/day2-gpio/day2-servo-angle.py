import RPi.GPIO as GPIO
import time

# 설정값
SERVO_PIN = 18  # GPIO 18번 핀
FREQ = 50       # 50Hz

# 초기 설정
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(SERVO_PIN, GPIO.OUT)

pwm = GPIO.PWM(SERVO_PIN, FREQ)
pwm.start(0)

# 서보모터 각도 → 듀티사이클 변환 함수
def angle_to_duty_cycle(angle):
    """
    주어진 각도(0~180도)를 서보모터 듀티사이클로 변환합니다.
    0도 → 2.5%, 180도 → 12.5%
    """
    return 2.5 + (angle / 180.0) * 10.0

# 서보모터를 원하는 각도로 이동시키는 함수
def move_servo_to(angle):
    """
    서보모터를 지정한 각도로 회전시킵니다.
    angle: 0~180 사이의 각도
    """
    if not (0 <= angle <= 180):
        raise ValueError("각도는 0도에서 180도 사이여야 합니다.")
    
    duty = angle_to_duty_cycle(angle)
    pwm.ChangeDutyCycle(duty)
    print(f"[INFO] 이동: {angle}도 → DutyCycle {duty:.2f}%")
    time.sleep(0.5)  # 안정화 시간
    pwm.ChangeDutyCycle(0.0)  # 모터 정지

# ===== 테스트 =====
try:
    while True:
        angle = int(input("이동할 각도 입력 (0~180, 종료는 -1): "))
        if angle == -1:
            break
        move_servo_to(angle)

except KeyboardInterrupt:
    pass

finally:
    pwm.stop()
    GPIO.cleanup()
    print("[INFO] 서보모터 종료 및 GPIO 정리 완료.")
