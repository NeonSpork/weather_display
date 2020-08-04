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

    conditionIcon = Image.open('icons/weatherIcons{}.png'.format(currentIcon))
    refreshIcon = Image.open('icons/refresh.png')
    windIcon = Image.open('icons/windicon.png')
    rainLine = Image.open('icons/rainline.png')
    rainChance = Image.open('icons/rainChance.png')
    twelveHrain = Image.open('icons/twelveHrain.png')
    next6hIcon = Image.open('icons/{}.png'.format(icon6h))
    sixhours = Image.open('icons/sixhours.png')
    next12hIcon = Image.open('icons/{}.png'.format(icon12h))
    twelvehours = Image.open('icons/twelvehours.png')

    # Wind information
    windSpeed = stats[0]['data']['instant']['details']['wind_speed']
    windMaxGust = stats[0]['data']['instant']['details']['wind_speed_of_gust']

    # Precipitation info
    rainAmount1 = stats[0]['data']['next_1_hours']['details']['precipitation_amount']
    rainAmount2 = stats[1]['data']['next_1_hours']['details']['precipitation_amount']
    rainAmount3 = stats[2]['data']['next_1_hours']['details']['precipitation_amount']
    rainAmount4 = stats[3]['data']['next_1_hours']['details']['precipitation_amount']
    rainAmount5 = stats[4]['data']['next_1_hours']['details']['precipitation_amount']
    rainAmount6 = stats[5]['data']['next_1_hours']['details']['precipitation_amount']
    rainAmount7 = stats[6]['data']['next_1_hours']['details']['precipitation_amount']
    rainAmount8 = stats[7]['data']['next_1_hours']['details']['precipitation_amount']
    rainAmount9 = stats[8]['data']['next_1_hours']['details']['precipitation_amount']
    rainAmount10 = stats[9]['data']['next_1_hours']['details']['precipitation_amount']
    rainAmount11 = stats[10]['data']['next_1_hours']['details']['precipitation_amount']
    rainAmount12 = stats[11]['data']['next_1_hours']['details']['precipitation_amount']
    rainMaxAmount1 = stats[0]['data']['next_1_hours']['details']['precipitation_amount_max']
    rainMaxAmount2 = stats[1]['data']['next_1_hours']['details']['precipitation_amount_max']
    rainMaxAmount3 = stats[2]['data']['next_1_hours']['details']['precipitation_amount_max']
    rainMaxAmount4 = stats[3]['data']['next_1_hours']['details']['precipitation_amount_max']
    rainMaxAmount5 = stats[4]['data']['next_1_hours']['details']['precipitation_amount_max']
    rainMaxAmount6 = stats[5]['data']['next_1_hours']['details']['precipitation_amount_max']
    rainMaxAmount7 = stats[6]['data']['next_1_hours']['details']['precipitation_amount_max']
    rainMaxAmount8 = stats[7]['data']['next_1_hours']['details']['precipitation_amount_max']
    rainMaxAmount9 = stats[8]['data']['next_1_hours']['details']['precipitation_amount_max']
    rainMaxAmount10 = stats[9]['data']['next_1_hours']['details']['precipitation_amount_max']
    rainMaxAmount11 = stats[10]['data']['next_1_hours']['details']['precipitation_amount_max']
    rainMaxAmount12 = stats[11]['data']['next_1_hours']['details']['precipitation_amount_max']
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

    # Precipitation lines
    # Black fill line for actual rain
    rain1h = 239 - (rainAmount1*10)
    rain2h = 239 - (rainAmount2*10)
    rain3h = 239 - (rainAmount3*10)
    rain4h = 239 - (rainAmount4*10)
    rain5h = 239 - (rainAmount5*10)
    rain6h = 239 - (rainAmount6*10)
    rain7h = 239 - (rainAmount7*10)
    rain8h = 239 - (rainAmount8*10)
    rain9h = 239 - (rainAmount9*10)
    rain10h = 239 - (rainAmount10*10)
    rain11h = 239 - (rainAmount11*10)
    rain12h = 239 - (rainAmount12*10)
    if(rain1h > 0):
        for i in range(10, 19):
            draw.line((i, 239, i, rain1h), fill=0, width=1)
    if(rain2h > 0):
        for i in range(24, 33):
            draw.line((i, 239, i, rain2h), fill=0, width=1)
    if(rain3h > 0):
        for i in range(38, 47):
            draw.line((i, 239, i, rain3h), fill=0, width=1)
    if(rain4h > 0):
        for i in range(52, 61):
            draw.line((i, 239, i, rain4h), fill=0, width=1)
    if(rain5h > 0):
        for i in range(66, 75):
            draw.line((i, 239, i, rain5h), fill=0, width=1)
    if(rain6h > 0):
        for i in range(80, 90):
            draw.line((i, 239, i, rain6h), fill=0, width=1)
    if(rain7h > 0):
        for i in range(94, 103):
            draw.line((i, 239, i, rain7h), fill=0, width=1)
    if(rain8h > 0):
        for i in range(108, 117):
            draw.line((i, 239, i, rain8h), fill=0, width=1)
    if(rain9h > 0):
        for i in range(122, 131):
            draw.line((i, 239, i, rain9h), fill=0, width=1)
    if(rain10h > 0):
        for i in range(136, 145):
            draw.line((i, 239, i, rain10h), fill=0, width=1)
    if(rain11h > 0):
        for i in range(150, 159):
            draw.line((i, 239, i, rain11h), fill=0, width=1)
    if(rain12h > 0):
        for i in range(164, 173):
            draw.line((i, 239, i, rain12h), fill=0, width=1)
    # Only outline for maximum possible rain
    rainMax1h = 239 - (rainMaxAmount1*10)
    rainMax2h = 239 - (rainMaxAmount2*10)
    rainMax3h = 239 - (rainMaxAmount3*10)
    rainMax4h = 239 - (rainMaxAmount4*10)
    rainMax5h = 239 - (rainMaxAmount5*10)
    rainMax6h = 239 - (rainMaxAmount6*10)
    rainMax7h = 239 - (rainMaxAmount7*10)
    rainMax8h = 239 - (rainMaxAmount8*10)
    rainMax9h = 239 - (rainMaxAmount9*10)
    rainMax10h = 239 - (rainMaxAmount10*10)
    rainMax11h = 239 - (rainMaxAmount11*10)
    rainMax12h = 239 - (rainMaxAmount12*10)
    if(rainMax1h > 0):
        draw.line((10, 239, 10, rainMax1h), fill=0, width=1)
        draw.line((10, 239, 19, 239), fill=0, width=1)
        draw.line((19, 239, 19, rainMax1h), fill=0, width=1)
        draw.line((10, rainMax1h, 19, rainMax1h), fill=0, width=1)
    if(rainMax2h > 0):
        draw.line((24, 239, 24, rainMax2h), fill=0, width=1)
        draw.line((24, 239, 33, 239), fill=0, width=1)
        draw.line((33, 239, 33, rainMax2h), fill=0, width=1)
        draw.line((24, rainMax2h, 33, rainMax2h), fill=0, width=1)
    if(rainMax3h > 0):
        draw.line((38, 239, 38, rainMax3h), fill=0, width=1)
        draw.line((38, 239, 47, 239), fill=0, width=1)
        draw.line((47, 239, 47, rainMax3h), fill=0, width=1)
        draw.line((38, rainMax3h, 47, rainMax3h), fill=0, width=1)
    if(rainMax4h > 0):
        draw.line((52, 239, 52, rainMax4h), fill=0, width=1)
        draw.line((52, 239, 61, 239), fill=0, width=1)
        draw.line((61, 239, 61, rainMax4h), fill=0, width=1)
        draw.line((52, rainMax4h, 61, rainMax4h), fill=0, width=1)
    if(rainMax5h > 0):
        draw.line((66, 239, 66, rainMax5h), fill=0, width=1)
        draw.line((66, 239, 75, 239), fill=0, width=1)
        draw.line((75, 239, 75, rainMax5h), fill=0, width=1)
        draw.line((66, rainMax5h, 75, rainMax5h), fill=0, width=1)
    if(rainMax6h > 0):
        draw.line((80, 239, 80, rainMax6h), fill=0, width=1)
        draw.line((80, 239, 89, 239), fill=0, width=1)
        draw.line((89, 239, 89, rainMax6h), fill=0, width=1)
        draw.line((80, rainMax6h, 89, rainMax6h), fill=0, width=1)
    if(rainMax7h > 0):
        draw.line((94, 239, 94, rainMax7h), fill=0, width=1)
        draw.line((94, 239, 103, 239), fill=0, width=1)
        draw.line((103, 239, 103, rainMax7h), fill=0, width=1)
        draw.line((94, rainMax7h, 103, rainMax7h), fill=0, width=1)
    if(rainMax8h > 0):
        draw.line((108, 239, 108, rainMax8h), fill=0, width=1)
        draw.line((108, 239, 117, 239), fill=0, width=1)
        draw.line((117, 239, 117, rainMax8h), fill=0, width=1)
        draw.line((108, rainMax8h, 117, rainMax8h), fill=0, width=1)
    if(rainMax9h > 0):
        draw.line((122, 239, 122, rainMax9h), fill=0, width=1)
        draw.line((122, 239, 131, 239), fill=0, width=1)
        draw.line((131, 239, 131, rainMax9h), fill=0, width=1)
        draw.line((122, rainMax9h, 131, rainMax9h), fill=0, width=1)
    if(rainMax10h > 0):
        draw.line((136, 239, 136, rainMax10h), fill=0, width=1)
        draw.line((136, 239, 145, 239), fill=0, width=1)
        draw.line((145, 239, 145, rainMax10h), fill=0, width=1)
        draw.line((136, rainMax10h, 145, rainMax10h), fill=0, width=1)
    if(rainMax11h > 0):
        draw.line((150, 239, 150, rainMax11h), fill=0, width=1)
        draw.line((150, 239, 159, 239), fill=0, width=1)
        draw.line((159, 239, 159, rainMax11h), fill=0, width=1)
        draw.line((150, rainMax11h, 159, rainMax11h), fill=0, width=1)
    if(rainMax12h > 0):
        draw.line((164, 239, 164, rainMax12h), fill=0, width=1)
        draw.line((164, 239, 173, 239), fill=0, width=1)
        draw.line((173, 239, 173, rainMax12h), fill=0, width=1)
        draw.line((164, rainMax12h, 173, rainMax12h), fill=0, width=1)

    mask.paste(windIcon, (0, 248))
    mask.paste(rainLine, (8, 240))
    mask.paste(twelveHrain, (1, 212))
    draw.text((43, 244), '{}-{} m/s'.format(windSpeed, windMaxGust),
              font=smallfont, fill=0)


    print('Successfully parsed json file and created mask. {}'.format(time.strftime('%d%m%y-%H:%M:%S')))
    # epd.display_frame(epd.get_frame_buffer(mask))

    # Turns mask upside down, this just happened to work best for my frame
    # with regards to which side the cable came out.
    rotatedMask = mask.rotate(180)
    epd.display_frame(epd.get_frame_buffer(rotatedMask))
    print('Weather display successfully refreshed at {}'.format(time.strftime('%d%m%y-%H:%M:%S')))


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
