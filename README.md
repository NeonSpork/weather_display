# Weather display

This is a short step-by-step of how to set up a simple weather display with the 2.7 inch Waveshare display. The python code only runs in python 2 because the Waveshare people wrote their library in python 2, and I don't see the point in wasting time converting it to python 3.X when it works just fine.

Also this is only in metric. Sorry I'm not sorry.

![alt text](https://i.imgur.com/MVdSSnAl.jpg "The finished product")

#### Disclaimer
Use at your own risk. It should work fine, but I can't guarantee no bugs :) Also, I'm fairly new to python and coding in general so go easy on me.

## Equipment used
* Raspberry Pi Zero W

   You could use any Raspberry Pi with GPIO pins and wifi capabilites. I chose the Zero W due to its small size.

* Waveshare 2.7 inch e-Paper HAT display

   You *could* use another size display, but you'd have to modify the code somewhat.

* 8 GB micro SD card (with Raspian installed)

   Most SD cards should be just fine. Not sure what the minimum size could be, but I wouldn't go below 4 GB.

* Piece of wood / plastic / box / whatever

   Whatever you want to make the frame out of really.

## Prepping the Raspberry Pi
I did this on a bog standard Raspian install.

### Setting up the e-Paper display
I followed the step by step instructions on Waveshare's wiki:
https://www.waveshare.com/wiki/Pioneer600#Libraries_Installation_for_RPi

Fairly straight forward step-by-step that worked without a hitch for me.

### Installing libraries for the code
All the libraries in this code should be built in to python, but in case you need any you should be able to install them via pip.

### Copying the code
Once the necessary libraries are set up for the display, you *should* be able to just copy the entire file onto your pi and run the python script. Make sure you also copy the 'yr_icons' folder, since that's where the code grabs the icons from. The icons were also graciously provided by Yr, I just processed them slightly to make them work better with the e-Paper display. *Sidenote: if you do improve upon the icons in any way or notice something off, let me know!*

### Setting up the font
You can use any .ttf font that tickles your fancy, but you may need to tweak the code. I chose Arial for my display because I enjoy how it looks. The FreeArial.ttf file is included in the repository, and it needs to be copied to **/usr/share/fonts/truetype/freefont** on your Pi.

### Weather data
This code uses weather data from yr.no (a collaboration between the Norwegian Meteorological Institute and the National Broadcasting Channel in Norway). They publish their data for free, but with the caveat that you follow their user requirements [found here.](http://om.yr.no/info/verdata/free-weather-data/ "Information about the free weather data service")

Search for your desired location on yr.no, then add "forecast.xml" to the end of the url.

Example:

Weather page for the South Pole https://www.yr.no/place/Antarctica/Other/South_Pole~6942239/

XML file for the South Pole https://www.yr.no/place/Antarctica/Other/South_Pole~6942239/forecast.xml

Then replace the example url with your url in the code!

## Running the code
Copy the whole folder onto your Pi.
### Option 1
Open terminal and navigate to the folder. Run the python script with 'python weather_display.py'
Stop the code with keyboard interrupt Ctrl+C in the terminal.
### Option 2
Use the launcher.sh script to start the python script automatically at reboot:

First make a logs directory. Open the terminal and navigate to the weather_display folder and make the directory.
```
$ cd /home/Pi/YOUR_FOLDER/weather_display
$ mkdir logs
```
Open crontab.
```
sudo crontab -e
```
Add the following line, replacing YOUR_FOLDER with whatever directory you placed the weather_display folder in:
```
@reboot sh /home/pi/YOUR_FOLDER/weather_display/launcher.sh >/home/pi/YOUR_FOLDER/weather_display/logs/cronlog 2>&1
```
Then hit Ctrl+X to save, Y to confirm and Enter to exit.
The launcher shell will navigate to the correct folder and run the python script. If for whatever reason it doesn't work, the errors will be logged in a text file in /weather_display/logs.

Once that is done, it's necessary to enable the option to delay boot until network is established (otherwise you get weird errors).
```
sudo raspi-config
```
Then navigate to option 3 - Boot options
![alt text](https://i.imgur.com/l7dhtTOm.png "Raspi-config option 3")
Turn on the option to wait for network at boot.
![alt text](https://i.imgur.com/9Rm3Gfvm.png "Wait for network")
Hit finish and reboot.

If you need to stop the script for whatever reason while using Option 2 you'll need to either use VNC and kill it via the task manager or via terminal by for example using the ps -A command and killing the python script.

## Make it your own
Feel free to edit the display or change the data it displays as you please. You can easily access anything in the .xml file by calling the correct tree:
```python
Example:
root[#][#][#][#].attrib['variableName']
```

Make a cool case or something to make it look smooth for bonus points! Have fun!

## TODO
* Do something to indicate an error has occurred, for example if urllub2 raises and urlopen error
* Maybe find a clever way to graphically display precipitation
