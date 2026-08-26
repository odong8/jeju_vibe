# day2-ultra-distance.py
# 초음파 센서(HC-SR04)로 거리 측정하기 (gpiozero)
#
# gpiozero 의 DistanceSensor 가 Trig 펄스 발생과 Echo 시간 측정을 모두 처리한다.
# (기존 RPi.GPIO 코드처럼 while 로 직접 시간을 재지 않아도 된다.)
#
# [핀 번호 변경 안내]
# 기존 코드는 Trig=GPIO2, Echo=GPIO3 을 사용했지만 이 두 핀은 I2C 전용 핀으로
# 보드에 1.8k 풀업 저항이 고정되어 있어서 gpiozero 의 DistanceSensor 가 사용할 수 없다.
# (또 day4 의 서보 드라이버(PCA9685)가 I2C 를 쓰므로 서로 충돌한다.)
# 그래서 아래처럼 일반 GPIO 핀으로 옮겼다.
#
# 배선:
#   HC-SR04 VCC  -- 5V
#   HC-SR04 GND  -- GND
#   HC-SR04 TRIG -- GPIO23
#   HC-SR04 ECHO -- 전압분배(330옴 + 470옴) -- GPIO24
#     * ECHO 출력은 5V 이므로 반드시 저항으로 3.3V 로 낮춰서 연결한다.

from gpiozero import DistanceSensor
import time

print('Ultrasonic -----------')

trig_pin = 23
echo_pin = 24

# max_distance: 측정 최대 거리(m). HC-SR04 는 약 4m 까지 측정 가능
sensor = DistanceSensor(echo=echo_pin, trigger=trig_pin, max_distance=4.0)

try:
    while True:
        # sensor.distance 는 0.0 ~ 1.0 (max_distance 에 대한 비율) 이 아니라 미터(m) 단위 값
        distance = sensor.distance * 100      # m -> cm
        distance = round(distance, 2)
        print(f"Distance : {distance:.1f} cm")

        time.sleep(0.5)

except KeyboardInterrupt:
    print("Measurement stopped by user")

finally:
    sensor.close()
