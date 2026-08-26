# day2-led-blink.py
# LED 1Hz 로 깜빡이기 (gpiozero)
# 배선: GPIO17 -- 저항 -- LED -- GND

from gpiozero import LED
import time

led_pin = 17
led = LED(led_pin)

try:
    print("--LED Blink (*Stop: ctrl+c)")
    while True:
        # LED blink (1Hz)
        led.on()
        time.sleep(0.5)
        led.off()
        time.sleep(0.5)

    # [참고] gpiozero 에는 깜빡임 전용 기능도 있다.
    #   led.blink(on_time=0.5, off_time=0.5)   # 백그라운드로 계속 깜빡임
    #   pause()                                 # from signal import pause

except KeyboardInterrupt:
    print("except KeyboardInterrupt")

finally:
    led.close()
