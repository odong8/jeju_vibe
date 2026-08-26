import RPi.GPIO as GPIO
import time

GPIO.setwarnings(False)

print('Ultrasonic -----------')

trig_pin = 2
echo_pin = 3

GPIO.setmode(GPIO.BCM)
GPIO.setup(trig_pin, GPIO.OUT)
GPIO.setup(echo_pin, GPIO.IN)

try:
    while True:
        #Trig핀의 신호를 0으로 출력
        GPIO.output(trig_pin,False)  # Trig 핀 초기 설정
        time.sleep(0.5)
        
        print("trig  True")
        GPIO.output(trig_pin, True)  # trig  핀에서 펄스 생성
        time.sleep(0.00001)   # 10 마이크로세컨드 딜레이
        GPIO.output(trig_pin, False)
        print("trig  False")
        
        
        while GPIO.input(echo_pin) == 0:
            print("echo_pin==0")
            start = time.time()           # echo핀 상승 시간
            
        while GPIO.input(echo_pin) == 1:
            print("echo_pin==1")
            stop = time.time()           # echo핀 하강 시간


        pulse_duration = stop - start
        distance = pulse_duration * (340*100) / 2
        distance = round(distance,2)        
        print(f"Distance : {distance:.1f} cm")
        
except KeyboardInterrupt:
    print("Measurement stopped by user")
    pass
    
except:
    print("Measurement stopped by system")
    GPIO.cleanup()
    
finally:
    GPIO.cleanup()