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
import urllib.request, urllib.error, urllib.parse
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

urlLegend = urllib.request.urlopen('https://api.met.no/weatherapi/weathericon/2.0/legends')
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
        url = urllib.request.urlopen(
            'https://api.met.no/weatherapi/locationforecast/2.0/complete?lat=58.8474&lon=5.7166')
        # Exchange the link above with your location. 
        # Essentially you just replace the latitude and longitude with the location you want.
        if(url.getcode() == 200):
            urlReady = True
            attempts = 1
            dataUrl = url.read()
            global data
            data = json.loads(dataUrl)
            print(('{} Weather data URL successfully opened.'
                  .format(data['properties']['meta']['updated_at'])))
        else:
            print(('Error retrieving data', url.getcode()))
            attempts += 1
            if attempts <= 100:
                print(('Retrying in 10 seconds.'
                      ' (Attempt {} of 100)'.format(attempts)))
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
    next12hTemp = stats[11]['data']['instant']['details']['air_temperature']
    icon12h = stats[0]['data']['next_12_hours']['summary']['symbol_code']

    # Weather conditions and various icons
    currentIcon = stats[0]['data']['next_1_hours']['summary']['symbol_code']
    iconStatus = currentIcon
    if(iconStatus[-4:]=='_day'):
        iconStatus = iconStatus.rstrip(iconStatus[-3:])
        iconStatus = iconStatus.rstrip('_')
    if(iconStatus[-6:]=='_night'):
        iconStatus = iconStatus.rstrip('_night')
    if(iconStatus[-14:]=='_polartwilight'):
        iconStatus = iconStatus.rstrip('_polartwilight')
    currentStatus = legend[iconStatus]['desc_en']
    rainChancePercent = stats[0]['data']['next_1_hours']['details']['probability_of_precipitation']

    conditionIcon = Image.open('icons/weatherIcons/{}.png'.format(currentIcon))
    refreshIcon = Image.open('icons/refresh.png')
    windIcon = Image.open('icons/windicon.png')
    rainLine = Image.open('icons/rainline.png')
    rainChance = Image.open('icons/rainChance.png')
    twelveHrain = Image.open('icons/twelveHrain.png')
    next6hIcon = Image.open('icons/weatherIcons/{}.png'.format(icon6h))
    sixhours = Image.open('icons/sixhours.png')
    next12hIcon = Image.open('icons/weatherIcons/{}.png'.format(icon12h))
    twelvehours = Image.open('icons/twelvehours.png')

    # Wind information
    windSpeed = stats[0]['data']['instant']['details']['wind_speed']
    windMaxGust = stats[0]['data']['instant']['details']['wind_speed_of_gust']

    # Precipitation info
    rainAmount = [min(stats[i]['data']['next_1_hours']['details']['precipitation_amount'],4) for i in range(12)]

    rainMaxAmount = [min(stats[i]['data']['next_1_hours']['details']['precipitation_amount_max'],4) for i in range(12)]
    
    # Coordinates are X, Y:
    # 0, 0 is top left of screen 176, 264 is bottom right
    # global mask
    mask = Image.new('1', (EPD_WIDTH, EPD_HEIGHT), 255)
    # 255: clear the image with white
    draw = ImageDraw.Draw(mask)

    mask.paste(conditionIcon, (0, 0))
    currentTemp = int(currentTemperature)
    if (currentTemp <= 9) and (currentTemp >= -9):
        # Centers the temperature when it is single digits
        draw.text((120, 12), '{}'.format(currentTemp), font=bigfont, fill=0)
    elif (currentTemp >= 10):
        draw.text((98, 12), '{}'.format(currentTemp), font=bigfont, fill=0)
    elif (currentTemp <= -10):
        # Adds text "BELOW ZERO" underneath, no space for a minus sign
        negativeCurrentTemp = (currentTemp * -1)
        draw.text((98, 3), '{}'.format(negativeCurrentTemp),
                  font=bigfont, fill=0)
        draw.text((105, 70), 'BELOW ZERO', font=teenytinyfont, fill=0)

    mask.paste(rainChance, (110, 83))
    draw.text((127, 83), '{}%'.format(int(rainChancePercent)), font=smallfont, fill=0)

    mask.paste(refreshIcon, (91, 1))
    draw.text((104, 1), '{}'.format(lastUpdated),
              font=teenytinyfont, fill=0)
    wrappedStatus = textwrap.fill(currentStatus, 19)
    draw.text((5, 104), '{}'.format(wrappedStatus), font=smallfont, fill=0)



    mask.paste(sixhours, (2, 153))
    draw.text((22, 162), '{}'.format(next6hTemp), font=smallfont, fill=0)
    mask.paste(next6hIcon.resize((48, 48)), (22, 144))
    mask.paste(twelvehours, (90, 153))
    draw.text((110, 162), '{}'.format(next12hTemp), font=smallfont, fill=0)
    mask.paste(next12hIcon.resize((48, 48)), (110, 144))

    # Black fill line for actual rain
    rainh = [239 - (ra*10) for ra in rainAmount]
    
    diagram_intervals = [
        (10,19),
        (24,33),
        (38,47),
        (52,61),
        (66,75),
        (80,90),
        (94,103),
        (108,117),
        (122,131),
        (136,145),
        (150,159),
        (164,173),
    ]

    for rain_amount, interval in zip(rainh,diagram_intervals):
        for i in range(*interval):
            draw.line((i,239,i,rain_amount), fill=0, width=1)

    # Only outline for maximum possible rain
    # rainMaxH = [239 - (max_rain*10) for max_rain in rainMaxAmount]
    rainMaxH = map(lambda x: 239 - (x*10), rainMaxAmount)

    for rain_max, interval in zip(rainMaxH,diagram_intervals):
        draw.line((interval[0], 239, interval[0], rain_max), fill=0, width=1)
        draw.line((interval[0], 239, interval[1], 239), fill=0, width=1)
        draw.line((interval[1], 239, interval[1], rain_max), fill=0, width=1)
        draw.line((interval[0], rain_max, interval[1], rain_max), fill=0, width=1)

    mask.paste(windIcon, (0, 248))
    mask.paste(rainLine, (8, 240))
    mask.paste(twelveHrain, (1, 212))
    draw.text((43, 244), '{}-{} m/s'.format(windSpeed, windMaxGust),
              font=smallfont, fill=0)


    print(('Successfully parsed json file and created mask. {}'.format(time.strftime('%d%m%y-%H:%M:%S'))))
    # epd.display_frame(epd.get_frame_buffer(mask))

    # Turns mask upside down, this just happened to work best for my frame
    # with regards to which side the cable came out.
    rotatedMask = mask.rotate(180)
    epd.display_frame(epd.get_frame_buffer(rotatedMask))
    print(('Weather display successfully refreshed at {}'.format(time.strftime('%d%m%y-%H:%M:%S'))))


# def printMaskToEinkScreen():


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
        # try:
        #     printMaskToEinkScreen()
        # except Exception as e:
        #     logError (e)
        #     print(e)
        time.sleep(600)
        # Refreshes every 10 minutes
