#!/usr/bin/env python3
"""Get and set attributes on a satellite netcdf file."""

import argparse
import os
import urllib.request, urllib.parse, urllib.error, urllib.request, urllib.error, urllib.parse
import datetime
from html.parser import HTMLParser
from time import strftime
from time import sleep
from datetime import datetime, timedelta

##############################################################
class MyHTMLParser(HTMLParser):
   def __init__(self):
      HTMLParser.__init__(self)
      self.satfile = []
      self.record = False
      self.fcnt = 0
   def handle_starttag(self, tag, attrs):
      """ look for start tag and turn on recording """
      if tag == 'a':
         #print "Encountered a url tag:", tag
         self.record = True
      #print "Encountered a start tag:", tag
   def handle_endtag(self, tag):
      """ look for end tag and turn on recording """
      if tag == 'a':
         #print "Encountered end of url tag :", tag
         self.record = False
   def handle_data(self, data):
      """ handle data string between tags """
      if verbose:
         print("Found data line: ", data)
      lines = data.splitlines()
      for dline in lines:
         #print "LINE: ",dline
         # make sure line is not blank
         if "CMORPH2" in dline[:8]:
            self.satfile.append(dline)

##################

def _process_command_line():
    """Process the command line arguments.

    Return an argparse.parse_args namespace object.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-bh', '--backhrs', type=int, action='store', default=8,
        help='num hrs back to search'
    )
    parser.add_argument(
        '-v', '--verbose', action='store_true', help='verbose flag'
    )

    args = parser.parse_args()
    return args

##############################################################3
def get_filepaths(directory):
    """ generate the filenames in a directory tree by walking down
    the tree. """

    file_paths = []
    for root, directories, files in os.walk(directory):
        for filename in files:
           # Join the two strings to form the full path
           filepath = os.path.join(root,filename)
           file_paths.append(filepath)

    return file_paths
##############################################################3
def find_files(directory,matchfile):
    """ generate the filenames in a directory tree by walking down
    the tree. """
    #print "directory={}".format(directory)
    #print "matchfile={}".format(matchfile)
    file_paths = []
    for root, directories, files in os.walk(directory):
        for filename in files:
           if filename == matchfile:
              return (1)

    return 0
##############################################################3
def filesecs(filename):
    """ decode filename for time """
    fparts=filename.split('_')
    fyr = int(fparts[2][:4])
    fmo = int(fparts[2][4:6])
    fda = int(fparts[2][6:8])
    fhr = int(fparts[2][8:10])
    fmn = int(fparts[2][10:12])
    #print ("{} {} {} {} {}".format(fyr,fmo,fda,fhr,fmn))
    filetime = datetime(fyr,fmo,fda,fhr,fmn)

    return filetime
#####################################################################

def main():
   """Call to run fetching script."""
   global verbose
   args = _process_command_line()
   verbose = args.verbose

   now = datetime.utcnow()
   nowdatestr = now.strftime("%Y%m%d%H%M")

   starttime = now - (timedelta(hours=args.backhrs))
   startyr = int(starttime.strftime("%Y"))
   startmo = int(starttime.strftime("%m"))
   startda = int(starttime.strftime("%d"))
   starthr = int(starttime.strftime("%H"))
   startmin = int(starttime.strftime("%M"))
   starttime = datetime(startyr,startmo,startda,starthr,startmin)

   endtime = now
   endyr = int(endtime.strftime("%Y"))
   endmo = int(endtime.strftime("%m"))
   endda = int(endtime.strftime("%d"))
   endhr = int(endtime.strftime("%H"))
   endmin = int((int(endtime.strftime("%M")) / 30) * 30)
   endtime = datetime(endyr,endmo,endda,endhr,endmin)

   #This is the base url for access to CMORPH2.
   baseurl = "https://ftp.cpc.ncep.noaa.gov/precip/PORT/NESDIS/CMORPH2_RT/.GINA/"
   print("URL=",baseurl)
   sock = urllib.request.urlopen (baseurl)
   htmlSource = str(sock.read(),'UTF-8')
   sock.close()
   if args.verbose:
      print("BEGIN HTML ==================================================")
      print(htmlSource)
      print("END HTML ====================================================")
      rtnval = len(htmlSource)
      print("HTML String length = {}".format(rtnval))

   # instantiate the parser and feed it the HTML page
   parser = MyHTMLParser()
   parser.feed(htmlSource)

   archivebase = "/mnt/noaa-case-study-data/cmorph2"
   download = 0
   for filename in parser.satfile:
      if args.verbose:
         print (filename)
      fsecs = filesecs(filename) 
      if fsecs < starttime:
         if args.verbose:
            print("File too old. Skipping...".format(filename))
      elif find_files(archivebase, filename):
         if args.verbose:
            print("File already downloaded: {} Skipping...".format(filename))
      else: 
         try:
            fullurl = "{}{}".format(baseurl, filename)
            print("Requesting: {}".format(fullurl))
            print("fullurl={}".format(fullurl))
            response = urllib.request.urlopen(fullurl)
         except urllib.error.HTTPError as e:
            print('The server couldn\'t fulfill the request.')
            print('Error code: ', e.code)
         except urllib.error.URLError as e:
            print('Failed to reach a server.')
            print('Reason: ', e.reason)
         else:
            #open the file for writing
            print(("Connected!  Writing to: {}", filename))
            fh = open(filename, "wb")
            # read from request while writing to file
            fh.write(response.read())
            fh.close()
            download += 1
   print("{}{}Z Files downloaded: {}".format(endhr, endmin, download))
   return

if __name__ == '__main__':
    main()
