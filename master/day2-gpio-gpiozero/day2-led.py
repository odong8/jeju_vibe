# day2-led.py
# LED 켜기 (gpiozero)
# 배선: GPIO17 -- 저항 -- LED -- GND

from gpiozero import LED
import time

led_pin = 17            # BCM 번호 (gpiozero는 항상 BCM 기준)
led = LED(led_pin)

try:
    print("set GPIO high")
    led.on()            # RPi.GPIO의 GPIO.output(led_pin, True)와 같음
    while True:
        time.sleep(0.1)  # CPU를 쉬게 하면서 대기 (pass 로 돌리면 CPU 100%)

except KeyboardInterrupt:  # Ctrl + C
    print("except KeyboardInterrupt")

finally:
    led.close()          # 자원 회수 (RPi.GPIO의 GPIO.cleanup() 역할)
