# Weather display

This is a short step-by-step of how to set up a simple weather display with the 2.7 inch Waveshare display. The python code only runs in python 2 because the Waveshare people wrote their library in python 2, and I don't see the point in wasting time converting it to python 3.X when it works just fine.

![alt text](https://i.imgur.com/MVdSSnAl.jpg "The finished product")

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
Copy the whole folder onto your Pi. Open terminal and navigate to the folder. Run the python script with 'python weather_display.py'
