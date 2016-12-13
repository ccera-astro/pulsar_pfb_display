# this module will be imported in the into your flowgraph
import sys
import os
import time
import ephem
import operator
import math
import xmlrpclib

AUDIO_ON=1
AUDIO_OFF=0
audio_state=AUDIO_OFF

def f_pad(filt,nc):
    f = list(filt)
    
    l = len(f)
    l = float(l)
    nl = math.ceil(l/float(nc))*nc
    nl = int(nl)
    nl = nl-int(l)
    low = int(nl/2)
    high = int(nl)-low
    return([0.0]*low+f+[0.0]*high)


def calculate_delays(dm,freq,bw,nchan,drate,mult):

    f_lower = freq-(bw/2.0)
    f_upper = freq+(bw/2.0)
    
    f_lower /= 1.0e6
    f_upper /= 1.0e6
    
    f1 = 1.0/(f_lower*f_lower)
    f2 = 1.0/(f_upper*f_upper)

    #
    # Compute smear time
    #
    Dt = 4.15e3 * dm * (f2-f1)
    Dt = abs(Dt)

    #
    # The number of samples at the input bandwidth that represent the total smear time
    #
    samps = float(bw)*Dt
    
    #
    # Compute that in per-channel
    # Scale to detector rate
    #
    perchan = samps/float(nchan)
    
    delays=[]
    for d in range(0,nchan):
        z = float(d) * perchan
        z = round(z)
        z = int(z)
        delays.append(z*mult)
    
    #
    # invert delays
    #
    dl = len(delays)
    dl -= 1
    idelays = []
    for i in range(0,len(delays)):
        idelays.append(delays[(dl-i)])
    return (delays)

import  time
import sys
import os

def log(vec,pref,longitude,which,freq,bw,decln,st,en,rawf):
    global audio_state
    global AUDIO_ON
    global AUDIO_OFF
    
    ltp = time.gmtime()
    fn = pref + "-profile-%04d%02d%02d.csv" % (ltp.tm_year, ltp.tm_mon, ltp.tm_mday)
    if (which == 1):
        fn = pref+"-tp-%04d%02d%02d.csv" % (ltp.tm_year, ltp.tm_mon, ltp.tm_mday)
    f = open(fn, "a")
    curs = cur_sidereal(longitude)
    stimes = curs.split(",")
    sidh = float(stimes[0])
    sidh += float(stimes[1])/60.0
    sidh += float(stimes[2])/3600.0
    
    #
    # Deal with "uadio" WAV file of de-dispersed, but not folded, data
    #
    if (sidh >= st and sidh < en and audio_state == AUDIO_OFF):
        try:
            s = xmlrpclib.Server('http://localhost:10001')
            sfn = rawf
            
            if (rawf == "@auto@"):
                mid = (float(st)+float(en))/2.0
                midh = int(mid)
                midm = mid-float(midh)
                midm *= 60.0
                sfn  = pref+"-psr%02d%02d+%02d-%04d%02d%02d.wav" % (midh, midm, decln, ltp.tm_year, ltp.tm_mon, ltp.tm_mday)
            s.set_soundfile (sfn)
            audio_state = AUDIO_ON
        except:
            pass
        
    if (sidh > en and audio_state == AUDIO_ON):
        try:
            s = xmlrpclib.Server('http://localhost:10001')
            s.set_soundfile("/dev/null")
            audio_state = AUDIO_OFF
        except:
            pass

    if which == 0:
        if (sidh >= st and sidh <= en):
            f.write("%02d,%02d,%02d,%s," % (ltp.tm_hour, ltp.tm_min, ltp.tm_sec, curs))
            f.write("%9.4f,%f,%5.2f," % (freq/1.0e6, bw, decln))
            for val in vec:
                f.write("%.4f," % val)
            f.write("\n")
    else:
        f.write("%02d,%02d,%02d,%s," % (ltp.tm_hour, ltp.tm_min, ltp.tm_sec, curs))
        f.write("%9.4f,%f,%5.2f," % (freq/1.0e6, bw, decln))
        f.write("%11.8f" % vec)
        f.write("\n")
    f.close()
    return 0

def cur_sidereal(longitude):
    longstr = "%02d" % int(longitude)
    longstr = longstr + ":"
    longitude = abs(longitude)
    frac = longitude - int(longitude)
    frac *= 60
    mins = int(frac)
    longstr += "%02d" % mins
    longstr += ":00"
    x = ephem.Observer()
    x.date = ephem.now()
    x.long = longstr
    jdate = ephem.julian_date(x)
    tokens=str(x.sidereal_time()).split(":")
    hours=int(tokens[0])
    minutes=int(tokens[1])
    seconds=int(float(tokens[2]))
    sidt = "%02d,%02d,%02d" % (hours, minutes, seconds)
    return (sidt)


def smear_time(dm,bw,freq):
    f_lower = freq-(bw/2.0)
    f_upper = freq+(bw/2.0)
    
    f_lower /= 1.0e6
    f_upper /= 1.0e6
    
    f1 = 1.0/(f_lower*f_lower)
    f2 = 1.0/(f_upper*f_upper)

    #
    # Compute smear time
    #
    Dt = 4.15e3 * dm * (f2-f1)
    Dt = abs(Dt)
    
    return (Dt)
