import RPi.GPIO as GPIO
import time

LED_PIN = 17
BUTTON_PIN = 4

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

GPIO.setup(LED_PIN, GPIO.OUT)

# 외부 풀업/풀다운 회로를 사용한다고 가정
GPIO.setup(BUTTON_PIN, GPIO.IN)

GPIO.output(LED_PIN, GPIO.LOW)


# --------------------------------
# 버튼의 평상시 상태 자동 감지
# --------------------------------
def detect_button_mode():

    samples = []

    # 여러 번 측정하여 노이즈 영향 감소
    for _ in range(20):
        samples.append(GPIO.input(BUTTON_PIN))
        time.sleep(0.01)

    # 가장 많이 측정된 값을 평상시 상태로 판단
    idle_state = 1 if sum(samples) > len(samples) / 2 else 0

    if idle_state == GPIO.HIGH:
        print("버튼 방식 : Pull-Up")
        pressed_state = GPIO.LOW

    else:
        print("버튼 방식 : Pull-Down")
        pressed_state = GPIO.HIGH

    return idle_state, pressed_state


idle_state, pressed_state = detect_button_mode()

led_on = False


try:
    print("버튼을 누르면 LED가 ON/OFF 됩니다.")

    while True:

        # 버튼이 눌린 상태인지 확인
        if GPIO.input(BUTTON_PIN) == pressed_state:

            # Debounce
            time.sleep(0.03)

            # 실제 버튼 입력인지 다시 확인
            if GPIO.input(BUTTON_PIN) == pressed_state:

                # LED 상태 반전
                led_on = not led_on

                GPIO.output(LED_PIN, led_on)

                print("LED :", "ON" if led_on else "OFF")

                # 버튼에서 손을 뗄 때까지 기다림
                while GPIO.input(BUTTON_PIN) == pressed_state:
                    time.sleep(0.01)

        time.sleep(0.01)


except KeyboardInterrupt:
    print("\n프로그램 종료")

finally:
    GPIO.cleanup()