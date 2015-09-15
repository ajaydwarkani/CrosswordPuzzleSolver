#!/usr/bin/env python
#--------------------------------------------------------------------
#
#   @author Ajay Kumar <ajaydwarkani@gmail.com
#   
#   @version 1.00
#
#   @copyright 2015
#
#--------------------------------------------------------------------

import sys
import os
import time
import math

# Checking for OrderedDict functionality.
try:
	from collections import OrderedDict
except ImportError:
    try:
        from ordereddict import OrderedDict
    except ImportError:
    	sys.exit('module "OrderedDict" is missing. Please install it by running "pip install ordereddict"')

from SolveCrossword import *




def checkPythonVersion():
	print 'Python version: %s.%s.%s\n' % (sys.version_info[0], sys.version_info[1], sys.version_info[2])
	if not (sys.version_info[0] == 2 and sys.version_info[1] == 6):
		sys.exit('ERROR: Unsupported Python version. Please use Python version "2.6.x"')


if __name__ == '__main__':
	start = time.clock()
	print('Running...%s' % (os.path.basename(sys.argv[0])))

	checkPythonVersion()

	urlCrossword = "http://www.onlinecrosswords.net/printable-daily-crosswords-1.php"
	noOfCells = 15
		
	croswordSolver = SolveCrossword(urlCrossword, noOfCells = noOfCells)
	croswordSolver.printSolvedCrossword()

	end = time.clock()
	minutes, seconds = divmod(end - start, 60)
	if minutes > 0:
		print("\nTime elapsed = %d min %d secs" % (minutes, seconds))
	else:
		print("\nTotal time elapsed - %.2f secs" % (seconds))
	
	print 'Done.'  