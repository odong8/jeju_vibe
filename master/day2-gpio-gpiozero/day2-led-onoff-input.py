# day2-led-onoff-input.py
# 키보드 입력으로 LED 켜고 끄기 (gpiozero)
# 배선: GPIO17 -- 저항 -- LED -- GND

from gpiozero import LED

led_pin = 17
led = LED(led_pin)

led.off()

try:
    print("#---사용자 입력 LED control-----")
    while True:
        userInput = input('키를 입력하세요(o/x/q): ')
        print(userInput)

        # 1. 'o' 입력시 LED 켜기
        if userInput == 'o':
            led.on()
            print('LED ON')

        # 2. 'x' 입력시 LED 끄기
        elif userInput == 'x':
            led.off()
            print('LED OFF')

        # 3. 'q' 입력시 프로그램 종료
        elif userInput == 'q':
            print('프로그램을 종료합니다.')
            break

        else:
            print('o(켜기), x(끄기), q(종료) 중에서 입력하세요.')

except KeyboardInterrupt:
    print("except KeyboardInterrupt")

finally:
    print("cleanup all GPIO")
    led.close()
