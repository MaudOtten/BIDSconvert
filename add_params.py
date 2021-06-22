#!/usr/bin/python

import os
import json
import re

from os.path import isfile, join
from os import walk


def add_vals_postrename(mypath):
	
	# TODO include values to be added
	# values below calculated inlog(/mnt/projects/LISA/BIDS_maud/scripts/)
	# get required values for calculations from sequence description on Philips scanner
	
	EES_fmri = 4.3820e-04
	EES_dwi = 4.6741e-04
	slicetiming = [0, 1.2450, 0.0593,    1.3043,    0.1186,    1.3636,    0.1779,    1.4229,    0.2371,    1.4821,    0.2964,    1.5414,    0.3557,    1.6007,    0.4150,    1.6600,    0.4743,    1.7193,    0.5336,    1.7786,    0.5929,    1.8379,    0.6521,    1.8971,    0.7114,    1.9564,    0.7707,    2.0157,    0.8300,   2.0750,    0.8893,    2.1343,    0.9486,    2.1936,    1.0079,    2.2529,    1.0671,    2.3121,    1.1264,    2.3714,    1.1857,    2.4307]
	PED_fmri = 'i'
	PED_dwi = 'i'
	
	PED_dwi_aref = 'i-'
	PED_dwi_pref = 'i'
	PED_fm = 'i-'
	taskname = 'rest'
	
	# leave following empty
	inf = ''
	ses = ''
	sub = ''
	
	for (dirpath, dirnames, filenames) in walk(mypath):
		filenames = [filename for filename in filenames if '.json' in filename]
		
		for fn in filenames:
		
			## EXAMPLE ENTRY ##
			#
			#if 'path-label' in dirpath and 'file-label' in fn:
			#with open(join(dirpath, fn), 'r') as f:
			#	data = json.load(f)
			#
			#data['PhaseEncodingDirection'] = 'i'
			#data['TotalReadoutTime'] = round(predefined_value * (data["ReconMatrixPE"] - 1), 4)
			#
			###
	
			if 'fmap' in dirpath:
				# find fieldmap for EPI
				if 'bold' in fn and fn.endswith('epi.json'):
					with open(join(dirpath, fn), 'r') as f:
						data = json.load(f)
					
					data['PhaseEncodingDirection'] = PED_fm
					data['EffectiveEchoSpacing'] = EES_fmri
					data['TotalReadoutTime'] = round(EES_fmri * (data["ReconMatrixPE"] - 1), 4)
					
					boldp = dirpath[:-5]
					
					# find sub name
					rgx = re.compile('sub-(.+?)_')
					sub_ext = re.findall(rgx, fn)
					if sub_ext:
						sub = 'sub-' + sub_ext[0] + '_'
					
					# find session nr if included in filename
					rgx = re.compile('ses-..')
					ses_ext = re.findall(rgx, fn)
					if ses_ext:
						ses = ses_ext[0] + '_'
					
					boldfn = join(boldp, 'func', sub + ses + 'task-rest_run-1_bold.nii.gz')
					
					if isfile(boldfn):
						inf = join(ses[:-1], 'func',  sub + ses + 'task-rest_run-1_bold.nii.gz')
						data['IntendedFor'] = inf
					else:
						print('Intended file not found for: {}'.format(boldfn))
					
					# dump to formatted string
					string = json.dumps(data, indent=8)
					string = string + '\n'
					
					# write new json with same name
					with open(join(dirpath, fn), 'w') as outfile:
						outfile.write(string)

				# find fieldmap for dwi
				elif 'dwi' in fn and fn.endswith('epi.json'):
					
					with open(join(dirpath, fn), 'r') as f:
						data = json.load(f)
					
					# adjust PED for diff files, values defined at top of function
					if 'AP' in fn:
						data['PhaseEncodingDirection'] = PED_dwi_aref
					elif 'PA' in fn:
						data['PhaseEncodingDirection'] = PED_dwi_pref
					
					data['TotalReadoutTime'] = round(EES_dwi * (data["ReconMatrixPE"] - 1), 4)
					
					boldp = dirpath[:-5]
					
					# find sub name
					rgx = re.compile('sub-(.+?)_')
					sub_ext = re.findall(rgx, fn)
					if sub_ext:
						sub = 'sub-' + sub_ext[0] + '_'
					
					# find session nr if included in filename
					rgx = re.compile('ses-..')
					ses_ext = re.findall(rgx, fn)
					if ses_ext:
						ses = ses_ext[0] + '_'
					
					boldfn = join(boldp, 'dwi', sub + ses + 'run-1_dwi.nii.gz')
					
					if isfile(boldfn):
						inf = join(ses[:-1], 'dwi', sub + ses + 'run-1_dwi.nii.gz')
						data['IntendedFor'] = inf
					else:
						print('Intended file not found for: {}'.format(fn))
					
					# dump to formatted string
					string = json.dumps(data, indent=8)
					string = string + '\n'
					
					with open(join(dirpath, fn), 'w') as outfile:
						outfile.write(string)
			
			# find reference volume for ASL	
			elif 'perf' in dirpath and 'm0scan' in fn:
				
				# find sub name
				rgx = re.compile('sub-(.+?)_')
				sub_ext = re.findall(rgx, fn)
				if sub_ext:
					sub = 'sub-' + sub_ext[0] + '_'
				
				# find session nr if included in filename
				rgx = re.compile('ses-..')
				ses_ext = re.findall(rgx, fn)
				if ses_ext:
					ses = ses_ext[0] + '_'
				
				boldfn1 = join(dirpath, sub + ses + 'asl1.nii.gz')
				boldfn2 = join(dirpath, sub + ses + 'asl2.nii.gz')
				boldfn3 = join(dirpath, sub + ses + 'asl.nii.gz')
				
				if isfile(boldfn1) and isfile(boldfn2):
					with open(join(dirpath, fn), 'r') as f:
						data = json.load(f)
					
					inf = [join(ses[:-1], 'perf', sub + ses + 'asl1.nii.gz'), join(ses[:-1], 'perf', sub + ses + 'asl2.nii.gz')]
					data['IntendedFor'] = inf
					
					# dump to formatted string
					string = json.dumps(data, indent=8)
					string = string + '\n'
					
					# write new json with same name
					with open(join(dirpath, fn), 'w') as outfile:
						outfile.write(string)
				
				elif isfile(boldfn3):
					with open(join(dirpath, fn), 'r') as f:
						data = json.load(f)
					
					inf = join(ses[:-1], 'perf', sub + ses + 'asl.nii.gz')
					data['IntendedFor'] = inf
					
					# dump to formatted string
					string = json.dumps(data, indent=8)
					string = string + '\n'
					
					# write new json with same name
					with open(join(dirpath, fn), 'w') as outfile:
						outfile.write(string)
				else:
					print('Intended file not found for: {}'.format(fn))
			
			# find EPI
			elif 'func' in dirpath and 'task-rest' in fn:					
				
				with open(join(dirpath, fn), 'r') as f:
					data = json.load(f)
				
				data['TaskName'] = taskname # only included fMRI protocol
				data['PhaseEncodingDirection'] = PED_fmri
				data['EffectiveEchoSpacing'] = EES_fmri
				data['TotalReadoutTime'] = round(EES_fmri * (data["ReconMatrixPE"] - 1), 4)
				
				# values calculated in script check_slicetiming.m (/mnt/projects/LISA/BIDS_maud/scripts/)
				data['SliceTiming'] = slicetiming
				
				# dump to formatted string
				string = json.dumps(data, indent=8)
				string = string + '\n'
				
				# write new json with same name
				with open(join(dirpath, fn), 'w') as outfile:
					outfile.write(string)
				
			# find dwi
			elif 'dwi' in dirpath and 'dwi' in fn:					
				
				with open(join(dirpath, fn), 'r') as f:
					data = json.load(f)
				
				data['PhaseEncodingDirection'] = PED_dwi
				data['EffectiveEchoSpacing'] = EES_dwi
				data['TotalReadoutTime'] = round(EES_dwi * (data["ReconMatrixPE"] - 1), 4)
				
				# dump to formatted string
				string = json.dumps(data, indent=8)
				string = string + '\n'
				
				# write new json with same name
				with open(join(dirpath, fn), 'w') as outfile:
					outfile.write(string)
				
	
	# Finish strong
	print('\n-- Added values successfully. --\n')
	return 0


if __name__ == '__main__':
	add_vals_postrename('../data/check_data/sub-mabs01/')
