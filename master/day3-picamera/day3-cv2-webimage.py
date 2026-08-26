import cv2
import numpy as np
import requests

url = 'https://movie-phinf.pstatic.net/20201229_146/1609226288425JgdsP_JPEG/movie_image.jpg'
# url = 'https://movie-phinf.pstatic.net/20220929_135/1664441921246ae2RC_JPEG/movie_image.jpg'

# url로 이미지 요청하고 결과 array로 저장
image_array = bytearray(requests.get(url).content) 

# numpy array로 변환
image_nparray = np.asarray(image_array, dtype=np.uint8)

# OpenCV이미지로  decoding
image = cv2.imdecode(image_nparray, cv2.IMREAD_COLOR)
print('이미지 원본크기:', image.shape)

# 영상 사이즈 변경
# image = cv2.resize(image, (640,480), None)    # (640,480)의 고정크기
image = cv2.resize(image, (0,0), None, .3, .3)  # 원본크기의 30% 크기로 변환

# 영상 화면에 출력하기
cv2.imshow('url image', image)
cv2.waitKey(0)
cv2.destroyAllWindows()