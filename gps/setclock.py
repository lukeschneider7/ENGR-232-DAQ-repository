#Source: https://m0iax.com/2018/11/30/setting-the-raspberry-pi-system-time-using-a-gps/
#For: setting gps internal clock to GPS UTC (4 hours ahead)
import os
import sys
import time
from gps import *

print ‘Set Raspberry Pi clock to GPS time’

try:
    gpsd = gps(mode=WATCH_ENABLE)
except:
    print ‘ERROR: No GPS found, the time has not been set’
    sys.exit()

   while True:
       #wait until the next GPSD time tick
      gpsd.next()
      if gpsd.utc != None and gpsd.utc != ”:
     #gpsd.utc is formatted like”2022-04-20T17:32:04.000Z”
     #convert it to a form the date -u command will accept: “20220419 17:32:04”
     #use python slice notation [start:end] (where end desired end char + 1)
     # gpsd.utc[0:4] is “2022”
     # gpsd.utc[5:7] is “04”
     # gpsd.utc[8:10] is “19” 
     gpsutc = gpsd.utc[0:4] + gpsd.utc[5:7] + gpsd.utc[8:10] + ‘ ‘ + gpsd.utc[11:19]
     os.system(‘sudo date -u –set=”%s”‘ % gpsutc)
     sys.exit()
