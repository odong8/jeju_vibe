import cv2
import numpy as np
import time
import threading
from datetime import datetime, timedelta, timezone  # 한국 표준시(KST) 적용을 위한 모듈
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
PIN_BUZZER = 18     # 3핀 수동 부저 모듈 (I/O 또는 S 신호 핀)
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
CONFIDENCE_THRESHOLD = 0.45

CLASSES = ["background", "aeroplane", "bicycle", "bird", "boat",
           "bottle", "bus", "car", "cat", "chair", "cow", "diningtable",
           "dog", "horse", "motorbike", "person", "pottedplant", "sheep",
           "sofa", "train", "tvmonitor"]

# 퇴치 대상 동물 (조류, 고양이, 개, 말)
ANIMAL_CLASSES = ["bird", "cat", "dog", "horse"]

print("[INFO] AI 야생 동물 및 사람 감지 모델 로딩 중...")
net = cv2.dnn.readNetFromCaffe(PROTOTXT, MODEL)
print("[INFO] AI 모델 로딩 완료!")

# ==========================================
# 3. 전역 공유 변수, 시간 설정 및 카메라 초기화
# ==========================================
app = Flask(__name__)

# 한국 표준시 (KST = UTC+9) 고정 설정
KST = timezone(timedelta(hours=9))

def get_kst_now_str():
    """OS 시간 오차 방지를 위해 한국 표준시(KST)를 HH:MM:SS 규격으로 취득"""
    return datetime.now(KST).strftime("%H:%M:%S")

current_distance = 0.0
detected_object = "없음"
system_status = " 안전 구역 (감시 중)"
last_alert_time = "-"
is_alerting = False

# 위험 발동 내역 저장용 리스트 (최대 50개 저장)
event_logs = []

latest_raw_frame = None
latest_processed_frame = None
frame_lock = threading.Lock()

picam2 = Picamera2()
picam2.configure(picam2.create_video_configuration(main={"size": (400, 300), "format": "RGB888"}))
picam2.start()

# ==========================================
# 4. 3핀 수동 부저 PWM 및 서보모터 허수아비 제어 함수
# ==========================================
def beep_pwm(duration=0.1, freq=2700):
    """3핀 수동 부저 모듈 PWM 제어 함수"""
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
        for _ in range(2):
            servo_pwm.ChangeDutyCycle(2.5)   # 0도 (좌)
            time.sleep(0.25)
            servo_pwm.ChangeDutyCycle(12.5)  # 180도 (우)
            time.sleep(0.25)
        
        servo_pwm.ChangeDutyCycle(7.5)   # 90도 (정면 원위치)
        time.sleep(0.2)
        servo_pwm.ChangeDutyCycle(0)     # 모터 떨림/발열 방지
    except Exception as e:
        print(f"[SERVO ERROR] {e}")

def add_event_log(animal_name, dist):
    """KST 기반 정확한 시각을 로그 및 웹 대시보드에 기록"""
    global last_alert_time
    now_str = get_kst_now_str()
    last_alert_time = now_str
    
    log_entry = {
        "time": now_str,
        "animal": animal_name,
        "distance": dist
    }
    
    event_logs.insert(0, log_entry)  # 최신 로그를 맨 위에 추가
    if len(event_logs) > 50:
        event_logs.pop()

def trigger_wildlife_deterrent(animal_name="미상"):
    global is_alerting
    if is_alerting:
        return

    # 정확한 시간으로 이력 기록 추가
    add_event_log(animal_name, current_distance)

    def alert_thread():
        global is_alerting
        is_alerting = True
        
        # 1. 서보모터 허수아비 회전 (독립 스레드)
        threading.Thread(target=move_scarecrow, daemon=True).start()

        # 2. LED 및 3핀 수동 부저 사이렌 작동
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
# 5. 초음파 센서 스레드
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
# 6. 실시간 카메라 Capturing 스레드
# ==========================================
def camera_capture_loop():
    global latest_raw_frame
    while True:
        frame = picam2.capture_array()
        with frame_lock:
            latest_raw_frame = frame.copy()
        time.sleep(0.01)

threading.Thread(target=camera_capture_loop, daemon=True).start()

# ==========================================
# 7. 비동기 AI 추론 백그라운드 스레드
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

                    if label_name == "person":
                        person_detected = True
                        color = (255, 165, 0)
                        cv2.rectangle(frame, (startX, startY), (endX, endY), color, 2)
                        cv2.putText(frame, f"Person: {confidence*100:.0f}%", (startX, startY - 10),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
                        curr_obj = f"person ({confidence * 100:.0f}%)"

                    elif label_name in ANIMAL_CLASSES:
                        animal_detected = True
                        detected_animal_name = label_name
                        color = (0, 0, 255)
                        cv2.rectangle(frame, (startX, startY), (endX, endY), color, 2)
                        cv2.putText(frame, f"{label_name}: {confidence*100:.0f}%", (startX, startY - 10),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
                        curr_obj = f"{label_name} ({confidence * 100:.0f}%)"

                    else:
                        color = (0, 255, 0)
                        cv2.rectangle(frame, (startX, startY), (endX, endY), color, 2)
                        cv2.putText(frame, f"{label_name}: {confidence*100:.0f}%", (startX, startY - 10),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
                        curr_obj = f"{label_name} ({confidence * 100:.0f}%)"

            detected_object = curr_obj

            # 50.0cm 접근 거리 기준 및 안전 제어 로직
            if person_detected:
                system_status = " 사람 감지됨 (안전)"
            elif animal_detected and current_distance <= 50.0:
                system_status = f" 경보! 유해 동물 [{detected_animal_name}] 접근 탐지 (허수아비&사이렌 작동)"
                trigger_wildlife_deterrent(detected_animal_name)
            else:
                if current_distance <= 50.0:
                    system_status = "⚠️ 물체/사람 접근 중 (감시 중...)"
                else:
                    system_status = " 안전 구역 (동물 감시 중)"

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
# 8. Flask 웹 대시보드
# ==========================================
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>지능형 허수아비 철통 경계 시스템</title>
    <style>
        body { font-family: 'Noto Sans KR', sans-serif; background-color: #121824; color: white; margin: 0; padding: 20px; text-align: center; }
        .container { max-width: 950px; margin: 0 auto; background: #1c2333; padding: 20px; border-radius: 12px; box-shadow: 0 4px 20px rgba(0,0,0,0.6); }
        h1 { color: #2ecc71; margin-bottom: 5px; }
        p.subtitle { color: #8a99ad; font-size: 14px; margin-bottom: 20px; }
        .main-content { display: flex; flex-wrap: wrap; gap: 20px; justify-content: center; margin-bottom: 25px; }
        .video-box { flex: 1.2; min-width: 320px; background: #000; border-radius: 8px; overflow: hidden; border: 2px solid #2c3a4e; }
        .video-box img { width: 100%; height: auto; display: block; }
        .status-box { flex: 1; min-width: 280px; text-align: left; display: flex; flex-direction: column; gap: 12px; }
        .card { background: #263248; padding: 12px 15px; border-radius: 8px; border-left: 5px solid #2ecc71; }
        .card.alert { border-left-color: #e74c3c; background: #342329; }
        .card h3 { margin: 0 0 5px 0; font-size: 13px; color: #a0aec0; }
        .card p { margin: 0; font-size: 18px; font-weight: bold; color: #ffffff; }
        
        /* 기록 데이터 테이블 스타일 */
        .log-section { text-align: left; background: #263248; padding: 15px; border-radius: 8px; }
        .log-section h2 { margin-top: 0; font-size: 16px; color: #2ecc71; border-bottom: 1px solid #3a4b68; padding-bottom: 8px; }
        .table-wrapper { max-height: 180px; overflow-y: auto; }
        table { width: 100%; border-collapse: collapse; text-align: center; font-size: 13px; }
        th { background: #1c2333; color: #8a99ad; padding: 8px; position: sticky; top: 0; }
        td { padding: 8px; border-bottom: 1px solid #313e56; }
        .tag-animal { color: #e74c3c; font-weight: bold; }
        
        .btn-group { display: flex; gap: 10px; margin-top: 5px; }
        button { flex: 1; padding: 10px; font-size: 13px; font-weight: bold; color: white; background: #27ae60; border: none; border-radius: 6px; cursor: pointer; }
        button:hover { background: #2ecc71; }
        button.btn-buzzer { background: #e67e22; }
        button.btn-servo { background: #2980b9; }
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
                    
                    let logRows = '';
                    if (data.logs.length === 0) {
                        logRows = '<tr><td colspan="3">최근 위험 발동 기록이 없습니다.</td></tr>';
                    } else {
                        data.logs.forEach(log => {
                            logRows += `<tr>
                                <td>${log.time}</td>
                                <td><span class="tag-animal">${log.animal}</span></td>
                                <td>${log.distance} cm</td>
                            </tr>`;
                        });
                    }
                    document.getElementById('log-tbody').innerHTML = logRows;
                });
        }
        setInterval(updateStatus, 500);

        function triggerLed() { fetch('/api/control/led'); }
        function triggerBuzzer() { fetch('/api/control/buzzer'); }
        function triggerScarecrow() { fetch('/api/control/scarecrow'); }
    </script>
</head>
<body>
    <div class="container">
        <h1> 지능형 허수아비의 철통 경계 근무</h1>
        <p class="subtitle">AI 영상분석 & 초음파 복합 제어 실시간 대시보드</p>
        <div class="main-content">
            <div class="video-box">
                <img src="{{ url_for('video_feed') }}" alt="실시간 카메라 스트리밍">
            </div>
            <div class="status-box">
                <div class="card">
                    <h3> 접근 감지 거리 (기준: 50cm 이내)</h3>
                    <p id="dist">0 cm</p>
                </div>
                <div class="card">
                    <h3> AI 실시간 식별 객체</h3>
                    <p id="obj">분석 중...</p>
                </div>
                <div class="card alert">
                    <h3> 현재 시스템 동작 상태</h3>
                    <p id="status">감시 중...</p>
                    <small style="color:#8a99ad;">최근 퇴치 작동: <span id="time">-</span></small>
                </div>
                <div class="btn-group">
                    <button onclick="triggerLed()">🟢 경고등</button>
                    <button class="btn-buzzer" onclick="triggerBuzzer()">🔔 사이렌</button>
                    <button class="btn-servo" onclick="triggerScarecrow()">🤖 허수아비</button>
                </div>
            </div>
        </div>

        <div class="log-section">
            <h2> 실시간 위험 발동 및 유해 동물 감지 이력</h2>
            <div class="table-wrapper">
                <table>
                    <thead>
                        <tr>
                            <th>발동 시간</th>
                            <th>감지된 동물종</th>
                            <th>접근 거리</th>
                        </tr>
                    </thead>
                    <tbody id="log-tbody">
                        <tr><td colspan="3">데이터 로딩 중...</td></tr>
                    </tbody>
                </table>
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
        'last_time': last_alert_time,
        'logs': event_logs
    })

@app.route('/api/control/led')
def control_led():
    trigger_wildlife_deterrent("수동 제어")
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
        print("[INFO] 지능형 허수아비 경계 시스템 웹 서버 시작: http://0.0.0.0:5000")
        app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)
    finally:
        servo_pwm.stop()
        picam2.stop()
        GPIO.cleanup()