#!/bin/bash
# autodht11.py 실행 스크립트 (cron 등록용)
#   crontab -e 에 아래처럼 등록:
#   */10 * * * * /home/pi/master/day3-picamera/autodht11.sh >> /home/pi/master/autodht11.log 2>&1

python3 /home/pi/master/day3-picamera/autodht11.py
