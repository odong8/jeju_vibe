import RPi.GPIO as GPIO

GPIO.setwarnings(False)

led_pin = 17
GPIO.setmode(GPIO.BCM)
GPIO.setup(led_pin, GPIO.OUT)

GPIO.output(led_pin, False)

try:
    print("#---사용자 입력 LED control-----")
    while True:
        userInput = input('키를 입력하세요(o/x/q): ')
        print(userInput)
        # 1. 'o' 입력시 LED 켜기
        # 2. 'x' 입력시 LED 끄기
        # 3. 'q' 입력시 프로그램 종료
         
except KeyboardInterrupt:
    print("except KeyboardInterrupt")
    pass

print("cleanup all GPIO")
GPIO.cleanup() 