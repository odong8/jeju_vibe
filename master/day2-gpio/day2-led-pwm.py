import RPi.GPIO as GPIO

GPIO.setwarnings(False)

led_pin = 17
GPIO.setmode(GPIO.BCM)
GPIO.setup(led_pin, GPIO.OUT)

pwm = GPIO.PWM(led_pin, 1.0)  # 1.0Hz
# pwm = GPIO.PWM(led_pin, 10.0)  # 10.0Hz
# pwm = GPIO.PWM(led_pin, 100.0)  # 100.0Hz
pwm.start(50.0)   # pwm 시작 0.0 ~ 100.0

try:
    while True:
        pass
    
except KeyboardInterrupt:
    print("except KeyboardInterrupt")
    pass

pwm.stop()   # pwm 멈춤
GPIO.cleanup()