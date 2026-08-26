# day3-cv2-imwrite.py
# 컬러 영상을 흑백으로 읽어서 파일로 저장하기

import cv2
import sys

src_file = '../image/cat.jpg'
dst_file = '../image/cat_gray.jpg'

img = cv2.imread(src_file, cv2.IMREAD_GRAYSCALE)
if img is None:
    print(f'Image load failed! : {src_file}')
    sys.exit()

# cv2.imwrite() 는 저장 성공 여부를 True/False 로 돌려준다.
ok = cv2.imwrite(dst_file, img)

if not ok:
    print('Image save failed!')
    sys.exit()

print(f'{dst_file} 저장됨')

cv2.imshow('gray', img)
cv2.waitKey()
cv2.destroyAllWindows()
