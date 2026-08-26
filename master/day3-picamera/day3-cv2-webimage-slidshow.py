import cv2

# URL을 이용하여 OpenCV 이미지 만들기
def getUrlImage(url):
    import numpy as np
    import requests
    
    # url로 이미지 요청하고 결과 array로 저장
    image_array = bytearray(requests.get(url).content) 
    image_nparray = np.asarray(image_array, dtype=np.uint8)
    image = cv2.imdecode(image_nparray, cv2.IMREAD_COLOR)
    print('이미지: ', url)
    print('이미지 원본크기:', image.shape)

    # 영상 사이즈 변경
    image = cv2.resize(image, (0,0), None, .3, .3)  # 원본크기의 30% 크기로 변환

    return image


# imgURL 목록
imgURL = ['https://movie-phinf.pstatic.net/20201229_146/1609226288425JgdsP_JPEG/movie_image.jpg',
          'https://movie-phinf.pstatic.net/20180724_290/1532393574542TGIna_JPEG/movie_image.jpg',
          'https://movie-phinf.pstatic.net/20111223_166/1324619308419RAp5L_JPEG/movie_image.jpg',
          'https://movie-phinf.pstatic.net/20111222_233/1324486884038nu8Xk_JPEG/movie_image.jpg',
          'https://movie-phinf.pstatic.net/20141113_224/1415868769500d1UGq_JPEG/movie_image.jpg']

# image 가져와 메모리에 저장하기
# URL의 개수가 많아지면 저장 시간이 오래 걸릴 수 있다.
imgFiles = []
for url in imgURL:
    imgFiles.append( getUrlImage(url) )

    
# 1초간격으로 이미지 슬라이드 쇼(ESC키 입력할 때까지 무한루프)
cnt = len(imgFiles)
idx = 0
while True:
    img =imgFiles[idx]
    cv2.imshow('image', img)
    
    key = cv2.waitKey(1000) # 1000=1초
    if key == 27: break

    # 이미지를 차례대로 불러오기
    idx += 1
    if idx >= cnt: idx = 0

cv2.destroyAllWindows()