#!/usr/bin/env python3
"""  main.py
//  Refresh Music Server
//
//  Created by Timothy Banks on 07/03/2025.
//  
//  This script can be run in any of three ways:
//     by invoking python3 with this file as the mail argument.  It runs in terminal mode.
//     by invoking the AsWrapper applescript file which invokeds it without terminal output.
"""

# Get the list of albums, then tracks and for each and determine what needs to be done.
# For m4a, check a corresponding mp3 is present in the transcoded library or make one.
#          If the file is recently updated, refresh the transcoding.
# For mp3, check a copy exists in the transcoded library or copy it.
#          If the file is recently updated, refresh the transcoding.
#

import os, sys, logging
import pdb # debugger
from pprint import pformat


file_handler = logging.FileHandler(filename='transcoding.log')
stdout_handler = logging.StreamHandler(stream=sys.stdout)
handlers = [file_handler, stdout_handler]
logging.basicConfig(
        format='[%(asctime)s] {%(filename)s:%(lineno)d} %(levelname)s - %(message)s',
        handlers=handlers,
        level=logging.INFO)
logger = logging.getLogger(__name__)


sourceDir = '/Volumes/Media/Shared Music/Music Library' # Source of all music
mp3Dir = '/Volumes/Media/Shared Music/MusicMP3/Music'
fnameExclusions=[".DS_Store",
                "Folder.jpg",  # Preserves existing artwork not present in Mac OS  Music.app
                "folder.jpg" ]
dnameExclusions=["Automatically Add to Music.localized",
                "Music Library.musiclibrary"]

# Damage limitation
#examConstraint = 10000000
transcodeConstraint = 500
copyConstraint = 50
removalConstraint = 20

sourceList=[]
sourceDates={}
dlen=len(sourceDir)
for (r,ds,ls) in os.walk(sourceDir,topdown=True):
  #  if len(ds)==0:
        for l in ls:
            if l not in fnameExclusions and r[dlen+1:].split("/")[0] not in dnameExclusions and not l.startswith("."): # and len(sourceList) <= examConstraint:
                sourceDates[r[dlen+1:]+"/"+l]=os.path.getmtime(r+"/"+l)
                sourceList.append(r[dlen+1:]+"/"+l)
                
sourceList.sort()


mp3List=[]
mp3Dates={}
dlen=len(mp3Dir)
for (r,ds,ls) in os.walk(mp3Dir,topdown=True):
    if ds==[]:
        for l in ls:
            if l not in fnameExclusions: # and len(mp3List) <= examConstraint:
                mp3Dates[r[dlen+1:]+"/"+l]=os.path.getmtime(r+"/"+l)
                mp3List.append(r[dlen+1:]+"/"+l)# l.replace(".mp3", ""))
mp3List.sort()

# Report the discoveries
additions=[f for f in sourceList if f.replace(".m4a", ".mp3")
    .replace(".M4A", ".mp3") not in mp3List]
additions = additions+ [f for f in sourceList if f.find("Folder.jpg")>-1 and f not in mp3List]
removals=[f for f in mp3List if f not in sourceList and f.replace(".mp3", ".m4a") not in sourceList and f.replace(".mp3", ".M4A") not in sourceList ]
updates=[f for f in sourceList if (f not in additions and (sourceDates[f]>mp3Dates[f.replace(".m4a", ".mp3").replace(".M4A", ".mp3")] or sourceDates[f]>mp3Dates[f.replace(".m4a", ".mp3").replace(".M4A", ".mp3")])) ]



logger.info("Additions to "+sourceDir+" not in "+mp3Dir+":")
logger.info(pformat(additions[0:3]))
if len(additions)>3: print ("of "+str(len(additions)))
logger.info("Removals from "+sourceDir+" present in "+mp3Dir+":")
logger.info(pformat(removals[0:3]))
if len(removals)>3: logger.info("of "+str(len(removals)))
logger.info("Updates to "+sourceDir+" needing refresh:")
logger.info(pformat(updates[0:3]))
if len(updates)>3: logger.info("of "+str(len(updates)))



if len(removals)>0:
    removed = 0
    for f in removals:
     if removed <= removalConstraint:
        os.remove(mp3Dir+"/"+f)
        removed=removed+1
        logger.info("Removed extraneous file: "+f)


# Convert video format

import ffmpeg, shutil
# Input and output file paths
if len(updates+additions)>0:
    transcoded=0
    copied=0
    for f in updates+additions:
        if f.find(".m4a") > -1 and transcoded<=transcodeConstraint:
            input_path = sourceDir+"/"+f
            output_path = mp3Dir+"/"+f.replace(".m4a", ".mp3").replace(".M4A", ".mp3")
            output_dir = "/".join(output_path.split("/")[0:-1])
            os.makedirs(output_dir, exist_ok=True)
            try:
                ffmpeg.input(input_path).output(output_path,loglevel="quiet").run(overwrite_output=True)
                if f in updates: msgInsert = "updated"
                else: msgInsert = "missing"
                logger.info(f"Successfully converted {msgInsert} {input_path} to {output_path}. ({transcoded} of {len(additions)}). ")
                transcoded=transcoded+1
            except ffmpeg.Error as e:
                logger.debug(f"An error occurred attempting to transcode {f}: {e}")
                raise Exception(f"An error occurred: {e} attempting to transcode {f}")
        elif f.lower().find(".mp3") or f.lower().find(".jpg") > -1 or f.lower().find(".pdf") and copied<=copyConstraint:
                input_path = sourceDir+"/"+f
                output_path = mp3Dir+"/"+f
                output_dir = "/".join(output_path.split("/")[0:-1])
                os.makedirs(output_dir, exist_ok=True)
                rc=shutil.copy2(input_path, output_dir)

                if rc==output_path:
                    copied = copied+1
                    logger.info(f"Copied {f} to {output_path}. ({copied+1} of {len(updates+additions)}). ")
                    
                else:
                    raise Exception(f"Failed copy of {input_path} to {output_path}. cp returned {rc}")
                    
else: logger.info("No transcoding or copying needed. ")
    


# References:
"""
This discussion suggests how to do the comparison to detect absences in the transcoded collection using a shell script.
https://unix.stackexchange.com/questions/4362/recursively-compare-directory-contents-by-name-ignoring-file-extensions
"""

