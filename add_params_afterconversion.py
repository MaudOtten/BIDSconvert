#!/usr/bin/python

import os
import json
import re

from os.path import isfile, join
from os import walk


def add_values(mypath):
	
	# TODO include values to be added
	
	# example values to add
	#EES = 0
	#slicetiming = [0, 0]
	#PED_fmri = 'i'
	#taskname = 'rest'
	
	# leave following empty
	inf = ''
	ses = ''
	sub = ''
	
	for (dirpath, dirnames, filenames) in walk(mypath):
		filenames = [filename for filename in filenames if '.json' in filename]
		
		for fn in filenames:
			
			# TODO add entry for each type of file to add to
			
#			## EXAMPLE ENTRY ##
#			
#			if 'path-label' in dirpath and 'file-label' in fn:
#			with open(join(dirpath, fn), 'r') as f:
#				data = json.load(f)
#			
#			data['PhaseEncodingDirection'] = 'i'
#			data['TotalReadoutTime'] = round(predefined_value * (data["ReconMatrixPE"] - 1), 4)
#			
#			# dump to formatted string
#			string = json.dumps(data, indent=8)
#			string = string + '\n'
#			
#			# write new json with same name
#			with open(join(dirpath, fn), 'w') as outfile:
#				outfile.write(string)
#			
#			###
	
	# Finish strong
	print('\n-- Added values successfully. --\n')
	return 0


if __name__ == '__main__':
	add_values('path/to/subject')
