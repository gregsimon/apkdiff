
#include <stdio.h>
#include <string.h>
#include <stdlib.h>

#include "patch.h"


void help(const char*);


int main (int argc, char** argv)
{
	ApkPatcher patcher;
	const char* fromfile = 0;
	const char* patchfile = 0;
	const char* destfile = 0;
	

	for (int i=1; i<argc; i++)
	{
		if ('-' == argv[i][0]) 
		{
			switch (argv[i][1]) 
			{
				case 'h':
					help(argv[0]);
					return 0;
					break;

				default:
					fprintf(stderr, "Unrecognized argument '%s'\n", argv[i]);
			}
		}
		else
		{
			if (!fromfile)
				fromfile = argv[i];
			else if (!destfile) 
				destfile = argv[i];
			else
				patchfile = argv[i];

		}
	}


	if (!fromfile || !patchfile || !destfile) {
		help(argv[0]);
		return 0;
	}

	patcher.patch(fromfile, destfile, patchfile);


	return 0;
}


void help(const char* exename)
{
	printf("Usage: %s [options] <fromfile> <destfile> <patchfile>\n", exename);
}