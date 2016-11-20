# this module will be imported in the into your flowgraph
import sys
import os
import time
import ephem
import operator
import math


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

    #
    # Compute smear time
    #
    f_lower = 1.0/(f_lower*f_lower)
    f_upper = 1.0/(f_upper*f_upper)
    Dt = 4.149e6 * dm * (f_lower-f_upper)
    Dt = abs(Dt)
    Dt = Dt/1000.0
    
    #
    # The number of samples at the input bandwidth that represent the total smear time
    #
    samps = float(bw)*Dt
    
    #
    # Compute that in per-channel
    # Scale to detector rate
    #
    perchan = samps/float(nchan)
    perchan /= float(bw)/float(drate)
    
    
    delays=[]
    for d in range(0,nchan):
        z = float(d) * perchan
        z = round(z)
        z = int(z)
        delays.append(z*mult)
    
    return (delays)

import  time
import sys
import os

def log(vec,pref,longitude,which,freq,bw,decln):
    ltp = time.gmtime()
    fn = pref + "-profile-%04d%02d%02d.csv" % (ltp.tm_year, ltp.tm_mon, ltp.tm_mday)
    if (which == 1):
        fn = pref+"-tp-%04d%02d%02d.csv" % (ltp.tm_year, ltp.tm_mon, ltp.tm_mday)
    f = open(fn, "a")
    curs = cur_sidereal(longitude)
    f.write("%02d,%02d,%02d,%s," % (ltp.tm_hour, ltp.tm_min, ltp.tm_sec, curs))
    f.write("%9.4f,%f,%f," % (freq/1.0e6, bw, decln))
    if which == 0:
        for val in vec:
            f.write("%.6f," % val)
    else:
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

    
