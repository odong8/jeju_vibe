# day2-dht11-file.py
# DHT11 온습도 센서 값을 읽어서 파일로 저장하기
#
# [참고] gpiozero 에는 DHT11 드라이버가 없어서 adafruit_dht 를 사용한다.
#        adafruit_dht 가 핀을 직접 관리하므로 RPi.GPIO / gpiozero 는 필요 없다.
#
# [주의!] 프로그램 멈출때는 Ctrl + C로 멈추세요.
# 배선: DHT11 DATA -- GPIO23, VCC -- 3.3V, GND -- GND

import adafruit_dht
import board
import time
import datetime

# DHT 센서를 사용할 핀 설정
DHT_PIN = board.D23  # GPIO 23번 핀에 연결된 경우

# DHT11 센서 객체 생성
dht_device = adafruit_dht.DHT11(DHT_PIN)

try:
    print("Temperature Humidity check")
    # with 를 쓰면 프로그램이 어떻게 끝나든 파일이 안전하게 닫힌다.
    with open('day2-dht11-file.txt', 'a+') as f:
        print("T/H check start ----------")
        while True:
            try:
                # 센서로부터 온도와 습도 값 읽기
                temperature = dht_device.temperature
                humidity = dht_device.humidity

                now = datetime.datetime.now()
                ctime = now.strftime("%Y-%m-%d %H:%M:%S")

                if temperature is not None and humidity is not None:
                    msg = f"{ctime} Temperature={temperature:0.1f}°C  Humidity={humidity:0.1f}%"
                else:
                    msg = f"{ctime} Read Error"

                print(msg)
                f.write(msg + "\n")
                f.flush()   # 바로 파일에 기록 (전원이 꺼져도 내용이 남도록)

            except RuntimeError as e:
                # DHT 센서는 간헐적으로 오류 발생할 수 있음
                print(f"Reading error: {e.args}")

            # 2초 간격으로 데이터 읽기
            time.sleep(2)

except KeyboardInterrupt:
    print("KeyboardInterrupt by user")

finally:
    # 프로그램 종료 시 센서 객체 해제
    dht_device.exit()
    print("Program terminated and resources cleaned up.")
