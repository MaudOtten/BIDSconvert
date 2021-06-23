import os



def create_key(template, outtype=('nii.gz'), annotation_classes=None):
	if template is None or not template:
		raise valueerror('template must be a valid format string')
	return template, outtype, annotation_classes


def infotodict(seqinfo):
	"""Heuristic evaluator for determining which runs belong where

	allowed template fields - follow python string module:

	item: index within category
	subject: participant id
	seqitem: run number during scanning
	subindex: sub index within group
	session: scan index for longitudinal acq
	
	"""


	# Protocols for DRCMR - Copenhagen
	# TODO Adjust keys for correct naming for each sequence included in study
	
	t1wmprage = create_key('{s[subject]}/{s[session]}/anat/{s[subject]}_{s[session]}_acq-{s[mod]}_T1w')
	
	t2w = create_key('{s[subject]}/{s[session]}/anat/{s[subject]}_{s[session]}_T2w')
	
	flair = create_key('{s[subject]}/{s[session]}/anat/{s[subject]}_{s[session]}_acq-{s[mod]}_FLAIR')
	
	flairME = create_key('{s[subject]}/{s[session]}/swi/{s[subject]}_{s[session]}_echo-{s[mod]}_GRE')
	
	dwi = create_key('{s[subject]}/{s[session]}/dwi/{s[subject]}_{s[session]}_run-{s[run]}_dwi')
	
	dwi_ref = create_key('{s[subject]}/{s[session]}/fmap/{s[subject]}_{s[session]}_acq-dwi_dir-{s[mod]}_run-{s[run]}_epi')
	
	asl = create_key('{s[subject]}/{s[session]}/perf/{s[subject]}_{s[session]}_asl')
	
	asl_ref = create_key('{s[subject]}/{s[session]}/perf/{s[subject]}_{s[session]}_m0scan')
	
	rest_PA = create_key('{s[subject]}/{s[session]}/fmap/{s[subject]}_{s[session]}_acq-bold_dir-{s[dir]}_run-{s[run]}_epi')
	
	rest = create_key('{s[subject]}/{s[session]}/func/{s[subject]}_{s[session]}_task-rest_run-{s[run]}_bold')

	other = create_key('{s[subject]}/{s[session]}/other/{s[subject]}_{s[session]}_run-{s[run]}_acq-{s[mod]}_other')
	
	
	# TODO Every protocol needs an entry here, NOTE: only included DRCMR protocols + 'other' (as check for leftover files)
	info = {t1wmprage: [], t2w: [], flair: [], flairME: [], dwi: [], dwi_ref: [], asl: [], asl_ref: [], rest_PA : [], rest: [], other: []}
	
	
	last_run = len(seqinfo)
	
	#TODO: Find a better way to do this run counting..
	t1wmprage_run = 0
	t2w_run = 0
	flair1mm_run = 0
	flairGH_run = 0
	flairother_run = 0
	dwi_run = 0
	dwipref_run = 0
	dwiaref_run = 0
	asl_run = 0
	aslref_run = 0
	rest_run = 0
	restPA_run = 0
	other_run = 0
	flair3d1_run = 0
	flair3d2_run = 0
	flair3d3_run = 0
	flair3d4_run = 0
	flair3d5_run = 0
	flair3d6_run = 0
	
	# Loop through each file sequence identified by heudiconv
	for idx, s in enumerate(seqinfo):
		
		if s.ProtocolName  is not None:
			
			acq = s.Manufacturer
			#print('\n', s, '\n')
			
			
			######################################################################
			# TODO filter based on multiple variables for each sequence in study #
			######################################################################

			#T1w
			if ('T1w' in s.ProtocolName):
				if round(s.EchoTime, 3) > 0.006:
					t1wTE_run += 1
					modus = 'highTE'
					info[t1wmprage].append({'item': s.ProtocolName, 'acq': acq, 'mod': modus, 'run': t1wTE_run, 'idx': idx})
				
				else:
					t1wmprage_run += 1
					modus = 'mprage'
					info[t1wmprage].append({'item': s.ProtocolName, 'acq': acq, 'mod': modus, 'run': t1wmprage_run, 'idx': idx})
			
			# T2W
			elif ('T2w' in s.ProtocolName):
				t2w_run += 1
				modus = 't2'
				info[t2w].append({'item': s.ProtocolName, 'acq': acq, 'mod': modus, 'run': t2w_run, 'idx': idx})
			
			# FLAIR
			elif ('FLAIR' in s.ProtocolName):
				if s.InversionTime == 1.65 and s.RepetitionTime == 4.8:
					flair1mm_run += 1
					modus = '1mmiso'
					info[flair].append({'item': s.ProtocolName, 'acq': acq, 'mod': modus, 'run': flair1mm_run, 'idx': idx})
				elif s.InversionTime == 2.8 and s.RepetitionTime == 11:
					flairGH_run += 1
					modus = 'GHenlarged'
					info[flair].append({'item': s.ProtocolName, 'acq': acq, 'mod': modus, 'run': flairGH_run, 'idx': idx})
				else:
					print('\n', s, '\n')
					other_run += 1
					info[other].append({'item': s.ProtocolName, 'acq': acq, 'run': other_run, 'idx': idx})
			
			# ASL
			elif ('ASL' in s.ProtocolName):
				asl_run += 1 
				modus = 'asl'
				info[asl].append({'item': s.ProtocolName, 'acq': acq, 'mod': modus, 'run': asl_run, 'idx': idx})
			
			# ASL reference volume
			elif ('M0_22slices' in s.ProtocolName):
				aslref_run += 1 
				modus = 'aslref'
				info[asl_ref].append({'item': s.ProtocolName, 'acq': acq, 'mod': modus, 'run': aslref_run, 'idx': idx})
			
			# fMRI
			elif ('RS-fMRI' in s.ProtocolName):
				if ('PA_' in s.ProtocolName):
					restPA_run += 1 
					modus = 'PA'
					info[rest_PA].append({'item': s.ProtocolName, 'acq': acq, 'dir': modus, 'run': restPA_run, 'idx': idx})
				else:
					rest_run += 1
					modus = 'rfmri'
					info[rest].append({'item': s.ProtocolName, 'acq': acq, 'mod': modus, 'run': rest_run, 'idx': idx})
			
			# DWI
			elif ('Eddy' in s.ProtocolName):
				if ('Pref' in s.ProtocolName):
					dwipref_run += 1
					modus = 'PA'
					info[dwi_ref].append({'item': s.ProtocolName, 'acq': acq, 'mod': modus, 'run': dwipref_run, 'idx': idx})
				elif ('Aref' in s.ProtocolName):
					dwiaref_run += 1
					modus = 'AP'
					info[dwi_ref].append({'item': s.ProtocolName, 'acq': acq, 'mod': modus, 'run': dwiaref_run, 'idx': idx})
				else:
					dwi_run += 1
					modus = 'dwi'
					info[dwi].append({'item': s.ProtocolName, 'acq': acq, 'mod': modus, 'run': dwi_run, 'idx': idx})
			
			elif ('3Dfl' in s.ProtocolName):
				if s.EchoTime > 0.002 and s.EchoTime < 0.003:
					flair3d1_run += 1
					modus = '1'
					info[flairME].append({'item': s.ProtocolName, 'acq': acq, 'mod': modus, 'run': flair3d1_run, 'idx': idx})
				elif s.EchoTime > 0.004 and s.EchoTime < 0.005:
					flair3d2_run += 1
					modus = '2'
					info[flairME].append({'item': s.ProtocolName, 'acq': acq, 'mod': modus, 'run': flair3d2_run, 'idx': idx})
				elif s.EchoTime > 0.007 and s.EchoTime < 0.008:
					flair3d3_run += 1
					modus = '3'
					info[flairME].append({'item': s.ProtocolName, 'acq': acq, 'mod': modus, 'run': flair3d3_run, 'idx': idx})
				elif s.EchoTime > 0.009 and s.EchoTime < 0.010:
					flair3d4_run += 1
					modus = '4'
					info[flairME].append({'item': s.ProtocolName, 'acq': acq, 'mod': modus, 'run': flair3d4_run, 'idx': idx})
				elif s.EchoTime > 0.011 and s.EchoTime < 0.0125:
					flair3d5_run += 1
					modus = '5'
					info[flairME].append({'item': s.ProtocolName, 'acq': acq, 'mod': modus, 'run': flair3d5_run, 'idx': idx})
				elif s.EchoTime > 0.014 and s.EchoTime < 0.015:
					flair3d6_run += 1
					modus = '6'
					info[flairME].append({'item': s.ProtocolName, 'acq': acq, 'mod': modus, 'run': flair3d6_run, 'idx': idx})
				else:
					other_run += 1
					info[other].append({'acq': acq, 'mod': s.ProtocolName, 'item': s.ProtocolName, 'run': other_run, 'idx': idx})

			# Catch other files
			else:
				if s.ProtocolName == 'sPerfusion':
					other_run += 1
					info[other].append({'acq': acq, 'mod': 'perf', 'item': s.ProtocolName, 'run': other_run, 'idx': idx})
				else:
					other_run += 1
					info[other].append({'acq': acq, 'mod': s.ProtocolName, 'item': s.ProtocolName, 'run': other_run, 'idx': idx})

	return info









if __name__ == '__main__':
	import json
	from collections import namedtuple
	from os.path import isfile, join, isdir

	mypath = '../data/check_data/sub-mabs01/sourcedata/ses-01/'

	alljsons = [f for f in os.listdir(mypath) if '.json' in f]
	listdata = []
	listnames = []

	for fn in alljsons:
	
		with open(join(mypath, fn)) as f:
			data = f.read()
	
		x = json.loads(data, object_hook=lambda d: namedtuple('X',d.keys())(*d.values()))
		listnames.append(fn)
		listdata.append(x)

	infotodict(listdata)




