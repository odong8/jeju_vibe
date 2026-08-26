import numpy as np
import cv2
import matplotlib.pyplot as plt

# 컬러 영상 & 그레이스케일 영상 불러오기
img1 = cv2.imread('../image/cat.jpg', cv2.IMREAD_COLOR) 
print(img1.shape)
# img1 = cv2.resize(img1, (0,0), None, .5, .5) # 컬러영상 사이즈변경
img2 = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)  # 컬러영상--흑백영상으로 변환
img2_3channel = cv2.cvtColor(img2, cv2.COLOR_GRAY2BGR) #흑백영상을 3채널(컬러채널)로 변경


# h_image = np.concatenate((img1, img2_3channel), axis=1)
h_image = np.hstack((img1, img2_3channel)) # 가로로 붙이기
v_image = np.vstack((img1, img2_3channel)) # 세로로 붙이기

cv2.imshow('Horizontal Image', h_image)# 이미지 띄우기
cv2.imshow('Vertical Image', v_image)

cv2.waitKey()             
cv2.destroyAllWindows()