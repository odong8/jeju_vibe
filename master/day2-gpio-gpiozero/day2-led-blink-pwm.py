# day2-led-blink-pwm.py
# LED 를 아주 빠르게 켜고 끄면(=PWM 원리) 밝기가 달라지는 것을 확인하기 (gpiozero)
# 배선: GPIO17 -- 저항 -- LED -- GND

from gpiozero import LED
import time

led_pin = 17
led = LED(led_pin)
led.off()

try:
    print("--LED 밝기 변경하기")
    while True:
        # 한 주기 10ms 중에서 켜져 있는 시간(High 구간)을 조정하여 밝기를 바꾼다.
        # 아래는 1ms 켜고 9ms 끄기 --> 밝기 10%
        led.on()
        time.sleep(0.001)
        led.off()
        time.sleep(0.009)

except KeyboardInterrupt:
    print("except KeyboardInterrupt")

finally:
    led.close()
