#!/usr/bin/env python3
"""  main.py
//  Analyse Music
//
//  Created by Timothy Banks on 07/03/2025.
//  
//  This script can be run 
//     by invoking python3 with this file as the mail argument.  It runs in terminal mode.
//
//  Examines the master library directory for files that are missing, extraneous or duplicated
//  and reports these to stdout.
//
//  
"""

# Get the list of albums, then tracks and for each and determine what needs to be done.

import os, sys, logging
from pprint import pformat

import unicodedata
def strip_accents(s):
    return ''.join(c for c in unicodedata.normalize('NFD', s)
                            if unicodedata.category(c) != 'Mn')


file_handler = logging.FileHandler(filename='analysis.log')
stdout_handler = logging.StreamHandler(stream=sys.stdout)
handlers = [file_handler, stdout_handler]
logging.basicConfig(
        format='[%(asctime)s] {%(filename)s:%(lineno)d} %(levelname)s - %(message)s',
        handlers=handlers,
        level=logging.INFO)
logger = logging.getLogger(__name__)


masterDir = '/Volumes/Media/Shared Music/Music Library' # Master - curated source of all music
candidateDir = '/Users/timbanks/Music/Music/Media.localized' # Resident library sometimes used by mistake.
fnameExclusions=[".DS_Store",
                "Folder.jpg",  # Preserves existing artwork not present in Mac OS  Music.app
                "folder.jpg" ]
dnameExclusions=["Automatically Add to Music.localized",
                "Music Library.musiclibrary",
                ".localized"
                ]
#examConstraint = 10000000
transcodeConstraint = 5
copyConstraint = 5
removalConstraint = 5

masterList=[]
masterDates={}
dlen=len(masterDir)

masterList1=[]  # Files suffixed '1' - indicating a duplication.

for (r,ds,ls) in os.walk(masterDir,topdown=True):
  #  if len(ds)==0:
        for l in ls:
            if l not in fnameExclusions and r[dlen+1:].split("/")[0] not in dnameExclusions and not l.startswith("."): # and len(masterList) <= examConstraint:
                masterDates[r[dlen+1:]+"/"+l]=os.path.getmtime(r+"/"+l)
                masterList.append(r[dlen+1:]+"/"+l)
                unsuffixed = (r[dlen+1:]+"/"+l).replace(" 1.m",".m")
                if l.find(" 1.m") > -1:
                    #unsuffixed in masterList:
                    #sys.exit()
                    masterList1.append(r[dlen+1:]+"/"+l)
                    
                
masterList.sort()

candidateList=[]
candidateDates={}
dlen=len(candidateDir)
for (r,ds,ls) in os.walk(candidateDir,topdown=True):
    if ds==[]:
        for l in ls:
            if l not in fnameExclusions and r[dlen+1:].split("/")[0] not in dnameExclusions and not l.startswith("."): # and len(candidateList) <= examConstraint:
                candidateDates[r[dlen+1:]+"/"+l]=os.path.getmtime(r+"/"+l)
                candidateList.append(r[dlen+1:]+"/"+l)# l.replace(".mp3", ""))
                
candidateList.sort()

# Avoid confusion created by accented characters
candidateListStripped=[strip_accents(s) for s in candidateList]
masterListStripped=[strip_accents(s) for s in masterList]

# Report the discoveries
duplicates=[f for f in masterListStripped if f
            in candidateListStripped]
    
uniques=[f for f in masterListStripped if f not in candidateListStripped]

missing=[f for f in candidateListStripped if f not in masterListStripped]
    
#additions = additions+ [f for f in masterList if f.find("Folder.jpg")>-1 and f not in candidateList]
"""removals=[f for f in candidateList if f not in masterList and f.replace(".mp3", ".m4a") not in masterList and f.replace(".mp3", ".M4A") not in masterList ]
updates=[f for f in masterList if (f not in additions and (masterDates[f]>candidateDates[f.replace(".m4a", ".mp3").replace(".M4A", ".mp3")] or masterDates[f]>candidateDates[f.replace(".m4a", ".mp3").replace(".M4A", ".mp3")])) ]
"""

w=220 # Width of output - some filenames are very long.
logger.info(' ')
logger.info("Files in "+masterDir+" and also in "+candidateDir+":")
logger.info(pformat(duplicates[0:3],width=w))
if len(duplicates)>3: print ("of "+str(len(duplicates)))
print('compared to a total of '+str(len(masterList)))

logger.info(' ')
logger.info("Files in "+masterDir+" not also in "+candidateDir+":")
logger.info(pformat(uniques[0:3],width=w))
if len(uniques)>3: print ("of "+str(len(uniques)))

logger.info(' ')
logger.info("Files in "+candidateDir+" missing from "+masterDir+":")
logger.info(pformat(missing[0:300],width=w))
if len(missing)>3 : print ("of "+str(len(missing)))

logger.info(' ')
logger.info("Files in "+masterDir+" with '1' suffix (duplicates?):")
logger.info(pformat(masterList1[0:300],width=w))
if len(masterList1)>3 : print ("of "+str(len(masterList1)))

"""logger.info("Files not in "+masterDir+" but present in "+candidateDir+":")
logger.info(pformat(removals[0:3]))
if len(removals)>3: logger.info("of "+str(len(removals)))
logger.info("?? Updates to "+masterDir+" needing inspection:")
logger.info(pformat(updates[0:3]))
if len(updates)>3: logger.info("of "+str(len(updates)))
"""

exit
"""

if len(removals)>0:
    removed = 0
    for f in removals:
     if removed <= removalConstraint:
      ##  os.remove(candidateDir+"/"+f)
        removed=removed+1
      ##  logger.info("Removed extraneous file: "+f)


# Convert video format

import ffmpeg, shutil
# Input and output file paths
if len(updates+additions)>0:
    transcoded=0
    copied=0
    for f in updates+additions:
        if f.find(".m4a") > -1 and transcoded<=transcodeConstraint:
            input_path = masterDir+"/"+f
            output_path = candidateDir+"/"+f.replace(".m4a", ".mp3").replace(".M4A", ".mp3")
            output_dir = "/".join(output_path.split("/")[0:-1])
          ##  os.makedirs(output_dir, exist_ok=True)
            try:
                ##ffmpeg.input(input_path).output(output_path,loglevel="quiet").run(overwrite_output=True)
                if f in updates: msgInsert = "updated"
                else: msgInsert = "missing"
                logger.info(f"Successfully converted {msgInsert} {input_path} to {output_path}. ({transcoded} of {len(additions)}). ")
                transcoded=transcoded+1
            except ffmpeg.Error as e:
                logger.debug(f"An error occurred attempting to transcode {f}: {e}")
                raise Exception(f"An error occurred: {e} attempting to transcode {f}")
        elif f.lower().find(".mp3") > -1 or f.lower().find(".jpg") > -1 and copied<=copyConstraint:
                input_path = masterDir+"/"+f
                output_path = candidateDir+"/"+f
                output_dir = "/".join(output_path.split("/")[0:-1])
              ##  os.makedirs(output_dir, exist_ok=True)
                rc=0## shutil.copy2(input_path, output_dir)

                if rc==output_path:
                    copied = copied+1
                    logger.info(f"Copied {f} to {output_path}. ({copied} of {len(additions)}). ")
                    
                else:
                    raise Exception(f"Failed copy of {input_path} to {output_path}. cp returned {rc}")
                    
else: logger.info("No transcoding or copying needed. ")
    
"""

# References:
"""
This discussion suggests how to do the comparison to detect absences in the transcoded collection using a shell script.
https://unix.stackexchange.com/questions/4362/recursively-compare-directory-contents-by-name-ignoring-file-extensions
"""

