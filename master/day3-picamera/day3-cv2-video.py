import sys
import cv2

cap = cv2.VideoCapture('../video/video.mp4') # 비디오 열기

if not cap.isOpened():
    print("Video open failed!")
    sys.exit()

# 동영상 프레임 정보 출력
fps = round(cap.get(cv2.CAP_PROP_FPS))
print(f'동영상 초당 프레임수: {fps}')

while True:     # 카메라 프레임 처리
    ret, frame = cap.read()

    if not ret:
        break

    cv2.imshow('frame', frame)

    if cv2.waitKey(10) == 27:  # ESC 키가 눌려지면
        break

cap.release()
cv2.destroyAllWindows()