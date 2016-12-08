BEGIN {FS=", *" 
       PSR_RATE=1.0
       PRM=1.0
       }
/./ {sidh=$4
     sidm=$5
     sids=$6
     hh = sidh + (sidm/60.0)
     if (hh > TSTART && hh < TEND )
     {
		 for (i = 10; i <= NF; i++)
		 {
			 pdata[i-9] = $i
		 }
		 pcnt++
		#
		 # Interpolate by about 33%
		 #
		 ic = 1
		pdata[NF-9] = (pdata[0] + pdata[1] + pdata[numdata])/3
		pdata[NF-8] = (pdata[NF-9] + pdata[NF-6])/2
		for (i = 1; i <= (numdata); i += 2)
		{
		   intp[ic] += pdata[i]
		   ic++
		   intp[ic] += ((pdata[i]+pdata[i+1])/2)
		   ic++
		   intp[ic] += pdata[i+1]
		   ic++
		}
		numinterp = ic-1
	    numdata = NF-10
	 }
	}
END {
       PSR_RATE /= PRM
       incr = (1.0/PSR_RATE)/(numdata)
       incr *= 1000.0
       incr /= numinterp/numdata
  
       mn = 9e11
       mx = -9e11
       
       #
       # Find the pulse peak
       #
       for (i = 1; i < numinterp; i++)
       {
           if (intp[i] > mx)
           {
               mxl = i
               mx = intp[i]
           }
       }
       ip = mxl - 7
       if (ip < 1) ip = 1
       op = numinterp/2
       
       #
       # Shift the pulse so that it's always phase-centered
       #
       for (i = 1; i <= numinterp; i++)
       {
           shifted[op] = intp[ip]
           op++
           ip++
           if (op > numinterp) op = 1
           if (ip > numinterp) ip = 1
       } 
       #
       # Scale the time-domain increment by interpolation ratio
       #
       for (i = 1; i <= numinterp; i++)
       {
			printf ("%f %.9f\n", (i-1)*incr, shifted[i]/pcnt)
	   }
	  }

