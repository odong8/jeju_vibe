picam2 = Picamera2()
picam2.configure(picam2.create_video_configuration(main={"size": (320, 240), "format": "RGB888"}))
picam2.start()



# 프레임 읽어오는 함수 내부 (cap.read() 대신 사용)
# ret, frame = cap.read()  <-- 기존
frame = picam2.capture_array() # <-- 변경
frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)




