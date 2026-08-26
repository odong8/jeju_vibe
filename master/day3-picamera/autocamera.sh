#!/bin/bash
# 사진 한 장 찍어서 저장하기 (Trixie: rpicam-still)

DATE=$(date +"%Y-%m-%d_%H%M")
SAVE_DIR=/home/pi/master/autocamera

# 저장 폴더가 없으면 먼저 만든다 (없으면 촬영이 실패한다)
mkdir -p "$SAVE_DIR"

rpicam-still --nopreview --width 1280 --height 720 -o "$SAVE_DIR/$DATE.jpg"
