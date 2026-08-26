import RPi.GPIO as GPIO

GPIO.setwarnings(False)

led_pin = 17
GPIO.setmode(GPIO.BCM)
GPIO.setup(led_pin, GPIO.OUT)

try:
    print("set GIOP high")    
    GPIO.output(led_pin, True)
    while True:        
        pass
        
except KeyboardInterrupt:  # Ctrl + c
    print("except KeyboardInterrupt")
    GPIO.cleanup() # cleanup all GPIO