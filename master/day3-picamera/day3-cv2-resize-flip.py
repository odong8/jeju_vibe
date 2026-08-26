# day3-cv2-resize-flip.py
# 이미지 크기 변환하고 상하 반전시켜서 저장하기
# (원본 코드는 없는 파일 '../../test.jpg' 를 읽어서 오류가 났으므로 실제 있는 파일로 바꿈)

import cv2
import sys

src_file = '../image/london.jpg'   # 720x540

img = cv2.imread(src_file)
if img is None:
    print(f'Image load failed! : {src_file}')
    sys.exit()

print('원본 크기:', img.shape)

# 이미지 크기 변환하기
src = cv2.resize(img, dsize=(320, 240), interpolation=cv2.INTER_AREA)

# 상하 반전시키기
dst = cv2.flip(src, 0)

# save image
cv2.imwrite('test2.jpg', dst)

dst = cv2.imread('test2.jpg')

cv2.imshow('img', img)
cv2.imshow('src', src)
cv2.imshow('dst', dst)

cv2.waitKey()
cv2.destroyAllWindows()
