# day2-led-button-toggle.py
# 버튼을 누를 때마다 LED ON/OFF 토글하기 (gpiozero)
# 버튼이 풀업 방식인지 풀다운 방식인지 자동으로 감지한다.
#
# 배선: 버튼 GPIO4  <-> GND 또는 3.3V (아래에서 자동 감지)
#      LED  GPIO17 -- 저항 -- LED -- GND

from gpiozero import LED, Button, DigitalInputDevice
import time

LED_PIN = 17
BUTTON_PIN = 4

led = LED(LED_PIN)
led.off()


# --------------------------------
# 버튼의 평상시 상태 자동 감지
# --------------------------------
def detect_button_mode(pin):
    """내부 풀 저항을 끈 상태(floating)로 핀을 읽어 평상시 상태를 알아낸다."""

    # pull_up=None 이면 내부 풀 저항을 사용하지 않고 핀 상태를 그대로 읽는다.
    probe = DigitalInputDevice(pin, pull_up=None, active_state=True)

    samples = []
    # 여러 번 측정하여 노이즈 영향 감소
    for _ in range(20):
        samples.append(probe.value)
        time.sleep(0.01)

    probe.close()  # Button 으로 다시 열기 위해 반드시 닫아준다

    # 가장 많이 측정된 값을 평상시 상태로 판단
    idle_state = 1 if sum(samples) > len(samples) / 2 else 0

    if idle_state == 1:
        print("버튼 방식 : Pull-Up")    # 평상시 HIGH, 누르면 LOW
        pull_up = True
    else:
        print("버튼 방식 : Pull-Down")  # 평상시 LOW, 누르면 HIGH
        pull_up = False

    return pull_up


pull_up = detect_button_mode(BUTTON_PIN)

# bounce_time: 채터링(떨림) 방지. RPi.GPIO 로 직접 짜던 디바운스를 대신한다.
button = Button(BUTTON_PIN, pull_up=pull_up, bounce_time=0.03)


def toggle_led():
    """버튼이 눌릴 때마다 호출된다."""
    led.toggle()                                    # LED 상태 반전
    print("LED :", "ON" if led.is_lit else "OFF")


# 버튼이 눌리는 순간 한 번만 toggle_led() 실행
button.when_pressed = toggle_led

try:
    print("버튼을 누르면 LED가 ON/OFF 됩니다.  (종료: Ctrl + C)")
    while True:
        time.sleep(0.1)

except KeyboardInterrupt:
    print("\n프로그램 종료")

finally:
    led.close()
    button.close()
