#!/bin/bash

DATE=$(date +"%Y-%m-%d_%H%M")

rpicam-still --nopreview --width 1280 --height 720 -o /home/pi/master/autocamera/$DATE.jpg
