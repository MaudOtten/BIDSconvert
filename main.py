#!/usr/bin/python


# import
import argparse
import os
import sys
import shutil
import json
import csv
import pandas as pd

from glob import glob
from numpy import unique
from collections import namedtuple
from os.path import join, isdir, isfile
from os import listdir

# import from other scripts
from add_params import add_vals_postrename
from heuristics_LISA import infotodict


# parse command-line arguments
def arg_parser():
	parser = argparse.ArgumentParser(description='Convert all PARREC data in a given subject directory to Nifti in a BIDS structure (run per subject)')
	
	parser.add_argument('-s', '--subject_ID', type=str, required=True,
                    help='Subject ID - required', metavar='sub_ID')
	
	parser.add_argument('-n', '--nr_sessions', type=int,
		                required=True, help='Number of sessions in study (and included in logfile). Unless session ID is given, all sessions are converted.',
		                metavar='nr_of_sessions')
	
	parser.add_argument('-o', '--output_dir', type=str,
		                default='output/', help='Output directory - default: output/', metavar='output_directory')
	
	parser.add_argument('-se', '--session_ID',  nargs='+',
		                default='all', help='Session ID (for session-specific conversion) - string/list, optional (default: all sessions in logfile are converted)',
		                metavar='session_ID')
	
	parser.add_argument('-i', '--input_dir', type=str,
		                default='input/', help='Data input directory - default: input/', metavar='input_directory')
	
	parser.add_argument('-l', '--logfile', type=str,
		                default='include/logfile.csv', help='Full path to logfile with subject and session ID\'s. See documentation for required format.', metavar='log_file')
		                
	parser.add_argument('-so', '--keep_sourcedata', action='store_true',
		                default=False, help='Save source data - yes (True) or no (False), default: False')

	parser.add_argument('-si', '--study_ID', type=str,
		                default='', help='Study ID, added to subject number in BIDS names (fx: study ID = lisa, BIDS name = \'sub-lisa001\') - string, default: none',
		                metavar='study_ID')
	return parser


##############################################################
# Parse JSON and pass data to heuristics in appropriate form #
##############################################################

def parse_json(mypath):
	alljsons = [f for f in os.listdir(mypath) if '.json' in f]
	listdata = []
	listnames = []
	
	for fn in alljsons:
		
		with open(join(mypath, fn)) as f:
			data = f.read()
		
		x = json.loads(data, object_hook=lambda d: namedtuple('X',d.keys())(*d.values()))
		listnames.append(fn)
		listdata.append(x)
	
	return infotodict(listdata), listnames



#####################################
# Call dcm2niix for file conversion #
#####################################

def convert_session(subID, oldses, newses, convert=True):
	try:
		inputdir = args.input_dir.format(session = oldses)
		suboutdir = join(args.output_dir, subID, 'NII_ONLY')
		sesoutdir = join(suboutdir, newses)
		
		if not os.path.isdir(sesoutdir):
			os.makedirs(sesoutdir)
		
		allScanPaths = []
		scansup = glob(join(inputdir, '*.PAR'))
		scanslow = glob(join(inputdir, '*.par'))
		scans = scansup + scanslow
		
		success = []
		failed = []
		
		# check if subdirectory contains PARREC data
		if len(scans) == 0:
			print('No PARREC data found in {}'.format(inputdir))
		
		# if PARREC found, convert data
		else:
			scanpaths = ['/'.join(scans[i].split('/')[:-1]) for i in range(len(scans))]
			scanpaths = unique(scanpaths)
			
			if convert:
				for scanpath in scanpaths:
					conv = os.system('dcm2niix -o {} {}/'.format(sesoutdir, scanpath))
				
					if conv != 0:
						print('NB! Failed conversion: {} \nCheck .tsv in dataset/conversion_log/ for details.'.format(scanpath))
						
						# keep track of failed conversions
						conversion = {'convs': 1, 'newsub': '', 'newses': newses, 'oldsub':args.subject_ID, 'oldses': oldses, 'ofn': scanpath, 'nfp': ''}
						entry = '{convs}\t{newses}\t{oldsub}\t{oldses}\t{ofn}\t{nfp}'.format(**conversion)
						failed.append(entry)
					else:
						file_found = glob(join(scanpath, '*.PAR')) + glob(join(scanpath, '*.par'))
						w = [success.append(f) for f in file_found]
						
		return sesoutdir, success, failed
	
	except Exception as e:
		print(e)
		return 1



###################################
# Get BIDS file name and location #
###################################

def get_fn_sep(alsbs, colnames, conv_sessions, t):
	if not isdir(join(args.output_dir, args.subject_ID)):
		print('NB! Subject is not converted / not in .BIDS directory')
		return 1
	
	# assign index of subject ID to i
	ind = alsbs.loc[alsbs['subID']==args.subject_ID]
	
	try:
		i = ind.index[0]
	except Exception as e:
		print(e)
		print('NB! Sub ID is likely not found in logfile (BIDS_convert.py, line 135)')
		return 1
	
	# get BIDS subject name, get conversion log file name
	subname = '{}{:0{}}'.format(args.study_ID, i+1, t)
	logfilename = '{}_renamelog.tsv'.format(subname)
	logfilepath = join(args.output_dir, 'conversion_log')
	
	# if source data should be kept, copy files for renaming
	if args.keep_sourcedata is False:
		mode = 'mv'
	else:
		mode = 'cp'

	for j in range(args.nr_sessions):
		ses = colnames[j+1]
		
		if args.nr_sessions > 1:
			sesname = 'ses-0{}'.format(j+1)
		else:
			sesname = ''
		
		sespath = join(args.output_dir, args.subject_ID, 'NII_ONLY', sesname)
		newpath = join(args.output_dir, 'sub-'+subname, sesname)
		
		if sesname not in conv_sessions:
			continue
		elif not isdir(sespath):
			print('NB! Session is not converted / does not exist')
			continue
		
		if not isdir(newpath):
			os.makedirs(newpath)
			print('Made new dir: {}'.format(newpath))
		
		sesID = alsbs.loc[i, ses]
		
		ses_info, oldnames = parse_json(sespath)
		allkeys = [s for s in ses_info]
		
		for key in ses_info:
			for entry in ses_info[key]:
				entry['subject'] = subname
				entry['session'] = sesname
				
				oldfilename = oldnames[entry['idx']][:-5]
				newfilename_FULL = key[0].format(s=entry)
				
				sp, sep, st, fn = newfilename_FULL.split('/')
				
				fn = fn.replace('__', '_')
				
				newfilepath = join(newpath, st)
				
				# MAKE DIR IF DOESNT EXIST
				if not isdir(newfilepath):
					os.makedirs(newfilepath)
				
				oldfile = join(sespath, oldfilename)
				newfile = join(newfilepath, fn)
				
				
				if args.subject_ID not in oldfilename:
					print('NB! Subject ID is not congruent with Patient ID in data! Check logfile for inconsistencies.')
					#return 1
					#####################################################################################################
					# No separate solution is implemented yet. If old subject ID does not matter for BIDS conversion 	#
					# (and original data is properly checked for correct transfer etc.), this if-statement can be 		#
					# commented out and conversion can be run regardless. Make sure to check proper naming afterwards.	#
					#####################################################################################################
				
				if isfile(newfile):
					print('NB! File with identical name found: {}\nCheck logfile for conversion naming detail'.format(fn))
				
				# keep track of cp / mv status
				returned = 0
				
				if entry['item'] == 'noJSON':
					# copy / move image without JSON
					returned = os.system('{} -n {}.nii.gz {}.nii.gz'.format(mode, oldfile, newfile))
				else:
					# copy / move file to BIDS name and dir
					returned = os.system('{} -n {}.nii.gz {}.nii.gz & {} -n {}.json {}.json'.format(mode, oldfile, newfile, mode, oldfile, newfile))
				
					# DWI
					if '_dwi' in fn:
						returned += os.system('{} -n {}.bval {}.bval & {} -n {}.bvec {}.bvec'.format(mode, oldfile, newfile, mode, oldfile, newfile))
				
				if returned != 0:
					returned = 2
				
				# keep track of old and new names of converted files
				conversion = {'convs': returned, 'newsub':subname, 'newses':sesname, 'oldsub':args.subject_ID, 'oldses': sesID, 'ofn': oldfilename, 'nfp': newfilepath + fn}
				entry = '{convs}\t{newses}\t{oldsub}\t{oldses}\t{ofn}\t{nfp}'.format(**conversion)
				
				# add to 'noconversion.tsv' if renaming NOT successful
				if returned != 0:
					os.system('echo "{}" >> {}'.format(entry, join(logfilepath, 'noconversion.tsv')))
				
				# always add to subject logfile
				os.system('echo "{}" >> {}'.format(entry, join(logfilepath, logfilename)))
	
	print('\n-- Renaming successful. --\n')
	return 0




def main():
	# get command-line arguments as args
	try:
		global args
		args = arg_parser().parse_args()
	except:
		print('NB! Arguments are not passed correctly')
		return 1
	
	colnames = ['subID']
	cols = [0]
	
	# get session names based on given nr of session in study
	for i in range(args.nr_sessions):
		colnames.append('ses-{:02}'.format(i+1))
		cols.append(i+1)
	
	try:
		allsubs = pd.read_csv(args.logfile, sep='\t', names=colnames, usecols=cols)
		allsubs.subID = allsubs.subID.astype(str)
	except:
		print('NB! Cannot load log file. Make sure the .csv logfile is in the same directory as this script.')
		return 1
	
	ind = allsubs.loc[allsubs['subID']==args.subject_ID]
	i = ind.index[0]
	total = allsubs.shape[0]
	
	# If smarter way to check amount of subjects for numbering, insert here
	if 1 <= total < 10:
		t = 1
	elif 10 <= total < 100:
		t = 2
	elif 100 <= total < 1000:
		t = 3
	elif 1000 <= total:
		t = 4
	
	newsubname = 'sub-{}{:0{}}'.format(args.study_ID, i+1, t)
	
	# check output directories
	if isdir(args.output_dir):
		if not args.output_dir.endswith('/'):
			args.output_dir += '/'
	else:
		print('NB! Output directory does not exist.')
		return 1
	
	# set log dir and file
	logfilename = '{}_convertlog.tsv'.format(newsubname[4:])
	logfilename_r = '{}_renamelog.tsv'.format(newsubname[4:])
	logfilepath = join(args.output_dir, 'conversion_log')
	
	try:
		os.mkdir(logfilepath)
	except:
		pass
	
	# write logfile for conversion
	if not isfile(join(logfilepath, logfilename_r)):
		os.system('touch {lfn} && chmod 755 {lfn} && echo "renaming_success\tnewses\toldsub\toldses\toldfilename\tnewfilepath" > {lfn}'.format(lfn = join(logfilepath, logfilename_r)))
		
	# write logfile for renaming
	if not isfile(join(logfilepath, logfilename)):
		os.system('touch {lfn} && chmod 755 {lfn} && echo "conversion_success\toldfilename\toldfilepath" > {lfn}'.format(lfn = join(logfilepath, logfilename)))
	
	if not isfile(join(logfilepath, 'noconversion.tsv')):
		try:
			os.system('touch {ncf} && chmod 755 {ncf} && echo "conversion_success\tnewses\toldsub\toldses\toldfilename\tnewfilepath" > {ncf}'.format(ncf = join(logfilepath, 'noconversion.tsv')))
		except:
			pass
	
	
	if isdir(join(args.output_dir, newsubname)):
		print('NB! Converted data of this subject already (partly) exists. Be careful to not overwrite existing files.')
		
		# When used directly from command line, this block of code can be uncommented to ask for input when converting existing sub folder
		# Does not work when submitting batch to cluster
		
		#while True:
		#	answer = input("Do you wish to continue anyway? y / n (possibly overwriting existing files): ")
			
		#	if answer.lower() == 'y':
		#		break
		#	elif answer.lower() == 'n':
		#		return 1
	
	
	if isdir(join(args.output_dir, args.subject_ID)):
		print('NB! This subject / session already partly exists, or is currently being converted. Use a different output directory or check existing data.')
		return 1
	
	converted_sessions = 0
	converted_sessions_names = []
	
	# convert specified nr of sessions (default = all)
	for j in range(args.nr_sessions):
		
		if args.nr_sessions == 1:
			newses = ''
		else:
			newses = colnames[j+1]
		
		oldses = allsubs.loc[i, colnames[j+1]]
		
		# Only convert if session exists
		if type(oldses) == str:
			# make code run session-specific
			if args.session_ID != 'all':
				if oldses not in args.session_ID:
					continue
			
			if isdir(join(args.output_dir, newsubname, newses)):
				print('NB! This session has already been converted.')
				continue
			
			# convert files in ses directory (dcm2niix)
			scandir, success_convs, failed_convs = convert_session(args.subject_ID, oldses, newses, True)
			
			for success_conv in success_convs:
				suc = '0\t{}\t{}'.format(success_conv.split('/')[-1], '/'.join(success_conv.split('/')[:-1]))
				os.system('echo "{suc}" >> {p}'.format(suc = suc, p = join(logfilepath, logfilename)))
			
			# log failed conversions to subject file and noconversion.tsv
			for failed_conv in failed_convs:
				os.system('echo "{failed}" >> {p1} && echo "{failed}" >> {p2}'.format(failed = failed_conv, p1 = join(logfilepath, logfilename), p2 = join(logfilepath, 'noconversion.tsv')))
			
			# check for empty session
			spath = join(args.output_dir, args.subject_ID, 'NII_ONLY', newses)
			
			# if no path to session
			if not isdir(spath):
				pass
			
			# if no files in session dir, remove dir
			elif not listdir(spath):
				os.system('rm -r {}'.format(spath))
				print('NB! Session resulted in zero output files. Check source data for potential missing conversions.')
			
			# otherwise, count session as converted
			else:
				converted_sessions += 1
				converted_sessions_names.append(newses)
		
		else:
			print('Session doesn\'t exist.')
	
	# Sanity check
	if converted_sessions == 0:
		print('NB! Zero sessions were converted. Conversion is stopped (no renaming done).')
		return 1
	
	# rename converted data
	renameRT = get_fn_sep(allsubs, colnames, converted_sessions_names, t)
	
	if renameRT != 0:
		print('NB! Renaming function returned non-zero. Check output for errors / warnings.')
		return 1
	
	# if copy converted data with original naming to source data folder
	if args.keep_sourcedata:
		for ss in converted_sessions_names:
			os.makedirs(join(args.output_dir, newsubname, 'sourcedata', ss))
			os.system('mv {old}/* {new}/'.format(new = join(args.output_dir, newsubname, 'sourcedata', ss), old = join(args.output_dir, args.subject_ID, 'NII_ONLY', ss)))
	
	# delete converted original data
	os.system('rm -r {path}'.format(path = join(args.output_dir, args.subject_ID)))
	
	# add parameters to JSON files post-rename (including IntendedFor field)
	add_vals_postrename(join(args.output_dir, newsubname))
	
	# copy over dataset description files
	os.system('cp specs/* {}'.format(args.output_dir))
	os.system('cp specs/.bidsignore {}'.format(args.output_dir))
	
	# finish strong
	print('\n\n-- Conversion successful. --')
	return 0




if __name__ == '__main__':
	main()


