#!/bin/bash
# 사진 촬영 + 성공 여부 확인 (Trixie: rpicam-still)

DATE=$(date +"%Y-%m-%d_%H%M")
SAVE_DIR=/home/pi/master/autocamera

# 저장 폴더를 "촬영하기 전에" 만든다
if [ ! -d "$SAVE_DIR" ]; then
    mkdir -p "$SAVE_DIR"
fi

rpicam-still --nopreview --width 1280 --height 720 -o "$SAVE_DIR/$DATE.jpg"

# Check if the image was captured successfully
if [ $? -eq 0 ]; then
    echo "Image captured successfully: $DATE.jpg"
else
    echo "Failed to capture image."
fi
