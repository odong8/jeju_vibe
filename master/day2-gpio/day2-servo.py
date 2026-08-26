import RPi.GPIO as GPIO
import time

GPIO.setwarnings(False)

print("# Servo motor----")
servo_pin = 18
GPIO.setmode(GPIO.BCM)
GPIO.setup(servo_pin, GPIO.OUT)

pwm = GPIO.PWM(servo_pin, 50)  # 50Hz
pwm.start(1)

# 서보모터를 정해진 각도로 맞추기 
d_cycle, degree = 2.5, 0    # 2.5(0도)
# d_cycle, degree = 7.5, 90   # 7.5(90) 
# d_cycle, degree = 12.5, 180 # 12.5(180)
pwm.ChangeDutyCycle(d_cycle)
print(f'DutyCycle: {d_cycle}-{degree}도')
time.sleep(1)

pwm.ChangeDutyCycle(0.0) # 0% 동작 멈춤 
    
pwm.stop()   # pwm 멈춤
GPIO.cleanup()