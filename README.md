# ldm-processing-extras
scripts and utilities for adding products to LDM outside of the NRT system
To set up the run directory for CMORPH2 downloading, the script will be 
expecting these subdirectories...
log
download

Also, create a symbolic link named "archive" to the mounted archiving 
directory in /mnt/noaa-case-study-data/cmorph2

The bash script sets up environmental variables, runs a python script for 
downloading file, inserts the file into the LDM queue, moves the 
downloaded file to the archive directory, and performs some clean-up. 
The download script checks to make sure a file has not already been 
downloaded, so the script can be run frequently from cron, at least every 15 min. 
