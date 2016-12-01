BEGIN {origfn=""
       ndx=1
       }
/./ {
       if (FILENAME != origfn)
       {
           origfn = FILENAME
           ndx = 1
           fc++
       }
       td[ndx] += $1
       pd[ndx] += $2
       ndx++
       maxndx = ndx
       }

END {
        for (i = 1; i < ndx; i++)
        {
             printf ("%f %.9f\n", td[i]/fc, pd[i]/fc)
        }
    }
    
