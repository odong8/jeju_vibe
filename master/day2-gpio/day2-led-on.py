import RPi.GPIO as GPIO

GPIO.setwarnings(False)

led_pin = 17
GPIO.setmode(GPIO.BCM)
GPIO.setup(led_pin, GPIO.OUT)

try:
    GPIO.output(led_pin, True)
    print("set GIOP high")    
    while True:
        pass
    
except KeyboardInterrupt:
    print("except KeyboardInterrupt")
    GPIO.cleanup()  # cleanup all GPIO
