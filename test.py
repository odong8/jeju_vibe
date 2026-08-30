import cv2
import numpy as np
import time
import threading
from flask import Flask, render_template_string, Response, jsonify
import RPi.GPIO as GPIO
from picamera2 import Picamera2

# ==========================================
# 1. GPIO 핀 설정
# ==========================================
GPIO.setmode(GPIO.BCM)

PIN_TRIG = 23
PIN_ECHO = 24
PIN_LED_GREEN = 17  # 경고등 LED
PIN_BUZZER = 18     # 2핀 부저 (+)
PIN_SERVO = 25      # 허수아비 구동 서보모터

GPIO.setwarnings(False)

GPIO.setup(PIN_TRIG, GPIO.OUT)
GPIO.setup(PIN_ECHO, GPIO.IN)
GPIO.setup(PIN_LED_GREEN, GPIO.OUT)
GPIO.setup(PIN_BUZZER, GPIO.OUT)
GPIO.setup(PIN_SERVO, GPIO.OUT)

GPIO.output(PIN_LED_GREEN, GPIO.LOW)
GPIO.output(PIN_BUZZER, GPIO.LOW)

# 서보모터 PWM 초기화 (50Hz)
servo_pwm = GPIO.PWM(PIN_SERVO, 50)
servo_pwm.start(0)

# ==========================================
# 2. AI 모델 로딩 (MobileNet-SSD)
# ==========================================
PROTOTXT = "models/deploy.prototxt"
MODEL = "models/MobileNetSSD_deploy.caffemodel"
CONFIDENCE_THRESHOLD = 0.45  # 오인식 방지를 위해 0.45로 설정

CLASSES = ["background", "aeroplane", "bicycle", "bird", "boat",
           "bottle", "bus", "car", "cat", "chair", "cow", "diningtable",
           "dog", "horse", "motorbike", "person", "pottedplant", "sheep",
           "sofa", "train", "tvmonitor"]

# 퇴치 대상 동물 (조류, 고양이, 개)
ANIMAL_CLASSES = ["bird", "cat", "dog"]

print("[INFO] AI 야생 동물 및 사람 감지 모델 로딩 중...")
net = cv2.dnn.readNetFromCaffe(PROTOTXT, MODEL)
print("[INFO] AI 모델 로딩 완료!")

# ==========================================
# 3. 전역 공유 변수 및 카메라 설정
# ==========================================
app = Flask(__name__)

current_distance = 0.0
detected_object = "없음"
system_status = "🌿 안전 구역 (감시 중)"
last_alert_time = "-"
is_alerting = False

latest_raw_frame = None  # 원본 캡처 프레임
latest_processed_frame = None  # AI 결과 오버레이 프레임
frame_lock = threading.Lock()

picam2 = Picamera2()
picam2.configure(picam2.create_video_configuration(main={"size": (400, 300), "format": "RGB888"}))
picam2.start()

# ==========================================
# 4. 2핀 부저 PWM 및 서보모터 허수아비 제어 함수
# ==========================================
def beep_pwm(duration=0.1, freq=2700):
    try:
        pwm = GPIO.PWM(PIN_BUZZER, freq)
        pwm.start(50)
        time.sleep(duration)
        pwm.stop()
    except Exception:
        GPIO.output(PIN_BUZZER, GPIO.LOW)

def move_scarecrow():
    """허수아비를 좌우로 회전시키는 서보모터 구동 함수"""
    try:
        # 0도 -> 180도 -> 0도 왕복 동작 (DutyCycle: 2.5% ~ 12.5%)
        for _ in range(2):
            servo_pwm.ChangeDutyCycle(2.5)   # 0도 (좌측)
            time.sleep(0.25)
            servo_pwm.ChangeDutyCycle(12.5)  # 180도 (우측)
            time.sleep(0.25)
        
        servo_pwm.ChangeDutyCycle(7.5)   # 90도 (정면 원위치)
        time.sleep(0.2)
        servo_pwm.ChangeDutyCycle(0)     # 신호 차단 (서보 떨림 방지)
    except Exception as e:
        print(f"[SERVO ERROR] {e}")

def trigger_wildlife_deterrent():
    global is_alerting, last_alert_time
    if is_alerting:
        return

    def alert_thread():
        global is_alerting, last_alert_time
        is_alerting = True
        last_alert_time = time.strftime("%H:%M:%S")
        
        # 1. 서보모터 허수아비 회전 동작 (별도 스레드 동시 실행)
        threading.Thread(target=move_scarecrow, daemon=True).start()

        # 2. LED 및 부저 경고음 동시 작동
        for _ in range(3):
            GPIO.output(PIN_LED_GREEN, GPIO.HIGH)
            beep_pwm(0.1, 2700)
            GPIO.output(PIN_LED_GREEN, GPIO.LOW)
            time.sleep(0.05)
            
        GPIO.output(PIN_LED_GREEN, GPIO.HIGH)
        beep_pwm(0.4, 3000)
        GPIO.output(PIN_LED_GREEN, GPIO.LOW)
        
        time.sleep(0.5)
        is_alerting = False

    threading.Thread(target=alert_thread, daemon=True).start()

# ==========================================
# 5. 초고속 반응 초음파 센서 스레드
# ==========================================
def measure_single_distance():
    GPIO.output(PIN_TRIG, False)
    time.sleep(0.000002)
    GPIO.output(PIN_TRIG, True)
    time.sleep(0.000008)
    GPIO.output(PIN_TRIG, False)

    pulse_start = time.time()
    timeout = pulse_start + 0.015
    while GPIO.input(PIN_ECHO) == 0:
        pulse_start = time.time()
        if pulse_start > timeout:
            return None

    pulse_end = time.time()
    timeout = pulse_end + 0.015
    while GPIO.input(PIN_ECHO) == 1:
        pulse_end = time.time()
        if pulse_end > timeout:
            return None

    duration = pulse_end - pulse_start
    distance = (duration * 34300) / 2
    if 2.0 <= distance <= 300.0:
        return distance
    return None

def sensor_loop():
    global current_distance
    while True:
        samples = []
        for _ in range(3):
            d = measure_single_distance()
            if d is not None:
                samples.append(d)
            time.sleep(0.005)

        if samples:
            samples.sort()
            current_distance = round(samples[len(samples) // 2], 1)

        time.sleep(0.03)

threading.Thread(target=sensor_loop, daemon=True).start()

# ==========================================
# 6. 실시간 카메라 Capturing 스레드 (30 FPS 고속)
# ==========================================
def camera_capture_loop():
    global latest_raw_frame
    while True:
        frame = picam2.capture_array()
        # frame = cv2.flip(frame, -1)
        with frame_lock:
            latest_raw_frame = frame.copy()
        time.sleep(0.01)

threading.Thread(target=camera_capture_loop, daemon=True).start()

# ==========================================
# 7. 비동기 AI 추론 백그라운드 스레드 (사람 예외 처리 적용)
# ==========================================
def ai_inference_loop():
    global latest_processed_frame, detected_object, system_status

    while True:
        frame = None
        with frame_lock:
            if latest_raw_frame is not None:
                frame = latest_raw_frame.copy()

        if frame is not None:
            (h, w) = frame.shape[:2]
            blob = cv2.dnn.blobFromImage(cv2.resize(frame, (300, 300)), 0.007843, (300, 300), 127.5)
            net.setInput(blob)
            detections = net.forward()

            person_detected = False
            animal_detected = False
            detected_animal_name = ""
            curr_obj = "없음"

            for i in range(0, detections.shape[2]):
                confidence = detections[0, 0, i, 2]
                if confidence > CONFIDENCE_THRESHOLD:
                    idx = int(detections[0, 0, i, 1])
                    label_name = CLASSES[idx]

                    box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
                    (startX, startY, endX, endY) = box.astype("int")

                    # 1. 사람 감지 시 (주황색 박스 & 경보/허수아비 차단 플래그 설정)
                    if label_name == "person":
                        person_detected = True
                        color = (255, 165, 0)
                        cv2.rectangle(frame, (startX, startY), (endX, endY), color, 2)
                        cv2.putText(frame, f"Person: {confidence*100:.0f}%", (startX, startY - 10),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
                        curr_obj = f"person ({confidence * 100:.0f}%)"

                    # 2. 동물 감지 시 (빨간색 박스)
                    elif label_name in ANIMAL_CLASSES:
                        animal_detected = True
                        detected_animal_name = label_name
                        color = (0, 0, 255)
                        cv2.rectangle(frame, (startX, startY), (endX, endY), color, 2)
                        cv2.putText(frame, f"{label_name}: {confidence*100:.0f}%", (startX, startY - 10),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
                        curr_obj = f"{label_name} ({confidence * 100:.0f}%)"

                    # 3. 기타 일반 사물 (초록색 박스)
                    else:
                        color = (0, 255, 0)
                        cv2.rectangle(frame, (startX, startY), (endX, endY), color, 2)
                        cv2.putText(frame, f"{label_name}: {confidence*100:.0f}%", (startX, startY - 10),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
                        curr_obj = f"{label_name} ({confidence * 100:.0f}%)"

            detected_object = curr_obj

            # --- 경보 및 허수아비 제어 핵심 로직 ---
            # 1. 사람이 카메라 화면에 감지되면 무조건 경보/허수아비 작동 차단 (사람 보호)
            if person_detected:
                system_status = "👤 사람 감지됨 (안전)"
            
            # 2. 사람이 없고, 30cm 이내에 동물이 다가온 경우 3단 퇴치 작동 (LED + 부저 + 허수아비)
            elif animal_detected and current_distance <= 30.0:
                system_status = f"🚨 경보! 유해 동물 [{detected_animal_name}] 접근 탐지 (허수아비&사이렌 작동)"
                trigger_wildlife_deterrent()

            # 3. 그 외 기본 상태
            else:
                if current_distance <= 30.0:
                    system_status = "⚠️ 물체/사람 접근 중 (감시 중...)"
                else:
                    system_status = "🌿 안전 구역 (동물 감시 중)"

            ret, buffer = cv2.imencode('.jpg', frame)
            if ret:
                latest_processed_frame = buffer.tobytes()

        time.sleep(0.03)

threading.Thread(target=ai_inference_loop, daemon=True).start()

def generate_frames():
    while True:
        if latest_processed_frame is not None:
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + latest_processed_frame + b'\r\n')
        time.sleep(0.03)

# ==========================================
# 8. Flask 웹 모니터링 대시보드
# ==========================================
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI 스마트 생태 감시 대시보드</title>
    <style>
        body { font-family: 'Noto Sans KR', sans-serif; background-color: #121824; color: white; margin: 0; padding: 20px; text-align: center; }
        .container { max-width: 900px; margin: 0 auto; background: #1c2333; padding: 20px; border-radius: 12px; box-shadow: 0 4px 20px rgba(0,0,0,0.6); }
        h1 { color: #2ecc71; margin-bottom: 5px; }
        p.subtitle { color: #8a99ad; font-size: 14px; margin-bottom: 20px; }
        .main-content { display: flex; flex-wrap: wrap; gap: 20px; justify-content: center; }
        .video-box { flex: 1.2; min-width: 320px; background: #000; border-radius: 8px; overflow: hidden; border: 2px solid #2c3a4e; }
        .video-box img { width: 100%; height: auto; display: block; }
        .status-box { flex: 1; min-width: 280px; text-align: left; display: flex; flex-direction: column; gap: 15px; }
        .card { background: #263248; padding: 15px; border-radius: 8px; border-left: 5px solid #2ecc71; }
        .card.alert { border-left-color: #e74c3c; background: #342329; }
        .card h3 { margin: 0 0 8px 0; font-size: 14px; color: #a0aec0; }
        .card p { margin: 0; font-size: 20px; font-weight: bold; color: #ffffff; }
        .btn-group { display: flex; gap: 10px; margin-top: 15px; }
        button { flex: 1; padding: 12px; font-size: 14px; font-weight: bold; color: white; background: #27ae60; border: none; border-radius: 6px; cursor: pointer; }
        button:hover { background: #2ecc71; }
        button.btn-buzzer { background: #e67e22; }
        button.btn-buzzer:hover { background: #f39c12; }
        button.btn-servo { background: #2980b9; }
        button.btn-servo:hover { background: #3498db; }
    </style>
    <script>
        function updateStatus() {
            fetch('/api/status')
                .then(response => response.json())
                .then(data => {
                    document.getElementById('dist').innerText = data.distance + ' cm';
                    document.getElementById('obj').innerText = data.object;
                    document.getElementById('status').innerText = data.status;
                    document.getElementById('time').innerText = data.last_time || '-';
                });
        }
        setInterval(updateStatus, 100);

        function triggerLed() { fetch('/api/control/led'); }
        function triggerBuzzer() { fetch('/api/control/buzzer'); }
        function triggerScarecrow() { fetch('/api/control/scarecrow'); }
    </script>
</head>
<body>
    <div class="container">
        <h1>🌿 AI 스마트 생태 감시 및 유해 동물 퇴치 시스템</h1>
        <p class="subtitle">제주 SW미래채움 - 라즈베리파이 AI 융합 프로젝트</p>
        <div class="main-content">
            <div class="video-box">
                <img src="{{ url_for('video_feed') }}" alt="생태 실시간 스트리밍">
            </div>
            <div class="status-box">
                <div class="card">
                    <h3>📏 접근 동물/물체 거리</h3>
                    <p id="dist">0 cm</p>
                </div>
                <div class="card">
                    <h3>🔍 AI 생물/객체 분류</h3>
                    <p id="obj">분석 중...</p>
                </div>
                <div class="card alert">
                    <h3>🚨 생태 감시 및 퇴치 상태</h3>
                    <p id="status">감시 중...</p>
                    <small style="color:#8a99ad;">최근 퇴치 작동 시간: <span id="time">-</span></small>
                </div>
                <div class="btn-group">
                    <button onclick="triggerLed()">🟢 경고등</button>
                    <button class="btn-buzzer" onclick="triggerBuzzer()">🔔 사이렌</button>
                    <button class="btn-servo" onclick="triggerScarecrow()">🤖 허수아비</button>
                </div>
            </div>
        </div>
    </div>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/api/status')
def api_status():
    return jsonify({
        'distance': current_distance,
        'object': detected_object,
        'status': system_status,
        'last_time': last_alert_time
    })

@app.route('/api/control/led')
def control_led():
    trigger_wildlife_deterrent()
    return jsonify({'result': 'success'})

@app.route('/api/control/buzzer')
def control_buzzer():
    beep_pwm(0.2, 2700)
    return jsonify({'result': 'success'})

@app.route('/api/control/scarecrow')
def control_scarecrow():
    threading.Thread(target=move_scarecrow, daemon=True).start()
    return jsonify({'result': 'success'})

if __name__ == '__main__':
    try:
        print("[INFO] AI 야생 동물 감시 고속 웹 서버 시작: [http://0.0.0.0:5000](http://0.0.0.0:5000)")
        app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)
    finally:
        servo_pwm.stop()
        picam2.stop()
        GPIO.cleanup()
