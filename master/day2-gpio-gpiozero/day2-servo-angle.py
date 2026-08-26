# day2-servo-angle.py
# 키보드로 각도를 입력해서 서보모터 움직이기 (gpiozero)
# 배선: 서보 신호선 GPIO18, VCC 5V, GND 공통

from gpiozero import AngularServo
import time

# 설정값
SERVO_PIN = 18   # GPIO 18번 핀 (BCM)

# AngularServo 가 50Hz PWM 과 듀티사이클 계산을 대신 처리해준다.
#   0도   <- 0.5ms 펄스 (기존 코드의 듀티 2.5%)
#   180도 <- 2.5ms 펄스 (기존 코드의 듀티 12.5%)
servo = AngularServo(
    SERVO_PIN,
    min_angle=0, max_angle=180,
    min_pulse_width=0.0005,
    max_pulse_width=0.0025,
)


# 서보모터를 원하는 각도로 이동시키는 함수
def move_servo_to(angle):
    """
    서보모터를 지정한 각도로 회전시킵니다.
    angle: 0~180 사이의 각도
    """
    if not (0 <= angle <= 180):
        raise ValueError("각도는 0도에서 180도 사이여야 합니다.")

    servo.angle = angle
    print(f"[INFO] 이동: {angle}도")
    time.sleep(0.5)   # 안정화 시간
    servo.detach()    # 모터 정지 (펄스 출력 중지)


# ===== 테스트 =====
try:
    while True:
        try:
            angle = int(input("이동할 각도 입력 (0~180, 종료는 -1): "))
        except ValueError:
            print("숫자를 입력하세요.")
            continue

        if angle == -1:
            break

        try:
            move_servo_to(angle)
        except ValueError as e:
            print(f"[ERROR] {e}")

except KeyboardInterrupt:
    pass

finally:
    servo.close()
    print("[INFO] 서보모터 종료 및 GPIO 정리 완료.")
