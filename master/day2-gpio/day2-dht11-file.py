import RPi.GPIO as GPIO
import adafruit_dht
import board
import time
import datetime

# [주의!] 프로그램 멈출때는 Ctrl + C로 멈추세요.
# 자원회수가 안될 때(Unable to set pin번호~ 메시지가 나올때)
# - 터미널에서 "ps -ef | grep python" 명령으로 gpio 관련 프로세스 번호 확인하고
# - 터미널에서 "sudo kill -9 프로세스번호" 명령으로 해당프로세스 삭제하기 
#------
# DHT 센서를 사용할 핀 설정(예: GPIO 00번 핀)
DHT_PIN = board.D23  # GPIO 23번 핀에 연결된 경우

# DHT11 센서 객체 생성
dht_device = adafruit_dht.DHT11(DHT_PIN)

try:
    print("Temperature Humidity check")
    f = open('day2-dht11-file.txt', 'a+')
    print("T/H check start ----------")
    while True: 
        try:       
            # 센서로부터 온도와 습도 값 읽기
            temperature = dht_device.temperature
            humidity = dht_device.humidity
            print(f"Temperature: {temperature}°C, Humidity: {humidity}%")
            
            now = datetime.datetime.now()
            ctime = now.strftime("%Y-%m-%d %H:%M:%S")
            if temperature and humidity:
                msg = f"{ctime} Temperature={temperature:0.1f}°C  Humidity={humidity:0.1f}%"
            else:
                msg = "{ctime} Read Error"
            print(msg)
            print(msg, file=f)
            f.write(msg+"\n")

        except RuntimeError as e:
            # DHT 센서는 간헐적으로 오류 발생할 수 있음
            print(f"Reading error: {e.args}")
        
        # 2초 간격으로 데이터 읽기
        time.sleep(2)
        
except KeyboardInterrupt:
    print("KeyboardInterrupt by user")
    f.close()

finally:
    # 프로그렘 종료 시 센서 객체 해제
    dht_device.exit()    
    del dht_device
    
    GPIO.cleanup()
    print("Program terminated and resources cleaned up.")