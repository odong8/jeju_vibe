import RPi.GPIO as GPIO
import time

GPIO.setwarnings(False)

# GPIO.BCM
led_pin = 17
GPIO.setmode(GPIO.BCM)
GPIO.setup(led_pin, GPIO.OUT)

GPIO.output(led_pin, False)

try:
    print("--LED 밝기 변경하기")
    while True:
        # LED high구간 조정하여 밝게 하기 
        GPIO.output(led_pin, True)
        time.sleep(0.001)
        GPIO.output(led_pin, False)
        time.sleep(0.009)        
        
except KeyboardInterrupt:
    print("except KeyboardInterrupt")
    GPIO.cleanup()
