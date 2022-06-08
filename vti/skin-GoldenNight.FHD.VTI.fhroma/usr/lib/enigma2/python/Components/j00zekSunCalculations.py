# Embedded file name: /usr/lib/enigma2/python/Components/j00zekSunCalculations.py
from Components.config import config
from Components.Element import cached
from decimal import Decimal as dec
DBG = False
if DBG:
    from Components.j00zekComponents import j00zekDEBUG
import math
import datetime
import json
import time

class Sun:

    def getSunriseTime(self, longitude, latitude):
        return self.calcSunTime(longitude, latitude, True)

    def getSunsetTime(self, longitude, latitude):
        return self.calcSunTime(longitude, latitude, False)

    def calcSunTime(self, longitude, latitude, isRiseTime, zenith = 90.8):
        longitude = float(longitude)
        latitude = float(latitude)
        now = datetime.datetime.now()
        day = now.day
        month = now.month
        year = now.year
        TO_RAD = math.pi / 180
        N1 = math.floor(275 * month / 9)
        N2 = math.floor((month + 9) / 12)
        N3 = 1 + math.floor((year - 4 * math.floor(year / 4) + 2) / 3)
        N = N1 - N2 * N3 + day - 30
        lngHour = longitude / 15
        if isRiseTime:
            t = N + (6 - lngHour) / 24
        else:
            t = N + (18 - lngHour) / 24
        M = 0.9856 * t - 3.289
        L = M + 1.916 * math.sin(TO_RAD * M) + 0.02 * math.sin(TO_RAD * 2 * M) + 282.634
        L = self.forceRange(L, 360)
        RA = 1 / TO_RAD * math.atan(0.91764 * math.tan(TO_RAD * L))
        RA = self.forceRange(RA, 360)
        Lquadrant = math.floor(L / 90) * 90
        RAquadrant = math.floor(RA / 90) * 90
        RA = RA + (Lquadrant - RAquadrant)
        RA = RA / 15
        sinDec = 0.39782 * math.sin(TO_RAD * L)
        cosDec = math.cos(math.asin(sinDec))
        cosH = (math.cos(TO_RAD * zenith) - sinDec * math.sin(TO_RAD * latitude)) / (cosDec * math.cos(TO_RAD * latitude))
        if cosH > 1:
            return {'status': False,
             'msg': 'the sun never rises on this location (on the specified date)'}
        if cosH < -1:
            return {'status': False,
             'msg': 'the sun never sets on this location (on the specified date)'}
        if isRiseTime:
            H = 360 - 1 / TO_RAD * math.acos(cosH)
        else:
            H = 1 / TO_RAD * math.acos(cosH)
        H = H / 15
        T = H + RA - 0.06571 * t - 6.622
        UT = T - lngHour
        UT = self.forceRange(UT, 24)
        now_timestamp = time.time()
        offset = datetime.datetime.fromtimestamp(now_timestamp) - datetime.datetime.utcfromtimestamp(now_timestamp)
        offset = divmod(offset.seconds, 3600)[0]
        LT = UT + offset
        LT = self.forceRange(LT, 24)
        hr = self.forceRange(int(UT), 24)
        min = round((UT - int(UT)) * 60, 0)
        Lhr = self.forceRange(int(LT), 24)
        if min >= 10:
            UTCtime = '%s:%s' % (int(hr), int(min))
            TZtime = '%s:%s' % (int(Lhr), int(min))
        else:
            UTCtime = '%s:0%s' % (int(hr), int(min))
            TZtime = '%s:0%s' % (int(Lhr), int(min))
        return {'status': True,
         'UTCtimeDec': UT,
         'TZtimeDec': LT,
         'UTChr': hr,
         'min': min,
         'TZhr': Lhr,
         'UTCtime': UTCtime,
         'TZtime': TZtime}

    def forceRange(self, v, max):
        if v < 0:
            return v + max
        if v >= max:
            return v - max
        return v


class geo:
    Position = {}

    def __init__(self):
        if DBG:
            j00zekDEBUG('[geo:__init__] >>>')
        if len(geo.Position) == 0:
            self.getPosition()

    def getPosition(self):
        if DBG:
            j00zekDEBUG('[self:getPosition] >>>')
        try:
            geo.Position['latitude'] = float(config.plugins.WeatherPlugin.Entry[0].geolatitude.value)
            geo.Position['longitude'] = float(config.plugins.WeatherPlugin.Entry[0].geolongitude.value)
            if DBG:
                j00zekDEBUG('[self:getPosition] configured latitude=%s, longitude=%s' % (geo.Position['latitude'], geo.Position['longitude']))
        except Exception as e:
            if DBG:
                j00zekDEBUG("[self:getPosition] >>> Error getting configured data: '%s'" % str(e))
            try:
                from twisted.web.client import getPage
                from twisted.web.client import downloadPage
                from twisted.web import client, error as weberror
            except:
                if DBG:
                    j00zekDEBUG('Error importing twisted. Something wrong with the image?')

            self.getWebData()

    def getLatitude(self):
        if DBG:
            j00zekDEBUG("self:getLatitude()='%s'" % geo.Position['latitude'])
        return geo.Position['latitude']

    def getLongitude(self):
        if DBG:
            j00zekDEBUG("self:getLongitude()='%s'" % geo.Position['longitude'])
        return geo.Position['longitude']

    def getWebData(self):
        if DBG:
            j00zekDEBUG('[geo:getWebData] >>>')

        def dataError(error = ''):
            if DBG:
                j00zekDEBUG('[geo:getWebData] Error downloading data %s, trying again' % str(error))

        def readData(data):
            if DBG:
                j00zekDEBUG("[geo:getWebData] >>> Received data: '%s'" % str(data))
            try:
                geo.Position = json.loads(data.strip()[1:-1])
                if DBG:
                    j00zekDEBUG("latitude='%s'" % geo.Position['latitude'])
                    j00zekDEBUG("longitude='%s'" % geo.Position['longitude'])
            except Exception as e:
                j00zekDEBUG("[geo:getWebData] >>> Exception: '%s'" % str(e))

        getPage('https://dcinfos.abtasty.com/geolocAndWeather.php').addCallback(readData).addErrback(dataError)