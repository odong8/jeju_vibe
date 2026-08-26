#!/bin/bash
# 사진 한 장 찍어서 저장하기 (예전 libcamera-still 이름 버전)
#
# [Trixie 안내]
#   libcamera-still / libcamera-hello 등의 명령은 rpicam-still / rpicam-hello 로 이름이 바뀌었다.
#   Bookworm 까지는 libcamera-* 가 심볼릭 링크로 남아 있었지만 Trixie 에서는 제거되었다.
#   아래는 둘 중 있는 명령을 찾아서 사용한다.

DATE=$(date +"%Y-%m-%d_%H%M")
SAVE_DIR=/home/pi/master/autocamera

mkdir -p "$SAVE_DIR"

if command -v libcamera-still >/dev/null 2>&1; then
    STILL_CMD=libcamera-still
else
    STILL_CMD=rpicam-still
fi

echo "사용 명령: $STILL_CMD"
$STILL_CMD --nopreview --width 1280 --height 720 -o "$SAVE_DIR/$DATE.jpg"
