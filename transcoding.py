#!/usr/bin/env python3
"""  main.py
//  Refresh Music Server
//
//  Created by Timothy Banks on 07/03/2025.
//  
//  This script can be run in any of three ways:
//     by invoking python3 with this file as the main argument.  It runs in terminal mode.
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
fnameExclusions=[".DS_Store"]
dnameExclusions=["Automatically Add to Music.localized",
                "Music Library.musiclibrary"]
fkinds =[".m4a",".mp3",".M4A",".MP3",".jpg",".m3u",".m3u8",".pdf"]

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
                if r!=sourceDir: lf = "/"+l
                else: lf ="/./"+l # File need a directory separator to make subsequent processing more straightforward
                sourceDates[r[dlen+1:]+lf]=os.path.getmtime(r+lf)
                if os.path.splitext(lf)[1] in fkinds: sourceList.append(r[dlen+1:]+lf)
                
sourceList.sort()


mp3List=[]
mp3Dates={}
emptydirs=[]
dlen=len(mp3Dir)
for (r,ds,ls) in os.walk(mp3Dir,topdown=True):
        if ls==[]: emptydirs.append(r)
        for l in ls:
            if l not in fnameExclusions: # and len(mp3List) <= examConstraint:
                if r!=mp3Dir: lf = "/"+l
                else: lf ="/./"+l
                mp3Dates[r[dlen+1:]+lf]=os.path.getmtime(r+lf)
                mp3List.append(r[dlen+1:]+lf)
mp3List.sort()


# Report the discoveries


additions=[f for f in sourceList if f.replace(".m4a", ".mp3").replace(".M4A", ".mp3") not in mp3List]
removals=[f for f in mp3List if f not in sourceList and f.replace(".mp3", ".m4a") not in sourceList and f.replace(".mp3", ".M4A") not in sourceList ]
updates=[f for f in sourceList if (f not in additions and (sourceDates[f]>mp3Dates[f.replace(".m4a", ".mp3").replace(".M4A", ".mp3")] or sourceDates[f]>mp3Dates[f.replace(".m4a", ".mp3").replace(".M4A", ".mp3")])) ]

logger.info(pformat(additions[0:3]))
if len(additions)>3: print ("of "+str(len(additions)))
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
        opath=mp3Dir+"/"+f
        logger.info(f"Removed extraneous file {opath} ({removed} of {len(removals)}). ")



emptydirs=[]
#dlen=len(mp3Dir)
for (r,ds,ls) in os.walk(mp3Dir,topdown=True):
        if ls==[] and ds==[]: emptydirs.append(r)

logger.info("Empty Directories: ")
logger.info(pformat(emptydirs[0:30]))
if len(emptydirs)>3: logger.info("of "+str(len(emptydirs)))

# Convert video format

import ffmpeg, shutil
# Input and output file paths
if len(updates+additions)>0:
    transcoded=0
    copied=0
    skipped=0
    for f in updates+additions:
        if (f.find(".m4a") > -1 or f.find(".M4A") > -1) and transcoded<=transcodeConstraint:
            input_path = sourceDir+"/"+f
            output_path = mp3Dir+"/"+f.replace(".m4a", ".mp3").replace(".M4A", ".mp3")
            output_dir = "/".join(output_path.split("/")[0:-1])
            os.makedirs(output_dir, exist_ok=True)
            try:
                ffmpeg.input(input_path).output(output_path,loglevel="quiet").run(overwrite_output=True)
                if f in updates: msgInsert = "updated"
                else: msgInsert = "missing"
                transcoded=transcoded+1
                logger.info(f"Successfully converted {msgInsert} {input_path} to {output_path}. ({transcoded+copied} of {len(updates+additions)}). ")
            except ffmpeg.Error as e:
                logger.debug(f"An error occurred attempting to transcode {f}: {e}")
                raise Exception(f"An error occurred: {e} attempting to transcode {f}")
        elif f.lower().find(".mp3") >-1 or f.lower().find(".jpg") > -1 or f.lower().find(".pdf") >-1 and copied<=copyConstraint:
                input_path = sourceDir+"/"+f
                output_path = mp3Dir+"/"+f
                output_dir = "/".join(output_path.split("/")[0:-1])
                os.makedirs(output_dir, exist_ok=True)
                rc=shutil.copy2(input_path, output_dir)
                if f in updates: msgInsert = "updated"
                else: msgInsert = "missing"
                if rc==output_path:
                    copied = copied+1
                    logger.info(f"Copied {msgInsert} {f} to {output_path}. ({transcoded+copied+skipped} of {len(updates+additions)}). ")
                    
                else:
                    raise Exception(f"Failed copy of {input_path} to {output_path}. cp returned {rc}")
        elif f.lower().find(".m3u") >-1 and copied<=copyConstraint:
                input_path = sourceDir+"/"+f
                output_path = mp3Dir+"/"+f
                output_dir = "/".join(output_path.split("/")[0:-1])
                os.makedirs(output_dir, exist_ok=True)
                rc=shutil.copy2(input_path, output_dir)
                # Edit the file here to replace m4a with mp3 and convert absolute paths to relative.
                # Read in the file
                with open(output_path, 'r') as file:
                    filedata = file.read()

                # Replace the target strings
                filedata = filedata.replace(sourceDir, '.').replace('.m4a','.mp3')
                # Write the file out again
                with open(output_path, 'w') as file:
                    file.write(filedata)
		
                if f in updates: msgInsert = "updated"
                else: msgInsert = "missing"
                if rc==output_path:
                    copied = copied+1
                    logger.info(f"Copied/translated {msgInsert} {f} to {output_path}. ({transcoded+copied+skipped} of {len(updates+additions)}). ")
                    
                else:
                    raise Exception(f"Failed copy of {input_path} to {output_path}. cp returned {rc}")
        
        else:
            skipped=skipped+1
            logger.info(f"Skipped {f}. Wrong file type. ({transcoded+copied+skipped} of {len(updates+additions)}). ")
            
        
                    
else: logger.info("No transcoding or copying needed. ")
    
if len(emptydirs)>0:
    emptied=0
    for f in emptydirs:
        #os.path.rmdir()
        logger.info(f"Non-Deleted empty directory {f}")
"""
# Should repeat the exercise until there are none left.
# ... and note that some directories which started out empty may be filled during transcoding.
emptydirs=[]
#dlen=len(mp3Dir)
for (r,ds,ls) in os.walk(mp3Dir,topdown=True):
        if ls==[] and ds==[]: emptydirs.append(r)
        
see also: 

This next example is a simple implementation of shutil.rmtree(). Walking the tree bottom-up is essential as rmdir() doesn’t allow deleting a directory before it is empty:

# Delete everything reachable from the directory "top".
# CAUTION:  This is dangerous! For example, if top == Path('/'),
# it could delete all of your files.
for root, dirs, files in top.walk(top_down=False):
    for name in files:
        (root / name).unlink()
    for name in dirs:
        (root / name).rmdir()        
        
        
"""

# References:
"""
This discussion suggests how to do the comparison to detect absences in the transcoded collection using a shell script.
https://unix.stackexchange.com/questions/4362/recursively-compare-directory-contents-by-name-ignoring-file-extensions
"""

