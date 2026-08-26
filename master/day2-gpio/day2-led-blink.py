import RPi.GPIO as GPIO
import time

GPIO.setwarnings(False)  

# GPIO.BCM
led_pin = 17
GPIO.setmode(GPIO.BCM)
GPIO.setup(led_pin, GPIO.OUT)

# GPIO.BOARD
# led_pin = 11
# GPIO.setmode(GPIO.BOARD)
# GPIO.setup(led_pin, GPIO.OUT)

try:
    print("--LED Blink (*Stop: ctrl+c)")
    while True:
        # LED blink (1Hz)
        GPIO.output(led_pin, True)
        time.sleep(0.5)
        GPIO.output(led_pin, False)
        time.sleep(0.5)
        
except KeyboardInterrupt:
    print("except KeyboardInterrupt")
    GPIO.cleanup()
