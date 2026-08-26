import RPi.GPIO as GPIO
import time

GPIO.setwarnings(False)

led_pin = 17
GPIO.setmode(GPIO.BCM)
GPIO.setup(led_pin, GPIO.OUT)

try:
    print("--LED 점점 밝게 점점 어둡게 변경하기")
    while True:        
        # LED 점점 밝게 하기
        for t_high in range(0, 11):
            cnt = 0
            while True:
                GPIO.output(led_pin, True)
                time.sleep(t_high*0.001)
                GPIO.output(led_pin, False)
                time.sleep((10-t_high)*0.001)
                
                cnt += 1
                if cnt == 10: break
        # LED 점점 어둡게 하기
        for t_high in range(10, -1, -1):
            cnt = 0
            while True:
                GPIO.output(led_pin, True)
                time.sleep(t_high*0.001)
                GPIO.output(led_pin, False)
                time.sleep((10-t_high)*0.001)
                
                cnt += 1
                if cnt == 10: break    
                    
except KeyboardInterrupt:
    print("except KeyboardInterrupt")
    pass

GPIO.cleanup()