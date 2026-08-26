# day2-led-pwm-loop.py
# PWMLED 로 LED 를 점점 밝게 / 점점 어둡게 반복하기 (gpiozero)
# 배선: GPIO17 -- 저항 -- LED -- GND

from gpiozero import PWMLED
import time

led_pin = 17

led = PWMLED(led_pin, frequency=1000)  # 1000Hz
led.value = 0.0                        # pwm 시작 (듀티비 0.0 ~ 1.0)

try:
    while True:
        # 점점 밝게 (0% -> 100%)
        for t_high in range(0, 101):
            led.value = t_high / 100
            time.sleep(0.01)
        # 점점 어둡게 (100% -> 0%)
        for t_high in range(100, -1, -1):
            led.value = t_high / 100
            time.sleep(0.01)

    # [참고] gpiozero 에는 밝기 조절 전용 기능도 있다.
    #   led.pulse(fade_in_time=1, fade_out_time=1)  # 백그라운드로 계속 반복

except KeyboardInterrupt:
    print("except KeyboardInterrupt")

finally:
    led.off()     # pwm 멈춤
    led.close()
