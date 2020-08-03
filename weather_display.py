"""Weather e-ink display.

Weather forecast from Yr, delivered by the
Norwegian Meteorological Institute and NRK.

This code is specifically written for the
2.7 inch e-ink display, but can easily be
modified to fit another size.
"""


import time
import logging
import os
import textwrap
import epd2in7
from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw
import urllib2
import json


"""Need to initialize the display so the
Waveshare libraries can do their thing. The 2.7 inch display is
176 x 264 pixels. This code used the display in portait
mode. It should be possible to render/draw in
landscape format and rotate the mask before updating
the frame. But I had a difficult time getting it to
work, and preferred a portrait set up for my use case.

If you want to use another font you need to download it
in .ttf format and place it in the relevant file.
"""
epd = epd2in7.EPD()
epd.init()
EPD_WIDTH = epd2in7.EPD_WIDTH  # 176 pixels
EPD_HEIGHT = epd2in7.EPD_HEIGHT  # 264 pixels
# Fonts
teenytinyfont = ImageFont.truetype(
    '/usr/share/fonts/truetype/freefont/FreeArial.ttf', 10)
teenyfont = ImageFont.truetype(
    '/usr/share/fonts/truetype/freefont/FreeArial.ttf', 12)
tinyfont = ImageFont.truetype(
    '/usr/share/fonts/truetype/freefont/FreeArial.ttf', 14)
smallfont = ImageFont.truetype(
    '/usr/share/fonts/truetype/freefont/FreeArial.ttf', 18)
normalfont = ImageFont.truetype(
    '/usr/share/fonts/truetype/freefont/FreeArial.ttf', 22)
medfont = ImageFont.truetype(
    '/usr/share/fonts/truetype/freefont/FreeArial.ttf', 40)
bigfont = ImageFont.truetype(
    '/usr/share/fonts/truetype/freefont/FreeArial.ttf', 70)

# data = 0
# mask = 0

urlLegend = urllib2.urlopen('https://api.met.no/weatherapi/weathericon/2.0/legends')
legendUrl = urlLegend.read()
legend = json.loads(legendUrl)

def updateWeatherUrl():
    """Opens the json file from www.yr.no

    Opens url and handles the processing of the json.
    Should be called every time you update
    the frame since the information won't be refreshed unless
    the url is updated.
    """
    # attempts = 1
    urlReady = False
    while not urlReady:
        url = urllib2.urlopen(
            'https://api.met.no/weatherapi/locationforecast/2.0/complete?lat=58.8474&lon=5.7166')
        # Exchange the link above with your location.
        if(url.getcode() == 200):
            urlReady = True
            attempts = 1
            dataUrl = url.read()
            global data
            data = json.loads(dataUrl)
            print('{} Weather data URL successfully opened.'
                  .format(data['properties']['meta']['updated_at']))
        else:
            print('Error retrieving data', url.getcode())
            attempts += 1
            if attempts <= 100:
                print('Retrying in 10 seconds.'
                      ' (Attempt {} of 100)'.format(attempts))
                time.sleep(10)
            elif attempts > 100:
                raise RuntimeError('Please check your internet connection '
                                   'and restart the program.')


def parseJsonAndDrawToMask():
    """Parses json into strings.

    Handles the expansion of the json into their respective variables.
    Also handles the opening of image files and draws everything to the
    mask that will be drawn on the E-ink screen.
    """
    lastUpdated = time.strftime('%d.%m.%y %H:%M')
    stats = data['properties']['timeseries']


    # Temperature related variables:
    # Five total periods: current temperature, and the four next
    # 6 hour periods. (FirstPeriod, SecondPeriod, etc)
    currentTemperature = stats[0]['data']['instant']['details']['air_temperature']

    next6hTemp = stats[0]['data']['next_6_hours']['details']['air_temperature_max']
    icon6h = stats[0]['data']['next_6_hours']['summary']['symbol_code']
    next12hTemp = stats[0]['data']['next_12_hours']['details']['air_temperature_max']
    icon12h = stats[0]['data']['next_12_hours']['summary']['symbol_code']

    # Weather conditions and various icons
    currentIcon = stats[0]['data']['next_1_hours']['summary']['symbol_code']
    currentStatus = legend[currentIcon]['desc_en']
    rainChancePercent = stats[0]['data']['next_1_hours']['summary']['symbol_code']

    conditionIcon = Image.open('yr_icons/{}.png'.format(currentIcon))
    refreshIcon = Image.open('yr_icons/refresh.png')
    windIcon = Image.open('yr_icons/windicon.png')
    rainLine = Image.open('yr_icons/rainline.png')
    rainChance = Image.open('yr_icons/rainChance.png')
    twelveHrain = Image.open('yr_icons/twelveHrain.png')
    next6hIcon = Image.open('yr_icons/{}.png'.format(icon6h))
    sixhours = Image.open('yr_icons/sixhours.png')
    next12hIcon = Image.open('yr_icons/{}.png'.format(icon12h))
    twelvehours = Image.open('yr_icons/twelvehours.png')

    # Wind information
    windSpeed = stats[0]['data']['instant']['details']['wind_speed']
    windMaxGust = stats[0]['data']['instant']['details']['wind_speed_of_gust']

    # Coordinates are X, Y:
    # 0, 0 is top left of screen 176, 264 is bottom right
    global mask
    mask = Image.new('1', (EPD_WIDTH, EPD_HEIGHT), 255)
    # 255: clear the image with white
    draw = ImageDraw.Draw(mask)

    mask.paste(conditionIcon, (0, 0))
    currentTemp = int(currentTemperature)
    if (currentTemp <= 9) and (currentTemp >= -9):
        # Centers the temperature when it is single digits
        draw.text((120, 22), '{}'.format(currentTemp), font=bigfont, fill=0)
    elif (currentTemp >= 10):
        draw.text((98, 22), '{}'.format(currentTemp), font=bigfont, fill=0)
    elif (currentTemp <= -10):
        # Adds text "BELOW ZERO" underneath, no space for a minus sign
        negativeCurrentTemp = (currentTemp * -1)
        draw.text((98, 22), '{}'.format(negativeCurrentTemp),
                  font=bigfont, fill=0)
        draw.text((105, 76), 'BELOW ZERO', font=teenyfont, fill=0)


    mask.paste(rainChance, (112, 93))
    draw.text((133, 92), '{}%'.format(int(rainChancePercent)), font=teenyfont, fill=0)


    mask.paste(refreshIcon, (93, 85))
    draw.text((106, 84), '{}'.format(lastUpdated),
              font=teenytinyfont, fill=0)
    wrappedStatus = textwrap.fill(currentStatus, 19)
    draw.text((5, 104), '{}'.format(wrappedStatus), font=smallfont, fill=0)



    mask.paste(sixhours, (2, 153))
    draw.text((22, 162), '{}'.format(next6hTemp), font=smallfont, fill=0)
    mask.paste(next6hIcon.resize((48, 48)), (22, 144))
    mask.paste(twelvehours, (90, 153))
    draw.text((110, 162), '{}'.format(next12hTemp), font=smallfont, fill=0)
    mask.paste(next12hIcon.resize((48, 48)), (110, 144))

    # Precipitation lines
    # Black fill line for actual rain
    rain1h = 249 - (rainAmount1*12)
    rain2h = 249 - (rainAmount2*12)
    rain3h = 249 - (rainAmount3*12)
    rain4h = 249 - (rainAmount4*12)
    rain5h = 249 - (rainAmount5*12)
    rain6h = 249 - (rainAmount6*12)
    rain7h = 249 - (rainAmount7*12)
    rain8h = 249 - (rainAmount8*12)
    rain9h = 249 - (rainAmount9*12)
    rain10h = 249 - (rainAmount10*12)
    rain11h = 249 - (rainAmount11*12)
    rain12h = 249 - (rainAmount12*12)
    if(rain1h > 0):
        draw.line((10, 249, 10, rain1h), fill=0, width=10)
    if(rain2h > 0):
        draw.line((24, 249, 24, rain2h), fill=0, width=10)
    if(rain3h > 0):
        draw.line((38, 249, 38, rain3h), fill=0, width=10)
    if(rain4h > 0):
        draw.line((52, 249, 52, rain4h), fill=0, width=10)
    if(rain5h > 0):
        draw.line((66, 249, 66, rain5h), fill=0, width=10)
    if(rain6h > 0):
        draw.line((80, 249, 80, rain6h), fill=0, width=10)
    if(rain7h > 0):
        draw.line((94, 249, 94, rain7h), fill=0, width=10)
    if(rain8h > 0):
        draw.line((108, 249, 108, rain8h), fill=0, width=10)
    if(rain9h > 0):
        draw.line((122, 249, 122, rain9h), fill=0, width=10)
    if(rain10h > 0):
        draw.line((136, 249, 136, rain10h), fill=0, width=10)
    if(rain11h > 0):
        draw.line((150, 249, 150, rain11h), fill=0, width=10)
    if(rain12h > 0):
        draw.line((164, 249, 164, rain12h), fill=0, width=10)
    # Only outline for maximum possible rain
    rainMax1h = 249 - (rainMaxAmount1*12)
    rainMax2h = 249 - (rainMaxAmount2*12)
    rainMax3h = 249 - (rainMaxAmount3*12)
    rainMax4h = 249 - (rainMaxAmount4*12)
    rainMax5h = 249 - (rainMaxAmount5*12)
    rainMax6h = 249 - (rainMaxAmount6*12)
    rainMax7h = 249 - (rainMaxAmount7*12)
    rainMax8h = 249 - (rainMaxAmount8*12)
    rainMax9h = 249 - (rainMaxAmount9*12)
    rainMax10h = 249 - (rainMaxAmount10*12)
    rainMax11h = 249 - (rainMaxAmount11*12)
    rainMax12h = 249 - (rainMaxAmount12*12)
    if(rainMax1h > 0):
        draw.line((10, 249, 10, rainMax1h), fill=0, width=1)
        draw.line((10, 249, 19, 249), fill=0, width=1)
        draw.line((19, 249, 19, rainMax1h), fill=0, width=1)
        draw.line((10, rainMax1h, 19, rainMax1h), fill=0, width=1)
    if(rainMax2h > 0):
        draw.line((24, 249, 24, rainMax2h), fill=0, width=1)
        draw.line((24, 249, 33, 249), fill=0, width=1)
        draw.line((33, 249, 33, rainMax2h), fill=0, width=1)
        draw.line((24, rainMax2h, 33, rainMax2h), fill=0, width=1)
    if(rainMax3h > 0):
        draw.line((38, 249, 38, rainMax3h), fill=0, width=1)
        draw.line((38, 249, 47, 249), fill=0, width=1)
        draw.line((47, 249, 47, rainMax3h), fill=0, width=1)
        draw.line((38, rainMax3h, 47, rainMax3h), fill=0, width=1)
    if(rainMax4h > 0):
        draw.line((52, 249, 52, rainMax4h), fill=0, width=1)
        draw.line((52, 249, 61, 249), fill=0, width=1)
        draw.line((61, 249, 61, rainMax4h), fill=0, width=1)
        draw.line((52, rainMax4h, 61, rainMax4h), fill=0, width=1)
    if(rainMax5h > 0):
        draw.line((66, 249, 66, rainMax5h), fill=0, width=1)
        draw.line((66, 249, 75, 249), fill=0, width=1)
        draw.line((75, 249, 75, rainMax5h), fill=0, width=1)
        draw.line((66, rainMax5h, 75, rainMax5h), fill=0, width=1)
    if(rainMax6h > 0):
        draw.line((80, 249, 80, rainMax6h), fill=0, width=1)
        draw.line((80, 249, 89, 249), fill=0, width=1)
        draw.line((89, 249, 89, rainMax6h), fill=0, width=1)
        draw.line((80, rainMax6h, 89, rainMax6h), fill=0, width=1)
    if(rainMax7h > 0):
        draw.line((94, 249, 94, rainMax7h), fill=0, width=1)
        draw.line((94, 249, 103, 249), fill=0, width=1)
        draw.line((103, 249, 103, rainMax7h), fill=0, width=1)
        draw.line((94, 249, 103, rainMax7h), fill=0, width=1)
    if(rainMax8h > 0):
        draw.line((108, 249, 108, rainMax8h), fill=0, width=1)
        draw.line((108, 249, 117, 249), fill=0, width=1)
        draw.line((117, 249, 117, rainMax8h), fill=0, width=1)
        draw.line((108, rainMax8h, 117, rainMax8h), fill=0, width=1)
    if(rainMax9h > 0):
        draw.line((122, 249, 122, rainMax9h), fill=0, width=1)
        draw.line((122, 249, 131, 249), fill=0, width=1)
        draw.line((131, 249, 131, rainMax9h), fill=0, width=1)
        draw.line((122, rainMax9h, 131, rainMax9h), fill=0, width=1)
    if(rainMax10h > 0):
        draw.line((136, 249, 136, rainMax10h), fill=0, width=1)
        draw.line((136, 249, 145, 249), fill=0, width=1)
        draw.line((145, 249, 145, rainMax10h), fill=0, width=1)
        draw.line((136, rainMax10h, 145, rainMax10h), fill=0, width=1)
    if(rainMax11h > 0):
        draw.line((150, 249, 150, rainMax11h), fill=0, width=1)
        draw.line((150, 249, 159, 249), fill=0, width=1)
        draw.line((159, 249, 159, rainMax11h), fill=0, width=1)
        draw.line((150, rainMax11h, 159, rainMax11h), fill=0, width=1)
    if(rainMax12h > 0):
        draw.line((164, 249, 164, rainMax12h), fill=0, width=1)
        draw.line((164, 249, 173, 249), fill=0, width=1)
        draw.line((173, 249, 173, rainMax12h), fill=0, width=1)
        draw.line((164, rainMax12h, 173, rainMax12h), fill=0, width=1)

    mask.paste(windIcon, (0, 258))
    mask.paste(rainLine, (8, 250))
    mask.paste(twelveHrain, (1, 224))
    draw.text((43, 256), '{}-{} m/s'.format(windSpeed, windMaxGust),
              font=smallfont, fill=0)


    print('Successfully parsed XML file and created mask. {}'.format(time.strftime('%d%m%y-%H:%M:%S')))


def printMaskToEinkScreen():
    rotatedMask = mask.rotate(180)
    # Turns mask upside down, this just happened to work best for my frame
    # with regards to which side the cable came out.
    epd.display_frame(epd.get_frame_buffer(rotatedMask))
    print('Weather display successfully refreshed at {}'.format(time.strftime('%d%m%y-%H:%M:%S')))


def setUpErrorLogging():
    logging.basicConfig(filename="{}/logs/weather.log".format(os.getcwd()),
                        filemode='w',
                        level=logging.ERROR,
                        format='%(asctime)s - %(levelname)s - %(message)s',
                        )


def logError(e):
    logging.error("{} ({}): {}".format(e.__class__, e.__doc__, e.message))

if __name__ == '__main__':
    setUpErrorLogging()
    running = True
    while running:
        try:
            updateWeatherUrl()
        except Exception as e:
            logError(e)
            print(e)
        try:
            parseJsonAndDrawToMask()
        except Exception as e:
            logError(e)
            print(e)
        try:
            printMaskToEinkScreen()
        except Exception as e:
            logError (e)
            print(e)
        time.sleep(600)
        # Refreshes every 10 minutes
