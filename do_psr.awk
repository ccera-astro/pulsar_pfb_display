BEGIN {FS=", *" 
       PSR_RATE=1.0
       }
/./ {sidh=$4
     sidm=$5
     sids=$6
     hh = sidh + (sidm/60.0)
     if (hh > TSTART && hh < TEND )
     {
		 for (i = 10; i <= NF; i++)
		 {
			 pdata[i-9] += $i
		 }
		 pcnt++
	 }
	 numdata = NF-10
	}
END {
       inc = 1
       incr = (1.0/PSR_RATE)/(numdata)
       incr *= 1000.0
       pdata[NF-9] = (pdata[0] + pdata[1] + pdata[numdata])/3
       pdata[NF-8] = (pdata[NF-9] + pdata[NF-6])/2
       
       #
       # Interpolate by about 33%
       #
       for (i = 1; i <= (numdata); i += 2)
       {
           intp[ic] = pdata[i]
           ic++
           intp[ic] = (pdata[i]+pdata[i+1])/2
           ic++
           intp[ic] = pdata[i+1]
           ic++
       }
       mn = 99999.999
       mx = -999999.999
       
       #
       # Find the pulse peak
       #
       for (i = 1; i < ic; i++)
       {
           if (intp[i] > mx)
           {
               mxl = i
               mx = intp[i]
           }
       }
       ip = mxl - 5
       op = ic/2
       
       #
       # Shift the pulse so that it's always phase-centered
       #
       for (i = 1; i <= ic; i++)
       {
           shifted[op] = intp[ip]
           op++
           ip++
           if (op > ic) op = 0
           if (ip > ic) ip = 0
       } 
       #
       # Scale the time-domain increment by interpolation ratio
       #
       incr /= ic/(numdata)
       for (i = 1; i <= ic; i++)
       {
			printf ("%f %.9f\n", (i-1)*incr, shifted[i]/pcnt)
	   }
	  }

