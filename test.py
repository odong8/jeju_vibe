import cv2
import numpy as np
import time
import threading
from flask import Flask, render_template_string, Response, jsonify
import RPi.GPIO as GPIO

# ==========================================
# 1. GPIO 핀 설정 (모듈 직접 연결)
# ==========================================
PIN_TRIG = 23
PIN_ECHO = 24
PIN_LED_GREEN = 17  # LED 모듈 'IN' 핀 연결
PIN_BUZZER = 18     # 부저 모듈 'S' 핀 연결

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
# 3. 전역 변수 및 카메라 초기화
# ==========================================
app = Flask(__name__)

current_distance = 0.0
detected_object = "없음"
ai_status = "대기 중..."
last_detected_time = ""

cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)

# ==========================================
# 4. 부저 & LED 모듈 제어 함수
# ==========================================
def beep(duration=0.1):
    GPIO.output(PIN_BUZZER, GPIO.HIGH)
    time.sleep(duration)
    GPIO.output(PIN_BUZZER, GPIO.LOW)

def trigger_success_alert():
    def alert_thread():
        GPIO.output(PIN_LED_GREEN, GPIO.HIGH)
        beep(0.1)
        time.sleep(0.1)
        beep(0.1)
        time.sleep(1.5)
        GPIO.output(PIN_LED_GREEN, GPIO.LOW)
    threading.Thread(target=alert_thread, daemon=True).start()

# ==========================================
# 5. 초음파 센서 모듈 측정 스레드
# ==========================================
def sensor_loop():
    global current_distance
    while True:
        try:
            GPIO.output(PIN_TRIG, True)
            time.sleep(0.00001)
            GPIO.output(PIN_TRIG, False)

            start_time = time.time()
            stop_time = time.time()

            timeout = start_time + 0.04
            while GPIO.input(PIN_ECHO) == 0:
                start_time = time.time()
                if start_time > timeout:
                    break

            while GPIO.input(PIN_ECHO) == 1:
                stop_time = time.time()
                if stop_time > timeout:
                    break

            elapsed = stop_time - start_time
            distance = (elapsed * 34300) / 2
            current_distance = round(distance, 1)
            time.sleep(0.2)
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
        success, frame = cap.read()
        if not success:
            break

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
# 7. Flask 웹 모니터링 페이지
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
        cap.release()
        GPIO.cleanup()
