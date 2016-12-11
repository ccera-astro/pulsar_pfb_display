#include <stdio.h>
#include <math.h>
#include <unistd.h>
#include <stdlib.h>
#include <fcntl.h>
#include <string.h>

#define BINS 250

int
main (int argc, char **argv)
{
	double thebuffer[BINS];
	int bincnts[BINS];
	double prate = 1.39951319;
	double sdt = (double)1.0/2000.0;
	double tpb = (1.0/prate)/(double)BINS;
	double srate = 2000.0;
	short sample;
	int indx = 0;
	double segt = 0.0;
	long long totsamps = 0LL;
	int i;
	unsigned char input[2];
	unsigned long offset;
	unsigned long duration;
	
	if (argc != 5)
	{
		fprintf (stderr, "Usage: do_psr <pulserate> <samprate> <offset> <duration>\n");
		exit (1);
	}
	
	prate = atof(argv[1]);
	srate = atof(argv[2]);
	offset = atol(argv[3]);
	duration = atol(argv[4]);
	
	offset *= srate*sizeof(input);
	duration *= srate*sizeof(input);
	
	tpb = (1.0/prate)/(double)BINS;
	sdt = 1.0/srate;

	
	memset ((void *)thebuffer, 0, sizeof(thebuffer));
	memset ((void *)bincnts, 0, sizeof(bincnts));
	
	
	/*
	 * Get past WAV header
	 */
	for (i = 0; i < 16/sizeof(input); i++)
	{
		fread (input, sizeof(input), 1, stdin);
	}
	
	
	/*
	 * Get to desired offset
	 */
	fseek (stdin, offset, SEEK_SET);
	
	while (fread(&input, sizeof(input), 1, stdin) > 0)
	{
		double ds;
		
		/*
		 * Deal with data format
		 */
		sample = input[0]<<8;
		sample += (input[1]);
		
		/*
		 * Housekeeping on number of samples
		 */
		totsamps ++;
		
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
			if (indx >= BINS)
			{
				indx = 0;
			}
		}
	}
	
	/*
	 * Dump the folded buffer
	 */
	for (i = 0; i < BINS; i++)
	{
		fprintf (stdout, "%f %f\n", (double)i*tpb, thebuffer[i]/bincnts[i]);
	}
	exit (0);
}
		
		
		
	
