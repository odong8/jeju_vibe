import cv2
import numpy as np
import time
import threading
from flask import Flask, render_template_string, Response, jsonify
import RPi.GPIO as GPIO
from picamera2 import Picamera2

# ==========================================
# 1. GPIO 핀 설정 (모듈 직접 연결)
# ==========================================
PIN_TRIG = 23
PIN_ECHO = 24
PIN_LED_GREEN = 17  # LED 모듈 'IN' 핀
PIN_BUZZER = 18     # 부저 모듈 'S' 핀

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

GPIO.setup(PIN_TRIG, GPIO.OUT)
GPIO.setup(PIN_ECHO, GPIO.IN)
GPIO.setup(PIN_LED_GREEN, GPIO.OUT)
GPIO.setup(PIN_BUZZER, GPIO.OUT)

GPIO.output(PIN_LED_GREEN, GPIO.LOW)
GPIO.output(PIN_BUZZER, GPIO.LOW)

# ==========================================
# 2. AI 모델 로딩 (MobileNet-SSD)
# ==========================================
PROTOTXT = "models/deploy.prototxt"
MODEL = "models/MobileNetSSD_deploy.caffemodel"
CONFIDENCE_THRESHOLD = 0.5

CLASSES = ["background", "aeroplane", "bicycle", "bird", "boat",
           "bottle", "bus", "car", "cat", "chair", "cow", "diningtable",
           "dog", "horse", "motorbike", "person", "pottedplant", "sheep",
           "sofa", "train", "tvmonitor"]

TARGET_CLASSES = ["bottle", "chair", "person"]  # 인식 대상

print("[INFO] AI 모델 로딩 중...")
net = cv2.dnn.readNetFromCaffe(PROTOTXT, MODEL)
print("[INFO] AI 모델 로딩 완료!")

# ==========================================
# 3. 전역 변수 및 카메라 초기화 (Picamera2)
# ==========================================
app = Flask(__name__)

current_distance = 0.0
detected_object = "없음"
ai_status = "대기 중..."
last_detected_time = ""
is_alerting = False  # 알림 중복 실행 방지 플래그

# Picamera2 초기화 및 설정
picam2 = Picamera2()
picam2.configure(picam2.create_video_configuration(main={"size": (320, 240), "format": "RGB888"}))
picam2.start()

# ==========================================
# 4. 부저 & LED 모듈 제어 함수 (중복 호출 방지 적용)
# ==========================================
def beep(duration=0.1):
    GPIO.output(PIN_BUZZER, GPIO.HIGH)
    time.sleep(duration)
    GPIO.output(PIN_BUZZER, GPIO.LOW)

def trigger_success_alert():
    global is_alerting
    if is_alerting:
        return  # 이미 알림이 울리는 중이면 추가 실행 안 함

    def alert_thread():
        global is_alerting
        is_alerting = True
        GPIO.output(PIN_LED_GREEN, GPIO.HIGH)
        beep(0.1)
        time.sleep(0.1)
        beep(0.1)
        time.sleep(1.0)
        GPIO.output(PIN_LED_GREEN, GPIO.LOW)
        time.sleep(1.0)  # 알림 후 1초간 쿨타임 부여
        is_alerting = False

    threading.Thread(target=alert_thread, daemon=True).start()

# ==========================================
# 5. 초음파 센서 모듈 측정 스레드 (오류 수정 완결판)
# ==========================================
def sensor_loop():
    global current_distance
    while True:
        try:
            # Trig 신호 전송 (10us High)
            GPIO.output(PIN_TRIG, False)
            time.sleep(0.000002)
            GPIO.output(PIN_TRIG, True)
            time.sleep(0.00001)
            GPIO.output(PIN_TRIG, False)

            # Echo 핀 1(High) 전환 대기
            pulse_start = time.time()
            timeout_start = pulse_start + 0.03
            while GPIO.input(PIN_ECHO) == 0:
                pulse_start = time.time()
                if pulse_start > timeout_start:
                    break

            # Echo 핀 0(Low) 전환 대기
            pulse_end = time.time()
            timeout_end = pulse_end + 0.03
            while GPIO.input(PIN_ECHO) == 1:
                pulse_end = time.time()
                if pulse_end > timeout_end:
                    break

            # 정상적으로 pulse 신호가 수신된 경우에만 거리 측정
            if pulse_end > pulse_start and (pulse_end - pulse_start) < 0.03:
                duration = pulse_end - pulse_start
                dist = (duration * 34300) / 2
                # HC-SR04 유효 거리범위 (2cm ~ 300cm)
                if 2.0 <= dist <= 300.0:
                    current_distance = round(dist, 1)

            time.sleep(0.15)
        except Exception:
            time.sleep(0.5)

threading.Thread(target=sensor_loop, daemon=True).start()

# ==========================================
# 6. AI 영상 처리 및 스트리밍 루프
# ==========================================
def generate_frames():
    global detected_object, ai_status, last_detected_time
    frame_count = 0

    while True:
        frame = picam2.capture_array()
        frame = cv2.flip(frame, -1)  # 상하좌우 반전 필요 시 조절

        frame_count += 1

        if frame_count % 2 == 0:
            (h, w) = frame.shape[:2]
            blob = cv2.dnn.blobFromImage(cv2.resize(frame, (300, 300)), 0.007843, (300, 300), 127.5)
            net.setInput(blob)
            detections = net.forward()

            found_target = False

            for i in range(0, detections.shape[2]):
                confidence = detections[0, 0, i, 2]

                if confidence > CONFIDENCE_THRESHOLD:
                    idx = int(detections[0, 0, i, 1])
                    label_name = CLASSES[idx]

                    box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
                    (startX, startY, endX, endY) = box.astype("int")

                    cv2.rectangle(frame, (startX, startY), (endX, endY), (0, 255, 0), 2)
                    text = f"{label_name}: {confidence * 100:.1f}%"
                    cv2.putText(frame, text, (startX, startY - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

                    detected_object = f"{label_name} ({confidence * 100:.0f}%)"

                    # 물체가 20cm 이내 접근하고 AI 대상일 경우 동작
                    if current_distance <= 20.0 and label_name in TARGET_CLASSES:
                        found_target = True
                        ai_status = f"✅ {label_name} 인식 성공!"
                        last_detected_time = time.strftime("%H:%M:%S")
                        trigger_success_alert()

            if not found_target:
                if current_distance <= 20.0:
                    ai_status = "⚠️ 물체 감지됨 (분석 중...)"
                else:
                    ai_status = "대기 중 (용기를 다가오게 하세요)"
                    detected_object = "없음"

        ret, buffer = cv2.imencode('.jpg', frame)
        frame_bytes = buffer.tobytes()

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

# ==========================================
# 7. Flask 웹 대시보드
# ==========================================
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI 스마트 재활용 모니터링</title>
    <style>
        body { font-family: 'Noto Sans KR', sans-serif; background-color: #f4f7f6; margin: 0; padding: 20px; text-align: center; }
        .container { max-width: 900px; margin: 0 auto; background: white; padding: 20px; border-radius: 12px; box-shadow: 0 4px 15px rgba(0,0,0,0.1); }
        h1 { color: #2c3e50; margin-bottom: 5px; }
        p.subtitle { color: #7f8c8d; font-size: 14px; margin-bottom: 20px; }
        .main-content { display: flex; flex-wrap: wrap; gap: 20px; justify-content: center; }
        .video-box { flex: 1; min-width: 300px; background: #000; border-radius: 8px; overflow: hidden; }
        .video-box img { width: 100%; height: auto; display: block; }
        .status-box { flex: 1; min-width: 280px; text-align: left; display: flex; flex-direction: column; gap: 15px; }
        .card { background: #eef2f5; padding: 15px; border-radius: 8px; border-left: 5px solid #3498db; }
        .card.success { border-left-color: #2ecc71; background: #e8f8f5; }
        .card h3 { margin: 0 0 8px 0; font-size: 14px; color: #555; }
        .card p { margin: 0; font-size: 20px; font-weight: bold; color: #2c3e50; }
        .btn-group { display: flex; gap: 10px; margin-top: 15px; }
        button { flex: 1; padding: 12px; font-size: 14px; font-weight: bold; color: white; background: #3498db; border: none; border-radius: 6px; cursor: pointer; }
        button:hover { background: #2980b9; }
        button.btn-buzzer { background: #e67e22; }
        button.btn-buzzer:hover { background: #d35400; }
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
        setInterval(updateStatus, 500);

        function triggerLed() { fetch('/api/control/led'); }
        function triggerBuzzer() { fetch('/api/control/buzzer'); }
    </script>
</head>
<body>
    <div class="container">
        <h1>♻️ AI 스마트 재활용 모니터링</h1>
        <p class="subtitle">제주 SW미래채움 - 라즈베리파이 AI 융합 프로젝트</p>
        <div class="main-content">
            <div class="video-box">
                <img src="{{ url_for('video_feed') }}" alt="AI 카메라 실시간 스트리밍">
            </div>
            <div class="status-box">
                <div class="card">
                    <h3>📏 초음파 센서 거리</h3>
                    <p id="dist">0 cm</p>
                </div>
                <div class="card">
                    <h3>🔍 AI 인식 사물</h3>
                    <p id="obj">분석 중...</p>
                </div>
                <div class="card success">
                    <h3>💡 AI 처리 상태</h3>
                    <p id="status">대기 중...</p>
                    <small style="color:#7f8c8d;">최근 인식 시간: <span id="time">-</span></small>
                </div>
                <div class="btn-group">
                    <button onclick="triggerLed()">🟢 LED 모듈 테스트</button>
                    <button class="btn-buzzer" onclick="triggerBuzzer()">🔔 부저 모듈 테스트</button>
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
        'status': ai_status,
        'last_time': last_detected_time
    })

@app.route('/api/control/led')
def control_led():
    trigger_success_alert()
    return jsonify({'result': 'success'})

@app.route('/api/control/buzzer')
def control_buzzer():
    beep(0.2)
    return jsonify({'result': 'success'})

if __name__ == '__main__':
    try:
        print("[INFO] 웹 서버 시작: http://0.0.0.0:5000")
        app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)
    finally:
        picam2.stop()
        GPIO.cleanup()


---

## 3. 하드웨어 현장 점검 체크리스트 (수정 후 점검)

1. **초음파 센서 VCC 핀 전원 확인**
   - 초음파 센서 모듈의 **VCC 핀이 반드시 라즈베리파이 Pin 2번(5V)**에 연결되어 있는지 확인합니다. (3.3V에 꽂히면 초음파가 발사되지 않아 0.4cm로 고정됩니다.)
2. **Trig / Echo 핀 교차 점검**
   - **Trig ➡️ Pin 16 (BCM 23)**
   - **Echo ➡️ Pin 18 (BCM 24)** (두 핀이 반대로 꽂히면 수치가 변하지 않습니다.)
```eof

### 🛠️ 하드웨어 필수 체크 포인트
1. 초음파 센서의 **VCC 핀이 라즈베리파이 2번 핀(5V)**에 꽂혀 있는지 꼭 확인하세요. (1번 핀 3.3V에 꽂으면 0.4cm만 나옵니다.)
2. 실행 시 `python3 app.py`를 실행하신 후 웹 페이지(`http://localhost:5000`) 접속 시 웹 버튼 **[🔔 부저 모듈 테스트]**를 클릭했을 때 소리가 정상적으로 나는지 확인하세요.

추가로 작동 과정에서 막히는 점이 있으시면 알려주세요!
