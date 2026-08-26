import RPi.GPIO as GPIO
import time

GPIO.setwarnings(False)

print("# Servo motor loop----")
servo_pin = 18
GPIO.setmode(GPIO.BCM)
GPIO.setup(servo_pin, GPIO.OUT)

pwm = GPIO.PWM(servo_pin, 50)  # 50Hz
pwm.start(1)   

# 서보모터 0도 각도 맞추기
pwm.ChangeDutyCycle(2.5)
time.sleep(2.0)
print('start-----------')

# 서보모터 특정 각도로 변경하기
for i in range(0,3):
    print("count = " + str(i))
    print("12.5")
    pwm.ChangeDutyCycle(12.5)
    time.sleep(2)        
    
    print("7.5")
    pwm.ChangeDutyCycle(7.5)
    time.sleep(2)
    
    print("2.5")
    pwm.ChangeDutyCycle(2.5)
    time.sleep(2)

pwm.ChangeDutyCycle(0.0) # 0% 동작 멈춤
pwm.stop()   # pwm 멈춤
GPIO.cleanup()