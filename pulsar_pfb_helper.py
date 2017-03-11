# this module will be imported in the into your flowgraph
import sys
import os
import time
import ephem
import operator
import math
import xmlrpclib
import numpy

AUDIO_ON=1
AUDIO_OFF=0
audio_state=AUDIO_OFF

BASEBAND_ON=1
BASEBAND_OFF=0
baseband_state=BASEBAND_OFF

def compute_cmap (nchan):
    cmap=[]
    start = int(nchan)/2
    start += 1
    for i in range(0,nchan):
        cmap.append(start)
        start = start+1
        if (start >= nchan):
            start = 0
    return cmap
        

def compute_rfi_map (flist, fc, bw, nchan):
    rmap=[1.0]*nchan
    incr = bw/nchan
    startf = fc-(bw/2.0)
    flist=flist.split(",")
    for i in range(0,nchan):
        for f in flist:
            if abs(startf-float(f)) <= incr:
                rmap[i] = 0.0
    
    return (rmap)

    
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


def calculate_delays(dm,freq,bw,nchan,mult):

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
    Dt = Dt / nchan

    #
    # The number of samples at the input bandwidth that represent the total smear time
    #
    perchan = float(bw/nchan)*Dt
    
    
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

def log(vec,pref,longitude,which,freq,bw,decln,st,en,xport):
    global audio_state
    global AUDIO_ON
    global AUDIO_OFF
    global baseband_state
    global BASEBAND_ON
    global BASEBAND_OFF
    
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
    
    logwindow = en - st
    logmid = st + (logwindow/2.0)
    
    #
    # 5 minutes for baseband data
    #
    bbst = logmid - (2.5 / 60.0)
    bben = logmid + (2.5 / 60.0)
    
    #
    # Deal with "audio" WAV file of de-dispersed, but not folded, data
    #
    if (sidh >= bbst and sidh <= bben and baseband_state == BASEBAND_OFF):
        try:
            s = xmlrpclib.Server('http://localhost:%d' % xport)
            bbfn = pref+"-baseband-%04d%02d%02d.bin" % (ltp.tm_year, ltp.tm_mon, ltp.tm_mday)
            s.set_baseband_file(bbfn)
            baseband_state = BASEBAND_ON
        except:
            pass
        
    if (sidh >= st and sidh <= en and audio_state == AUDIO_OFF):
        try:
            s = xmlrpclib.Server('http://localhost:%d' % xport)
            sfn  = pref+"-demod-%04d%02d%02d.wav" % (ltp.tm_year, ltp.tm_mon, ltp.tm_mday)
            s.set_soundfile (sfn)
            audio_state = AUDIO_ON
        except:
            pass
        
    if (sidh > en and audio_state == AUDIO_ON):
        try:
            s = xmlrpclib.Server('http://localhost:%d' % xport)
            s.set_soundfile("/dev/null")
            audio_state = AUDIO_OFF
        except:
            pass
            
    if (sidh > bben and baseband_state == BASEBAND_ON):
        try:
            s = xmlrpclib.Server('http://localhost:%d' % xport)
            s.set_baseband_file("/dev/null")
            baseband_state = BASEBAND_OFF
        except:
            pass

    if which == 0:
        if (sidh >= st and sidh <= en):
            f.write("%02d,%02d,%02d,%s," % (ltp.tm_hour, ltp.tm_min, ltp.tm_sec, curs))
            f.write("%9.4f,%f,%5.2f," % (freq/1.0e6, bw, decln))
            for val in vec:
                f.write("%.10f," % val)
            f.write("\n")
    else:
        f.write("%02d,%02d,%02d,%s," % (ltp.tm_hour, ltp.tm_min, ltp.tm_sec, curs))
        f.write("%9.4f,%f,%5.2f," % (freq/1.0e6, bw, decln))
        f.write("%.10f" % vec)
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

#
# Compute a de-dispersion filter
#  From Hankins, et al, 1975
#
# This code translated from dedisp_filter.c from Swinburne
#   pulsar software repository
#
def compute_dispfilter(dm,doppler,bw,centerfreq):
    npts = compute_disp_ntaps(dm,bw,centerfreq)
    tmp = numpy.zeros(npts, dtype=numpy.complex)
    M_PI = 3.14159265358
    DM = dm/2.41e-10
    #
    # Because astronomers are a crazy bunch, the "standard" calculation
    #   is in Mhz, rather than Hz
    #
    centerfreq = centerfreq / 1.0e6
    bw = bw / 1.0e6
    
    isign = int(bw / abs (bw))
    
    # Center frequency may be doppler shifted
    cfreq     = centerfreq / doppler

    # As well as the bandwidth..
    bandwidth = bw / doppler

    # Bandwidth divided among bins
    binwidth  = bandwidth / npts

    # Delay is an "extra" parameter, in usecs, and largely
    #  untested in the Swinburne code.
    delay = 0.0
    
    # This determines the coefficient of the frequency response curve
    # Linear in DM, but quadratic in center frequency
    coeff = -isign * 2.0*M_PI * DM / (cfreq*cfreq)
    
    # DC to nyquist/2
    n = 0
    for i in range(int(npts/2),npts):
        freq = (n + 0.5) * binwidth
        phi = coeff*freq*freq/(cfreq+freq) + (2.0*M_PI*freq*delay)
        tmp[i] = complex(math.cos(phi), math.sin(phi))
        n += 1

    # -nyquist/2 to DC
    n = int(npts/2)
    n *= -1
    for i in range(0,int(npts/2)):
        freq = (n + 0.5) * binwidth
        phi = coeff*freq*freq/(cfreq+freq) + (2.0*M_PI*freq*delay)
        tmp[i] = complex(math.cos(phi), math.sin(phi))
        n += 1
    
    
    return(numpy.fft.ifft(tmp))

#
# Compute minimum number of taps required in de-dispersion FFT filter
#
def compute_disp_ntaps(dm,bw,freq):
    NTLIMIT=65536*2
    #
    # Dt calculations are in Mhz, rather than Hz
    #    crazy astronomers....
    mbw = bw/1.0e6
    mfreq = freq/1.0e6

    f_lower = mfreq-(mbw/2)
    f_upper = mfreq+(mbw/2)

    # Compute smear time
    Dt = dm/2.41e-4 * (1.0/(f_lower*f_lower)-1.0/(f_upper*f_upper))

    # ntaps is now bandwidth*smeartime
    ntaps = bw*Dt
    if (ntaps < 32):
        ntaps = 32
    # special "flag" from command-line invoker to get around a bug
    #   in Gnu Radio involving the FFT filter implementation
    #   we can *never* increase the size of an FFT filter at runtime
    #   but can decrease it.  So there's a special "startup" flag (dm=1500.0)
    #   that causes us to return the NTLIMIT number of taps
    #
    if (dm >= 1500.0):
        ntaps = NTLIMIT
    if (ntaps > NTLIMIT):
        ntaps = NTLIMIT
    ntaps = int(math.log(ntaps) / math.log(2))
    ntaps = int(math.pow(2,ntaps+1))
    return(int(ntaps))
