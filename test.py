import time
import logging
import os
import textwrap
import urllib2
import json

print('Time: {}'.format(time.strftime('%d.%m.%y %H:%M')))

urlWeather = urllib2.urlopen(
    'https://api.met.no/weatherapi/locationforecast/2.0/compact?lat=58.8474&lon=5.7166')
# Exchange the link above with your location.
dataUrl = urlWeather.read()
data = json.loads(dataUrl)
urlLegend = urllib2.urlopen('https://api.met.no/weatherapi/weathericon/2.0/legends')
legendUrl = urlLegend.read()
legend = json.loads(legendUrl)

stats = data['properties']['timeseries']

currentIcon = stats[0]['data']['next_1_hours']['summary']['symbol_code']
currentStatus = legend[currentIcon]['desc_en']
print(currentStatus)


urlReady = False
while not urlReady:
    url = urllib2.urlopen(
        'https://api.met.no/weatherapi/locationforecast/2.0/complete?lat=58.8474&lon=5.7166')
    # Exchange the link above with your location.
    print(url.getcode())
    if(url.getcode() == 200):
        attempts = 1
        dataUrl = url.read()
        data = json.loads(dataUrl)
        print('Weather data URL successfully opened. Weather station update: {}'
              .format(data['properties']['meta']['updated_at']))
        urlReady = True
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
