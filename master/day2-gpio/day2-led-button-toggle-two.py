import RPi.GPIO as GPIO
import time

GPIO.setwarnings(False)

led_pin = [17,27]
button_pin = 4

GPIO.setmode(GPIO.BCM)
GPIO.setup(led_pin, GPIO.OUT)
GPIO.setup(button_pin, GPIO.IN)
GPIO.output(led_pin, False)

try: 
    button_on = 0
    while True:
        # 푸시버튼 방식이 풀업(누르지 않으면 1), 풀다운(0)에 따라서 코드를 다르게 한다.
        # 아래코드 풀업 방식인 경우
        if GPIO.input(button_pin)==False:  # 버튼 클릭하면
            time.sleep(0.1)  # 시간간격 주기
            button_on += 1
            
            if button_on%3==1:
                GPIO.output(led_pin[0], True)  # LED1 On
            elif button_on%3==2:
                GPIO.output(led_pin[1], True)  # LED2 On
            elif button_on%3==0:
                GPIO.output(led_pin, False)  # LED1+LED2 Off
                button_on = 0
            
        time.sleep(0.1)
        print('button_on: ', button_on)
except KeyboardInterrupt:
    print("except KeyboardInterrupt")
    GPIO.cleanup()  # cleanup all GPIO
