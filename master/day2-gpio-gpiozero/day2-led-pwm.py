# day2-led-pwm.py
# PWMLED 로 LED 밝기(듀티비) 조절하기 (gpiozero)
# RPi.GPIO 의 GPIO.PWM(pin, freq) + pwm.start(duty) 를 PWMLED 가 대신한다.
# 배선: GPIO17 -- 저항 -- LED -- GND

from gpiozero import PWMLED
import time

led_pin = 17

# frequency: PWM 주파수(Hz)
led = PWMLED(led_pin, frequency=1)      # 1.0Hz -- 눈으로 깜빡임이 보인다
# led = PWMLED(led_pin, frequency=10)   # 10.0Hz
# led = PWMLED(led_pin, frequency=100)  # 100.0Hz -- 깜빡임 대신 밝기로 보인다

# 듀티비는 0.0 ~ 1.0 (RPi.GPIO 의 0.0~100.0 을 100으로 나눈 값)
led.value = 0.5   # 50%

try:
    print(f"PWM 주파수: {led.frequency}Hz, 듀티비: {led.value*100:.1f}%")
    while True:
        time.sleep(0.1)

except KeyboardInterrupt:
    print("except KeyboardInterrupt")

finally:
    led.off()     # pwm 멈춤
    led.close()
