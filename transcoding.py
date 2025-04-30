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
from subprocess import Popen, PIPE
import metadataCleaning
from metadataCleaning import strip_accents



def transLogger(level):
    file_handler = logging.FileHandler(filename='transcoding.log')
    stdout_handler = logging.StreamHandler(stream=sys.stdout)
    handlers = [file_handler, stdout_handler]
    logging.basicConfig(
            format='[%(asctime)s] {%(filename)s:%(lineno)d} %(levelname)s - %(message)s',
            handlers=handlers,
            level=level or logging.DEBUG)
    logger = logging.getLogger(__name__)
    return logger
"""
    Export the playlists from Music 
"""
def exportPlaylists(logger):
    scriptPath = "/Users/timbanks/MyWork/Refresh Music Server/ExportPlaylists.scpt"
    args = []#["args are not used", 3]
    p = Popen(
            ['/usr/bin/osascript', scriptPath] + [str(arg) for arg in args],
            stdout=PIPE, stderr=PIPE)

    out, err = p.communicate()

    if p.returncode:
        logger.info(f'ERROR: {err}')
        # print(f'ERROR: {err}')
        exit(err)
    else: logger.info(f'Export of playlists from Music was successful.')
    
#proto main
logger=transLogger(level=logging.INFO)
exportPlaylists(logger)



fnameExclusions=[".DS_Store"]
dnameExclusions=["Automatically Add to Music.localized",
                "Music Library.musiclibrary"]
fkinds =[".m4a",".mp3",".M4A",".MP3",".jpg",".m3u",".m3u8",".pdf"]

# Damage limitation
#examConstraint = 10000000
transcodeConstraint = 500
copyConstraint = 50
removalConstraint = 20

sourceDir = '/Volumes/Media/Shared Music/Music Library' # Source of all music
sourceList=[]
sourceDates={}
dlen=len(sourceDir)
#for (r,ds,ls) in os.walk(sourceDir,topdown=True)
for (r,ds,ls) in ((x,y,z) for (x,y,z) in os.walk(sourceDir,topdown=True) if "Rake's" in x):
  #  if len(ds)==0:
        for l in ls:
            if l not in fnameExclusions and r[dlen+1:].split("/")[0] not in dnameExclusions and not l.startswith("."): # and len(sourceList) <= examConstraint:
                if r!=sourceDir: lf = "/"+l
                else: lf ="/./"+l # File need a (redundant) directory separator to make subsequent processing more straightforward
                sourceDates[r[dlen+1:]+lf]=os.path.getmtime(r+lf)
                if os.path.splitext(lf)[1] in fkinds: sourceList.append(r[dlen+1:]+lf)
                
sourceList.sort()


mp3Dir = '/Volumes/Media/Shared Music/MusicMP3/Music'
mp3List=[]
mp3Dates={}
emptydirs=[]
dlen=len(mp3Dir)
#for (r,ds,ls) in os.walk(mp3Dir,topdown=True):
for (r,ds,ls) in ((x,y,z) for (x,y,z) in os.walk(mp3Dir,topdown=True) if "Rake's" in x):
        if ls==[]: emptydirs.append(r)
        for l in ls:
            if l not in fnameExclusions: # and len(mp3List) <= examConstraint:
                if r!=mp3Dir: lf = "/"+l
                else: lf ="/./"+l
                mp3Dates[r[dlen+1:]+lf]=os.path.getmtime(r+lf)
                mp3List.append(r[dlen+1:]+lf)
mp3List.sort()

# Report the discoveries

strippedSourceList=[strip_accents(f) for f in sourceList]
strippedSourceDates={strip_accents(f):sourceDates[f] for f in list(sourceDates.keys())}

additions=[f for f in sourceList if strip_accents(f).replace(".m4a", ".mp3").replace(".M4A", ".mp3") not in mp3List]
removals=[f for f in mp3List if f not in strippedSourceList and f.replace(".mp3", ".m4a") not in strippedSourceList and f.replace(".mp3", ".M4A") not in strippedSourceList ]
updates=[f for f in sourceList if (f not in additions and (sourceDates[f]>mp3Dates[strip_accents(f).replace(".m4a", ".mp3").replace(".M4A", ".mp3")] or sourceDates[f]>mp3Dates[strip_accents(f).replace(".m4a", ".mp3").replace(".M4A", ".mp3")])) ]

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
        trueLs=[l for l in ls if l not in fnameExclusions]
        trueDs=[d for d in ds if d not in dnameExclusions]
        if trueLs==[] and ds==[]: emptydirs.append(r)

logger.info("Empty Directories: ")
logger.info(pformat(emptydirs[0:30]))
if len(emptydirs)>3: logger.info("of "+str(len(emptydirs)))

# Convert video format and clean the metadata to make it palatable to Pure consumers
cleaner=metadataCleaning.MDcleaner(logger)
import ffmpeg, shutil
# Input and output file paths
if len(updates+additions)>0:
    transcoded=0
    copied=0
    skipped=0
    for f in updates+additions:
        if transcoded<=transcodeConstraint and \
        (f.lower().find(".m4a") > -1 or \
        f.lower().find(".mp3")) >-1: # It seems that downloaded mp3's sometimes can't be played by Pure, (namely LAME v3.97 encoding)
                                     # used in Stravinsky's Rake's progress. They need to be re-encoded
                                     # The original settings were
                                     # 'bitrate': 320015, 'bitrate_mode': <BitrateMode.CBR: 1>, 'channels': 2, 'encoder_info': 'LAME 3.97.0', 'encoder_settings': '-b 320', 'mode': 1, TSSE=LAME v3.97
                                     # The new ones are: 'bitrate': 128000, 'bitrate_mode': <BitrateMode.CBR: 1>, 'channels': 2,
                                     # 'encoder_settings': '', 'mode': 0, TSSE=Lavf61.7.100,
                                     # The "joint_stereo" (mode)  argument needs experimentation - it seems to be ignored.
            input_path = sourceDir+"/"+f
            output_path = strip_accents(mp3Dir+"/"+f.replace(".m4a", ".mp3").replace(".M4A", ".mp3"))
            output_dir = "/".join(output_path.split("/")[0:-1])
            os.makedirs(output_dir, exist_ok=True)
            try:
                #breakpoint() # transcoding imminent
                ffmpeg.input(input_path).output(output_path,loglevel="quiet", acodec='mp3', joint_stereo=1, audio_bitrate=128000) \
                    .run(overwrite_output=True) # ouput(,acodec="copy"  causes error
                                                # need to find a way to specify -codec:a libmp3lame  -q:a 3
                                                # and  -joint_stereo 1
                if f in updates: msgInsert = "updated"
                else: msgInsert = "missing"
                transcoded=transcoded+1
                logger.info(f"Successfully converted {msgInsert} {input_path} to {output_path}. ({transcoded+copied} of {len(updates+additions)}). ")
                
            except ffmpeg.Error as e:
                logger.debug(f"An error occurred attempting to transcode {f}: {e}")
                raise Exception(f"An error occurred: {e} attempting to transcode {f}")
            # Decode the metadata
            report=cleaner.report(output_path)
            # Make it palatable to Pure radio
            cleanResult=cleaner.clean(output_path)
            if cleanResult!= "Cleaned":
                os.remove(output_path)
                raise Exception(f"Cleaning error: {cleanResult}")
        
        elif f.lower().find(".jpg") > -1 or f.lower().find(".pdf") >-1 and copied<=copyConstraint:
                input_path = sourceDir+"/"+f
                output_path = strip_accents(mp3Dir+"/"+f)
                output_dir = "/".join(output_path.split("/")[0:-1])
                os.makedirs(output_dir, exist_ok=True)
                rc=shutil.copy2(input_path, output_dir)
                if f in updates: msgInsert = "updated"
                else: msgInsert = "missing"
                if rc==output_path:
                    copied = copied+1
                    logger.info(f"Copied {msgInsert} {f} to {output_path}. ({transcoded+copied+skipped} of {len(updates+additions)}). ")
                    if cleaner.report(output_path)=="Overlength":
                        cleanResult=cleaner.clean(output_path)
                        if cleanResult!= "Cleaned":
                            os.remove(output_path)
                            raise Exception(f"Cleaning error: {cleanResult}") # Make it palatable to Pure radio
                else:
                    raise Exception(f"Failed copy of {input_path} to {output_path}. cp returned {rc}")
        
        elif f.lower().find(".m3u") >-1 and copied<=copyConstraint: # Playlists with absolute urls (filepathjs)
                                                                    # don't work when relocated.
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
        try: #it may be that the directory has been repopulated by transcoding.
            # Doesn't work:  os.remove(f+"/.DS_Store")
            os.removedirs(f)
        except OSError as e:
            logger.info(f"Attempt to delete sometime-empty directory {f} failed with error: {e}")
        else: logger.info(f"Deleted empty directory {f}")
        
logger.info(f"Transcoding done")
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

