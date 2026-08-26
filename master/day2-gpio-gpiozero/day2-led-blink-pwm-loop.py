# day2-led-blink-pwm-loop.py
# LED 를 점점 밝게 / 점점 어둡게 (PWM 원리를 직접 구현) (gpiozero)
# 배선: GPIO17 -- 저항 -- LED -- GND

from gpiozero import LED
import time

led_pin = 17
led = LED(led_pin)

try:
    print("--LED 점점 밝게 점점 어둡게 변경하기")
    while True:
        # LED 점점 밝게 하기 (High 구간 0ms -> 10ms)
        for t_high in range(0, 11):
            cnt = 0
            while True:
                led.on()
                time.sleep(t_high * 0.001)
                led.off()
                time.sleep((10 - t_high) * 0.001)

                cnt += 1
                if cnt == 10: break

        # LED 점점 어둡게 하기 (High 구간 10ms -> 0ms)
        for t_high in range(10, -1, -1):
            cnt = 0
            while True:
                led.on()
                time.sleep(t_high * 0.001)
                led.off()
                time.sleep((10 - t_high) * 0.001)

                cnt += 1
                if cnt == 10: break

except KeyboardInterrupt:
    print("except KeyboardInterrupt")

finally:
    led.close()
