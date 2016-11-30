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
	}
END {
       incr = (1.0/PSR_RATE)/(NF-10)
       incr *= 1000.0
       for (i = 1; i <= (NF-10); i++)
       {
            printf ("%f %9.6f\n", (i-1) * incr, pdata[i]/pcnt)
       }
    }
