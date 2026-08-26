# day2-led-button-toggle-two.py
# 버튼을 누를 때마다 LED 2개를 순서대로 켜고, 3번째에 모두 끄기 (gpiozero)
#   1번 누름 -> LED1 ON
#   2번 누름 -> LED1 + LED2 ON
#   3번 누름 -> 모두 OFF (카운트 초기화)
#
# 배선: 버튼 GPIO4  <-> GND (내부 풀업 사용)
#      LED1 GPIO17 -- 저항 -- LED -- GND
#      LED2 GPIO27 -- 저항 -- LED -- GND

from gpiozero import LEDBoard, Button
import time

led_pin = [17, 27]
button_pin = 4

# LEDBoard: 여러 개의 LED 를 한 번에 다루는 gpiozero 기능
leds = LEDBoard(*led_pin)

# 푸시버튼 방식이 풀업(누르지 않으면 1), 풀다운(0)에 따라서 코드를 다르게 한다.
# 아래코드 풀업 방식인 경우 (gpiozero 기본값 pull_up=True)
button = Button(button_pin, pull_up=True, bounce_time=0.1)

leds.off()

button_on = 0

try:
    print("버튼을 누르세요.  (종료: Ctrl + C)")
    while True:
        if button.is_pressed:
            button_on += 1

            if button_on % 3 == 1:
                leds[0].on()      # LED1 On
            elif button_on % 3 == 2:
                leds[1].on()      # LED2 On (LED1 은 켜진 상태 유지)
            elif button_on % 3 == 0:
                leds.off()        # LED1 + LED2 Off
                button_on = 0

            print('button_on: ', button_on)

            # 버튼에서 손을 뗄 때까지 기다림 (중복 카운트 방지)
            button.wait_for_release()

        time.sleep(0.01)

except KeyboardInterrupt:
    print("except KeyboardInterrupt")

finally:
    leds.close()      # cleanup all GPIO
    button.close()
