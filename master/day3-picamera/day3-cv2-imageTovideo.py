# day3-cv2-imageTovideo.py
# 폴더 안의 이미지 파일들을 모아서 하나의 동영상 파일로 만들기

import cv2
import time
import os
import re
import sys


def get_files(path):  # 해당 폴더 위치의 파일 목록 만들기 (파일명 오름차순 정렬)
    list_files = []

    if not os.path.exists(path):
        print(f'경로가 존재하지 않습니다: {path}')
        return list_files
    if not os.path.isdir(path):
        print(f'폴더가 아닙니다: {path}')
        return list_files
    if not os.access(path, os.R_OK):
        print(f'폴더 읽기 권한이 없습니다: {path}')
        return list_files

    # 이미지 확장자만 골라내기
    exts = ('.jpg', '.jpeg', '.png', '.bmp')

    # os.walk()를 사용하여 하위 폴더까지 포함한 모든 파일 목록을 가져오기
    # os.walk()는 (root, subdirs, files) 형태의 튜플 반환
    for root, subdirs, files in os.walk(path):
        if len(files) > 0:
            for f in files:
                if f.lower().endswith(exts):
                    fullpath = root + '/' + f
                    list_files.append(fullpath)

    # 파일명 기준 정렬 (숫자가 포함된 이름도 자연스럽게 정렬)
    list_files.sort(key=lambda x: os.path.basename(x))
    return list_files


def check_date_format(txt):
    """파일명에서 날짜를 찾아 돌려준다. 없으면 빈 문자열."""

    # 1) 날짜와 시간까지 추출: YYYY-MM-DD_HH-MM 또는 YYYY-MM-DD_HH:MM
    m = re.search(r'\d{4}-\d{2}-\d{2}[ _]?\d{2}[-:]\d{2}', txt)
    if m:
        return m.group()

    # 2) 날짜만 추출: YYYY-MM-DD
    m = re.search(r'\d{4}-\d{2}-\d{2}', txt)
    if m:
        return m.group()

    return ''


#--------------------------
# Start
#--------------------------
# 1. (동영상으로 만들 이미지)파일 절대경로 목록 만들기
#    './picture' 는 autocamera 로 찍은 사진을 모아두는 폴더.
#    그 폴더가 없으면 예제용 '../image' 폴더를 사용한다.
img_dir = './picture' if os.path.isdir('./picture') else '../image'
print(f'이미지 폴더: {img_dir}')

image_files = get_files(img_dir)
print(f'파일 개수: {len(image_files)}')
# print(image_files)
print()

if len(image_files) == 0:
    print('이미지 파일이 없습니다.')
    sys.exit()

# 2.(동영상으로 만들 이미지)파일 크기 정보 얻기
img = cv2.imread(image_files[0])
if img is None:
    print(f'Image load failed! : {image_files[0]}')
    sys.exit()

height, width, channel = img.shape
fps = 25
print(f'동영상 크기: {width}x{height}, fps: {fps}')

# 3.저장할 동영상 정보 만들기
fourcc = cv2.VideoWriter_fourcc(*'mp4v')
BASE_DIR = os.getcwd()  # BASE_DIR = os.path.dirname(os.path.abspath(__file__))
out_file = BASE_DIR + '/' + 'output.mp4'
writer = cv2.VideoWriter(out_file, fourcc, fps, (width, height))


# 4.이미지 파일을 동영상으로 만들기
for file in image_files:
    img = cv2.imread(file)    # 이미지 파일 읽기
    if img is None:
        print(f'건너뜀(읽기 실패): {file}')
        continue

    # 이미지마다 크기가 다르면 동영상에 들어가지 않으므로 첫 번째 크기로 맞춰준다.
    if img.shape[0] != height or img.shape[1] != width:
        img = cv2.resize(img, (width, height))

    # 영상에 날짜 넣기
    text = check_date_format(file)
    cv2.putText(img, text, (10, 30), cv2.FONT_HERSHEY_DUPLEX, 1, (0, 0, 0), 2, cv2.LINE_AA)
    cv2.imshow("Color", img)  # 화면에 이미지 파일 보여주기

    writer.write(img)         # 동영상 객체에 이미지파일 추가하기

    if cv2.waitKey(25) == 27: # ESC키 누르면 중지
        break

print(f'finish!  ({out_file} 저장됨)')
writer.release()              # 동영상 객체 자원 회수
cv2.destroyAllWindows()       # 화면 중단하기
