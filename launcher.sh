#!/bin/sh
# launcher.sh
# navigate to home directory, then to this directory, then execute python script, then back home
# MAKE SURE TO EDIT YOUR_FOLDER TO THE CORRECT DIRECTORY

cd /
cd home/pi/YOUR_FOLDER/weather_display
python weather_display.py
cd /
