# Embedded file name: /usr/lib/enigma2/python/Components/j00zekBING.py
import json
import urllib
import urllib2
from os.path import exists as OsPathExists
try:
    from Components.j00zekComponents import isINETworking
except Exception:
    from j00zekComponents import isINETworking

def getPicOfTheDay(CountryCode = 'pl_PL', downloadPathAndFileName = '/usr/share/enigma2/BlackHarmony/icons/BingPicOfTheDay.jpg'):
    retVal = False
    url = 'http://www.bing.com/HPImageArchive.aspx?format=js&idx=0&n=1&mkt=%s' % CountryCode
    try:
        if isINETworking():
            response = urllib2.urlopen(url, timeout=1)
            response = response.read()
            response = json.loads(response)
            if 'images' in response:
                images = response['images']
                for i in range(len(images)):
                    url = 'http://www.bing.com' + images[i]['url']
                    urllib.urlretrieve(url, downloadPathAndFileName)
                    if OsPathExists(downloadPathAndFileName):
                        retVal = True
                        break

    except Exception as e:
        print e

    return retVal


if __name__ == '__main__':
    getPicOfTheDay()