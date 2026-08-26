import cv2

# URL을 이용하여 OpenCV 이미지 만들기
def getUrlImage(url):
    import numpy as np
    import requests

    # url로 이미지 요청하고 OpenCV용 numpy array로 저장
    image_array = bytearray(requests.get(url).content) 
    image_nparray = np.asarray(image_array, dtype=np.uint8)
    image = cv2.imdecode(image_nparray, cv2.IMREAD_COLOR)
    print('이미지: ', url)
    print('이미지 원본크기:', image.shape)

    # 영상 사이즈 변경
    image = cv2.resize(image, (0,0), None, .3, .3)  # 원본크기의 30% 크기로 변환

    return image


# 함수 호출하기
url = 'https://movie-phinf.pstatic.net/20201229_146/1609226288425JgdsP_JPEG/movie_image.jpg'
image = getUrlImage(url)


# 영상 화면에 출력하기
cv2.imshow('url image', image)
cv2.waitKey(0)
cv2.destroyAllWindows()