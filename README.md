------------------------

README - BIDS_conversion

Code by Maud Ottenheijm (DRCMR) - 2020 / 2021

Heuristics setup is based on conversion package heudiconv: https://github.com/nipy/heudiconv

------------------------

This folder contains code for conversion of PARREC data to BIDS format (in nifti file format).
This file gives a brief overview of the code makeup and how to use it.


###Folder content:

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



###How to run conversion:


######Step 1: 
A .csv file with all log nrs should be in the same directory as main.py. This file should contain a column with 'old' subject ID's called **BIDSconvID**, a column with the BIDS subject id (fx. sub-lisa001) called **bidsID**, and subsequent columns with session ID's (in case of single-session data this is the ID of the raw data) called **ses-01**, **ses-02** etc. Other columns can be added, with appropriate column names. BIDSconverter expects a header row at the top of the file.


######Step 2: 
Heuristics.py should be adjusted to include all new naming conventions and their filter criteria (use parameter information, not just name!).


######Step 3: 
Run main.py as such

python main.py [-h] -s sub_ID [-o output_directory]

				[-se session_ID [session_ID ...]] [-i input_directory]

				[-l log_file] [--keep_sourcedata]

- -s	[REQ]	subject ID
- -o	[OPT]	output directory for converted (BIDS) dataset, default: output/
- -i	[OPT]	input directory (root folder of raw dataset), default: input/
- -se	[OPT]	session ID, can be a string or a list of strings (including one or more session ID's to be converted)
- -l	[OPT]	lognr csv (define as described in step 1), default: logfile.csv
- --keep_sourcedata     Save source data - yes (True) or no (False), default: False


######Example 1 (from LISA study):
python main.py -s FN011 -o /mnt/projects/LISA/BIDS_LISA/ -i /mnt/xnat/LISA/arc001/{session}/SCANS/*/RAW/ -l LISA_logno_2FU.csv

This command converts all 4 sessions of one subject to the given output directory.

######Example 2:
python main.py -s FN011 -se ['someID', 'anotherID'] -o /mnt/projects/LISA/BIDS_LISA/ -i /mnt/xnat/LISA/arc001/{session}/SCANS/*/RAW --keep_sourcedata

This command converts two specified sessions (by their original ID) of one subject to the output directory, while saving the intermittent converted files in [OUTPUTFOLDER]/[OLD_SUBNAME]]/, where OLD_SUBNAME here is FN011.



###Error logs:

For each subject, a conversion log file is kept to track which of the original data was successfully converted ([SUBNAME]_convertlog.tsv). Here the first column indicates successful conversion (0) or erroneous (1) results. Name of original file is included as well as the path.
Also, a renaming file is kept to track which files are renamed to what and its success ([SUBNAME]_renamelog.tsv). Here the first column also indicates successful conversion (0) or erroneous (2) results. Old and new subject and session ID's are stored, as well as new file path and name.

One separate logfile shows all erroneous results for all subjects, as a startoff point for possible debugging / troubleshooting (noconversion.tsv).

