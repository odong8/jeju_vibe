# day2-led-button.py
# 버튼을 누르는 동안 LED 켜기 (gpiozero)
# 배선: 버튼 GPIO4 <-> GND  (gpiozero 가 내부 풀업을 켜므로 별도 저항 불필요)
#      LED   GPIO17 -- 저항 -- LED -- GND

from gpiozero import LED, Button
import time

led_pin = 17
button_pin = 4

led = LED(led_pin)

# gpiozero 의 Button 은 기본값이 pull_up=True (내부 풀업)
#  - 누르지 않음: 핀 HIGH -> is_pressed == False
#  - 누름       : 핀 LOW  -> is_pressed == True
# 풀다운 회로를 쓴다면 Button(button_pin, pull_up=False) 로 바꾼다.
button = Button(button_pin)

led.off()

try:
    while True:
        # print(button.is_pressed)
        if button.is_pressed:
            led.on()
        else:
            led.off()
        time.sleep(0.01)

    # [참고] gpiozero 는 아래 한 줄로도 같은 동작을 만들 수 있다.
    #   led.source = button

except KeyboardInterrupt:
    print("except KeyboardInterrupt")

finally:
    led.close()      # cleanup all GPIO
    button.close()
