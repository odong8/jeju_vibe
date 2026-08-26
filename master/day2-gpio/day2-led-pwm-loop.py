import RPi.GPIO as GPIO
import time

GPIO.setwarnings(False)

led_pin = 17
GPIO.setmode(GPIO.BCM)
GPIO.setup(led_pin, GPIO.OUT)

pwm = GPIO.PWM(led_pin, 1000.0)
pwm.start(0.0)   # pwm 시작 0.0 ~ 100.0

try:
    while True:
        for t_high in range(0,101):
            pwm.ChangeDutyCycle(t_high)
            time.sleep(0.01)
        for t_high in range(100,-1,-1):
            pwm.ChangeDutyCycle(t_high)
            time.sleep(0.01)
    
except KeyboardInterrupt:
    print("except KeyboardInterrupt")
    pass

pwm.stop()   # pwm 멈춤
GPIO.cleanup()