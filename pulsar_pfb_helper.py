# this module will be imported in the into your flowgraph
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


def calculate_delays(dm,freq,bw,nchan,drate):

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
        delays.append(z)
    
    return (delays)

import  time
import sys
import os

def log(vec,pref):
    ltp = time.gmtime()
    fn = pref + "%04d%02d%02d.csv" % (ltp.tm_year, ltp.tm_mon, ltp.tm_mday)
    f = open(fn, "a")
    f.write("%02d,%02d,%02d," % (ltp.tm_hour, ltp.tm_min, ltp.tm_sec))
    for val in vec:
        f.write("%.6f," % val)
    f.write("\n")
    f.close()
    return 0


    
