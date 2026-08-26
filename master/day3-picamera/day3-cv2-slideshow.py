import cv2

# 1.특정 이미지 파일을 모두 imgFiles 리스트에 추가
imgFiles = ['../image/picture1.png',
            '../image/picture2.png',
            '../image/picture3.png',
            '../image/picture4.png',
            '../image/picture5.png']

# 2.전체 화면으로 'image' 창 생성
cv2.namedWindow('image', cv2.WINDOW_NORMAL)
cv2.setWindowProperty('image', cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

# 3.1초간격으로 이미지 슬라이드 쇼(ESC키 입력할 때까지 무한루프)
cnt = len(imgFiles)
idx = 0
while True:
#     img = cv2.imread(imgFiles[idx])
    img = cv2.imread(imgFiles[idx])
    cv2.imshow('image', img)
    
    key = cv2.waitKey(1000)
    if key == 27: break

    idx += 1
    if idx >= cnt: idx = 0

cv2.destroyAllWindows()