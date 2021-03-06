# Embedded file name: /usr/lib/enigma2/python/Components/j00zekComponents.py
import inspect
from os import path, system
from datetime import datetime
append2file = False
myDEBUG = '/tmp/j00zekComponents.log'
imageType = None

def isImageType(imgName = ''):
    global imageType
    if imageType is None:
        if path.exists('/usr/lib/enigma2/python/Plugins/SystemPlugins/VTIPanel'):
            imageType = 'vti'
        elif path.exists('/usr/lib/enigma2/python/Plugins/Extensions/Infopanel/'):
            imageType = 'openatv'
        elif path.exists('/usr/lib/enigma2/python/Blackhole'):
            imageType = 'blackhole'
        elif path.exists('/etc/init.d/start_pkt.sh'):
            imageType = 'pkt'
        else:
            imageType = 'unknown'
    if imgName.lower() == imageType.lower():
        return True
    else:
        return False
        return


def j00zekDEBUG(myText = None, Append = True):
    global myDEBUG
    global append2file
    if myDEBUG is None:
        return
    elif myText is None:
        return
    else:
        try:
            if append2file == False or Append == False:
                append2file = True
                f = open(myDEBUG, 'w')
            else:
                f = open(myDEBUG, 'a')
            f.write('%s\t%s\n' % (str(datetime.now()), myText))
            f.close()
            if path.getsize(myDEBUG) > 100000:
                system('sed -i -e 1,10d %s' % myDEBUG)
        except Exception as e:
            system('echo "Exception:%s" >> %s' % (str(e), myDEBUG))

        return


def isINETworking():
    try:
        import socket
        socket.setdefaulttimeout(0.5)
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect(('8.8.8.8', 53))
        return True
    except Exception as e:
        printDEBUG('%s' % str(e))

    try:
        import socket
        socket.setdefaulttimeout(0.5)
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect(('8.8.4.4', 53))
        return True
    except Exception as e:
        printDEBUG('%s' % str(e))

    printDEBUG('Error no internet connection. > %s' % str(e))
    return False