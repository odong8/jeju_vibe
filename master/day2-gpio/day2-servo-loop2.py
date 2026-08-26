import RPi.GPIO as GPIO
import time

GPIO.setwarnings(False)

print("# Servo motor loop----")
servo_pin = 18
GPIO.setmode(GPIO.BCM)
GPIO.setup(servo_pin, GPIO.OUT)

pwm = GPIO.PWM(servo_pin, 50)  # 50Hz
pwm.start(1)   

pwm.ChangeDutyCycle(0.0) # 0% 동작 멈춤
print('start-----------')
time.sleep(1.0)

# 서보모터 특정 각도로 변경하기
d_cycles = {2.5:0, 7.5:90, 12.5:180}
for i in range(3):
    for d_cycle in d_cycles:
        print(f'DutyCycle: {d_cycle}-{d_cycles[d_cycle]}도')
        pwm.ChangeDutyCycle(d_cycle)
        time.sleep(2.0)        
    
    pwm.ChangeDutyCycle(0.0) # 0% 동작 멈춤
    time.sleep(1.0)
    print(f'count[{i+1}]')

pwm.ChangeDutyCycle(0.0) # 0% 동작 멈춤

pwm.stop()   # pwm 멈춤
GPIO.cleanup()