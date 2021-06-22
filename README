README - BIDS_conversion

Code largely written by Maud Ottenheijm (DRCMR)



This folder contains code for conversion of PARREC data to BIDS format (in nifti file format).
This file gives a brief overview of the code makeup and how to use it.


Folder content:

- main.py			: contains main function, convert and rename functions, runs conversion of single subject to nifti, renames based on heuristics.py and writes logfiles
- add_params.py		: called by main.py to add missing values to json sidecars
- heuristics.py		: heuristics for renaming files to BIDS standard
- logno.csv			: file with all subject and session ID's

- specs/			: folder with all BIDS-required files being directly copied into the root folder of the resulting dataset
	- .bidsignore
	- CHANGES
	- README (for dataset)
	- dataset_description.json
	- participants.json
	- participants.tsv

- add_params_afterconversion.py	: code to use for adding values to JSON sidecars after full conversion of a dataset. Called for single subject, adjust to include the desired values and filter criteria of file names
	


How to run conversion:


Step 1: A .csv file with all log nrs should be in the same directory as main.py. This file should contain a first column with subject ID's, and subsequent columns with session ID's (in case of single-session data this is simply the subject ID again).


Step 2: heuristics.py should be adjusted to include all new naming conventions and their filter criteria (use parameter information, not just name!).


Step 3: run main.py as such

python main.py [-h] -s sub_ID -n nr_of_sessions [-o output_directory]
				[-se session_ID [session_ID ...]] [-i input_directory]
				[-l log_file] [-so] [-si study_ID]

s	[REQ]	- subject ID
n	[REQ]	- nr of sessions to convert (if not all sessions should be converted, define -se)
i	[OPT]	- input directory (root folder of converted dataset), default: input/
si	[OPT]	- study ID, this will be appended to the subject number (fx. study ID = lisa, subject name = sub-lisa001)
se	[OPT]	- session ID, can be a string or a list of strings (including one or more session ID's to be converted)
l	[OPT]	- lognr csv (define as described in step 1), default: logfile.csv


Example 1 (from LISA study):
python main.py -s FN011 -n 4 -o /mnt/projects/LISA/BIDS_LISA/ -i /mnt/xnat/LISA/arc001/{session}/SCANS/*/RAW/ -si lisa -l LISA_logno_2FU.csv

This command converts all 4 sessions of one subject to the given output directory with study ID 'lisa'.

Example 2:
python main.py -s FN011 -n 2 -se [] -o /mnt/projects/LISA/BIDS_LISA/ -i /mnt/xnat/LISA/arc001/{session}/SCANS/*/RAW/ -si lisa



Error logs:

For each subject, a conversion log file is kept to track which of the original data was successfully converted ([SUBNAME]_convertlog.tsv). Here the first column indicates successful conversion (0) or erroneous (1) results. Name of original file is included as well as the path.
Also, a renaming file is kept to track which files are renamed to what and its success ([SUBNAME]_renamelog.tsv). Here the first column also indicates successful conversion (0) or erroneous (2) results. Old and new subject and session ID's are stored, as well as new file path and name.

One separate logfile shows all erroneous results for all subjects, as a startoff point for possible debugging / troubleshooting (noconversion.tsv).

