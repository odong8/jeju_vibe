import RPi.GPIO as GPIO

GPIO.setwarnings(False)

led_pin = 17
button_pin = 4

GPIO.setmode(GPIO.BCM)
GPIO.setup(led_pin, GPIO.OUT)
GPIO.setup(button_pin, GPIO.IN)
GPIO.output(led_pin, False)

try: 
    while True:
        # print(GPIO.input(button_pin))
        # 푸시버튼 방식이 풀업(누르지 않으면 1), 풀다운(0)에 따라서 코드를 다르게 한다.
        # 아래코드 풀업 방식인 경우
        if GPIO.input(button_pin)==True:
            GPIO.output(led_pin, False)
        elif GPIO.input(button_pin)==False:
            GPIO.output(led_pin, True)
    
except KeyboardInterrupt:
    print("except KeyboardInterrupt")
    GPIO.cleanup()  # cleanup all GPIO
