#include <stdio.h>
#include <math.h>
#include <unistd.h>
#include <stdlib.h>
#include <fcntl.h>
#include <string.h>

#define DEFAULT_BINS 250

int
main (int argc, char **argv)
{
	double thebuffer[DEFAULT_BINS*5];
	int bincnts[DEFAULT_BINS*5];
	int numbins = DEFAULT_BINS;
	double prate =0.0;
	double sdt = 0.0;
	double tpb = 0.0;
	double srate = 0.0;
	short sample;
	int indx = 0;
	double segt = 0.0;
	long long totsamps = 0LL;
	int i;
	unsigned char input[2];
	unsigned long offset;
	unsigned long duration;
	int opt;
	char *fn;
	FILE *fp;
	
	if (argc < 2)
	{
		fprintf (stderr, "Usage: do_psr -p <pulserate> -s <samprate> -o <offset> -d <duration> -n <numbins> <infile>\n");
		exit (1);
	}
	
	/*
	 * Set defaults
	 */
	prate = -1;
	srate = -1;
	offset = 0L;
	duration = 3600L;
	numbins = 250;
	
	while ((opt = getopt(argc, argv, "p:n:d:s:o:")) != -1)
	{
		switch(opt)
		{
		case 'p':
		    prate = atof(optarg);
		    break;
		case 'n':
		    numbins = atoi(optarg);
		    if (numbins > (5*DEFAULT_BINS))
		    {
				fprintf (stderr, "Numbins exceeds the maximum of %d\n", (5*DEFAULT_BINS));
				exit (1);
			}
		    break;
		case 'd':
		    duration = atol(optarg);
		    break;
		case 's':
		    srate = atof(optarg);
		    break;
		case 'o':
		    offset = atol(optarg);
			break;
	    default:
	        fprintf (stderr, "Unknown option: '%c'\n", opt);
	        exit (1);
	    }
	 }
	 
	 /*
	  * Make sure that -p and -s have both been specified, and are valid
	  */
	 if (prate < 0.0)
	 {
		 fprintf (stderr, "-p must be specified, and must be > 0\n");
		 exit (1);
	 }
	 if (prate > 50.0)
	 {
		 fprintf (stderr, "-p specifies an unusually-high expected pulse rate\n");
	 }
	 
	 
	 if (srate < 0.0)
	 {
		 fprintf (stderr, "-s must be specified, and must be > 0\n");
		 exit (1);
	 }
	 if (srate < 100.0)
	 {
		 fprintf (stderr, "Warning: -s specifies an unusually-low sample rate\n");
     }
     
     fprintf (stderr, "Running with: prate %f srate %f bins %d\n", prate, srate, numbins);
     
     /*
      * Open input file
      */
	 fn = argv[optind];
	 fp = fopen (fn, "r");
	 if (fp == NULL)
	 {
		 perror ("Cannot open input file");
		 exit (1);
	 }
	 
	/*
	 * Offset/duration are given in seconds--convert to samples
	 */
	offset *= srate*sizeof(input);
	duration *= srate*sizeof(input);
	
	/*
	 * Calculate folding values from input parameters
	 */
	
	/*
	 * Time-per-bin
	 */
	tpb = (1.0/prate)/(double)numbins;
	
	fprintf (stderr, "Time-per-bin: %f\n", tpb);
	
	/*
	 * Dt produced by sample-rate
	 */
	sdt = 1.0/srate;
	
	fprintf (stderr, "Dt: %f\n", sdt);

	
	/*
	 * Zero-out out buffers
	 */
	memset ((void *)thebuffer, 0, sizeof(thebuffer));
	memset ((void *)bincnts, 0, sizeof(bincnts));
	
	/*
	 * Get to desired offset  (+16 to skip WAV header)
	 */
	fseek (stdin, offset+16, SEEK_SET);
	
	/*
	 * We read one 16-bit sample at a time, and process accordingly.
	 * This is reasonably efficient, since stdio takes care of buffering
	 *   for us.
	 */
	while (fread(&sample, sizeof(sample), 1, fp) > 0)
	{
		double ds;
		
		
		/*
		 * Housekeeping on number of samples
		 */
		totsamps ++;
		
		/*
		 * We're done, even though we haven't reached EOF
		 */
		if (totsamps > duration)
		{
			break;
		}
		
		/*
		 * Scale sample into something "reasonable" for a double
		 */
		ds = (double)sample / (double)16384.5;
		
		/*
		 * Add into accumulator buffer
		 */
		thebuffer[indx] += ds;
		
		/*
		 * Bump number of samples in this position
		 */
		bincnts[indx] += 1;
		
		/*
		 * Bump up our "segment" timer by the time-per-sample
		 */
		segt += sdt;
		
		/*
		 * One "segment" is one binwidth (pulsar-period / 256)
		 * If our segt after incrementing is >= binwidth, handle
		 *   bumping to next bin, and dealing with residual on
		 *   segment time.
		 */
		if (segt >= tpb)
		{
			/*
			 * Segt becomes whatever was left over from subtracting-out tpb
			 */
			segt = segt - tpb;
			
			/*
			 * Bump to the next bin
			 */
			indx ++;
			
			/*
			 * Handle wrap-around
			 */
			if (indx >= numbins)
			{
				indx = 0;
			}
		}
	}
	
	/*
	 * Dump the folded buffer
	 */
	for (i = 0; i < numbins; i++)
	{
		fprintf (stdout, "%f %f\n", (double)i*tpb, thebuffer[i]/bincnts[i]);
	}
	exit (0);
}
		
		
		
	
