import cv2
import sys

img = cv2.imread('../image/cat.jpg',cv2.IMREAD_COLOR) # 영상 파일 읽기(컬러)

if img is None:
    print('Image load failed!')
    sys.exit()

cv2.imshow('image', img)  #영상 출력하기
cv2.waitKey()             #키가 입력될 때까지 화면을 유지하기
cv2.destroyAllWindows()   #이벤트가 발생되면(키가 입력되면) 화면 닫기