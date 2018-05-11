"""Weather e-ink display.

JB "neonSpork" Leiknes

Weather forecast from Yr, delivered by the
Norwegian Meteorological Institute and NRK.

Code for Waveshare display available at
https://www.waveshare.com/wiki/
This code is specifically written for the
2.7 inch e-ink display, but can easily be
modified to fit another size.
"""


import time
import textwrap
import epd2in7
import Image
import ImageFont
import ImageDraw
import urllib2
import xml.etree.ElementTree as ET


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


def frameUpdate():
    # Opens the .xml file from yr.no
    # Replace "Skeiane" with desired location
    f = urllib2.urlopen(
        'https://www.yr.no/place/Norge/Rogaland/Sandnes/Skeiane/forecast.xml')
    yr_online = f.read()
    # Parses xml file into strings
    root = ET.fromstring(yr_online)

    # Temperature related variables:
    # Five total periods: current temperature, and the four next
    # 6 hour periods. (FirstPeriod, SecondPeriod, etc)
    currentTemperature = root[5][1][0][4].attrib['value']
    timeFirstPeriodStart = root[5][1][1].attrib['from'][11:13]
    timeFirstPeriodEnd = root[5][1][1].attrib['to'][11:13]
    tempFirstPeriod = root[5][1][1][4].attrib['value']
    iconFirstPeriod = root[5][1][1][0].attrib['var']
    timeSecondPeriodStart = root[5][1][2].attrib['from'][11:13]
    timeSecondPeriodEnd = root[5][1][2].attrib['to'][11:13]
    tempSecondPeriod = root[5][1][2][4].attrib['value']
    iconSecondPeriod = root[5][1][2][0].attrib['var']
    timeThirdPeriodStart = root[5][1][3].attrib['from'][11:13]
    timeThirdPeriodEnd = root[5][1][3].attrib['to'][11:13]
    tempThirdPeriod = root[5][1][3][4].attrib['value']
    iconThirdPeriod = root[5][1][3][0].attrib['var']
    timeFourthPeriodStart = root[5][1][4].attrib['from'][11:13]
    timeFourthPeriodEnd = root[5][1][4].attrib['to'][11:13]
    tempFourthPeriod = root[5][1][4][4].attrib['value']
    iconFourthPeriod = root[5][1][4][0].attrib['var']

    # Weather conditions and various icons
    currentIcon = root[5][1][0][0].attrib['var']
    unconvertedIcon = Image.open('yr_icons/{}.png'.format(currentIcon))
    conditionIcon = unconvertedIcon.convert('L')
    currentStatus = root[5][1][0][0].attrib['name']
    fullSunriseTimeStamp = root[4].attrib['rise']
    fullSunsetTimeStamp = root[4].attrib['set']
    sunriseTime = fullSunriseTimeStamp[11:16]
    sunsetTime = fullSunsetTimeStamp[11:16]
    sunupIcon = Image.open('yr_icons/sunup.png')
    sundownIcon = Image.open('yr_icons/sundown.png')
    windIcon = Image.open('yr_icons/windicon.png')
    icon1 = Image.open('yr_icons/{}.png'.format(iconFirstPeriod))
    icon2 = Image.open('yr_icons/{}.png'.format(iconSecondPeriod))
    icon3 = Image.open('yr_icons/{}.png'.format(iconThirdPeriod))
    icon4 = Image.open('yr_icons/{}.png'.format(iconFourthPeriod))

    # Wind information
    windSpeed = root[5][1][0][3].attrib['mps']
    windBeaufort = root[5][1][0][3].attrib['name']
    windDirection = root[5][1][0][2].attrib['name']

    # Coordinates are X, Y:
    # 0, 0 is top left of screen 176, 264 is bottom right
    mask = Image.new('1', (EPD_WIDTH, EPD_HEIGHT), 255)
    # 255: clear the image with white
    draw = ImageDraw.Draw(mask)

    mask.paste(conditionIcon, (0, 0))
    currentTemp = int(currentTemperature)
    if (currentTemp <= 9) and (currentTemp >= -9):
        # Centers the temperature when it is single digits
        draw.text((120, 5), '{}'.format(currentTemp), font=bigfont, fill=0)
    elif (currentTemp >= 10):
        draw.text((98, 5), '{}'.format(currentTemp), font=bigfont, fill=0)
    elif (currentTemp <= -10):
        # Adds text "BELOW ZERO" underneath, no space for a minus sign
        negativeCurrentTemp = (currentTemp * -1)
        draw.text((98, 5), '{}'.format(negativeCurrentTemp),
                  font=bigfont, fill=0)
        draw.text((98, 75), 'BELOW ZERO', font=teenyfont, fill=0)
    wrappedStatus = textwrap.fill(currentStatus, 16)
    draw.text((5, 100), '{}'.format(wrappedStatus), font=normalfont, fill=0)
    draw.line((0, 155, 176, 155), fill=0, width=2)

    draw.text((2, 158), '{}-{}'.format(timeFirstPeriodStart,
              timeFirstPeriodEnd), font=tinyfont, fill=0)
    draw.text((46, 158), '{}-{}'.format(timeSecondPeriodStart,
              timeSecondPeriodEnd), font=tinyfont, fill=0)
    draw.text((90, 158), '{}-{}'.format(timeThirdPeriodStart,
              timeThirdPeriodEnd), font=tinyfont, fill=0)
    draw.text((134, 158), '{}-{}'.format(timeFourthPeriodStart,
              timeFourthPeriodEnd), font=tinyfont, fill=0)
    draw.text((0, 180), '{}'.format(tempFirstPeriod), font=tinyfont, fill=0)
    draw.text((44, 180), '{}'.format(tempSecondPeriod), font=tinyfont, fill=0)
    draw.text((88, 180), '{}'.format(tempThirdPeriod), font=tinyfont, fill=0)
    draw.text((132, 180), '{}'.format(tempFourthPeriod), font=tinyfont, fill=0)
    mask.paste(icon1.resize((25, 25)), (16, 175))
    mask.paste(icon2.resize((25, 25)), (60, 175))
    mask.paste(icon3.resize((25, 25)), (104, 175))
    mask.paste(icon4.resize((25, 25)), (148, 175))
    draw.line((42, 155, 42, 204), fill=0, width=1)
    draw.line((86, 155, 86, 204), fill=0, width=1)
    draw.line((130, 155, 130, 204), fill=0, width=1)
    draw.line((0, 173, 176, 173), fill=0, width=1)

    draw.line((0, 204, 176, 204), fill=0, width=2)
    mask.paste(windIcon, (0, 208))
    draw.text((41, 206), '{}'.format(windDirection), font=tinyfont, fill=0)
    draw.text((0, 220), '{} {}'.format(windSpeed, windBeaufort),
              font=smallfont, fill=0)

    mask.paste(sunupIcon, (0, 244))
    mask.paste(sundownIcon, (88, 244))
    draw.line((0, 242, 176, 242), fill=0, width=2)
    draw.text((40, 244), '{}'.format(sunriseTime), font=smallfont, fill=0)
    draw.text((128, 244), '{}'.format(sunsetTime), font=smallfont, fill=0)

    rotatedMask = mask.rotate(180)
    # Turns mask upside down, this just happened to work best for my frame
    # with regards to which side the cable came out.
    epd.display_frame(epd.get_frame_buffer(rotatedMask))

if __name__ == '__main__':
    running = True
    while running:
        frameUpdate()
        time.sleep(600)
        # loops every 10 minutes and reupdates
