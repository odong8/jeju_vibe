# day2-led-on.py
# LED 켜기 (gpiozero)
# 배선: GPIO17 -- 저항 -- LED -- GND

from gpiozero import LED
import time

led_pin = 17
led = LED(led_pin)

try:
    led.on()
    print("set GPIO high")
    while True:
        time.sleep(0.1)

except KeyboardInterrupt:
    print("except KeyboardInterrupt")

finally:
    led.close()  # cleanup all GPIO
