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
from metadataCleaning import pureMangle
import json
import ffmpeg, shutil
import math




def transLogger(level):
    info_handler = logging.FileHandler(filename='transcoding.log')
    
    warnings_handler = logging.FileHandler(filename='Warnings.log')
    warnings_handler.setLevel(logging.WARNING)
    
    stdout_handler = logging.StreamHandler(stream=sys.stdout)
    handlers = [info_handler, stdout_handler, warnings_handler ]
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
findKinds =[".m4a",".mp3",".M4A",".MP3",".jpg",".m3u",".m3u8",".pdf"]
musicKinds =[".m4a",".mp3",".M4A",".MP3"]

# Damage limitation
#examConstraint = 10000000
transcodeConstraint = 5000
copyConstraint = 5000
removalConstraint = 5000
searchConstraint = ""
# This query reports if a higher quality version ould be made...  Need to erase the old version and let the search fill the missing pieces.
# grep -m 1 'Ostinata' sourceRates.txt & grep -m 1 'Ostinata'  mp3Rates.txt

sourceDir = '/Volumes/Media/Shared Music/Music Library' # Source of all music
sourceList=[]
sourceDates={}
sourceRates={}
dlen=len(sourceDir)
    
for (r,ds,ls) in ((x,ys,zs) for (x,ys,zs) in os.walk(sourceDir,topdown=True) if searchConstraint in x):
# or metadataCleaning.smatch(searchConstraint,zs)):
  #  if len(ds)==0:
        for l in ls:
            if l not in fnameExclusions and r[dlen+1:].split("/")[0] not in dnameExclusions and not l.startswith("."): # and len(sourceList) <= examConstraint:
                leafRelPath=os.path.join(r[dlen+1:],l)
                sourceDates[leafRelPath]=os.path.getmtime(os.path.join(r,l))
                if os.path.splitext(l)[1] in findKinds:
                    sourceList.append(leafRelPath)

sourceList.sort()


mp3Dir = '/Volumes/Media/Shared Music/MusicMP3/Music'
mp3List=[]
mp3Dates={}
mp3Rates={}
emptydirs=[]
dlen=len(mp3Dir)

for (r,ds,ls) in ((x,ys,zs) for (x,ys,zs) in os.walk(mp3Dir,topdown=True) if searchConstraint in x):
#or metadataCleaning.smatch(searchConstraint,zs)):
        if ls==[]: emptydirs.append(r)
        for l in ls:
            if l not in fnameExclusions: # and len(mp3List) <= examConstraint:
                leafRelPath=os.path.join(r[dlen+1:],l)
                mp3List.append(leafRelPath)
                mp3Dates[leafRelPath]=os.path.getmtime(os.path.join(r,l))
                
mp3List.sort()

strippedSourceList=[pureMangle(f,filePath=True) for f in sourceList]
strippedSourceDates={pureMangle(f,filePath=True):sourceDates[f] for f in list(sourceDates.keys())}
strippedSourceRates={pureMangle(f,filePath=True):sourceRates[f] for f in list(sourceRates.keys())}


from collections import Counter
# NB & TBD? The statistics would be easier to read if averaged by album.
sourceRateStats = Counter(sourceRates.values())
sourceStats=pformat(dict(sorted(sourceRateStats.items(), key=lambda item: item[1]))) # Sort and format (ready for writelines)
sourceLowRates=pformat({(f,mp3Rates[f]) for f in mp3Rates.keys() if mp3Rates[f]<130})
sourceHighRates=pformat({(f,mp3Rates[f]) for f in mp3Rates.keys() if mp3Rates[f]>300})

mp3RateStats = Counter(mp3Rates.values())
mp3Stats=pformat(dict(sorted(mp3RateStats.items(), key=lambda item: item[1]))) # Sort and format (ready for writelines)
mp3LowRates=pformat({(f,mp3Rates[f]) for f in mp3Rates.keys() if mp3Rates[f]<130})
mp3HighRates=pformat({(f,mp3Rates[f]) for f in mp3Rates.keys() if mp3Rates[f]>250})
writeablemp3Rates=pformat(dict(mp3Rates))
"""
How to write the stats files...  
r3low=open("mp3LowRates.txt","w")
r3low.writelines(mp3LowRates)
r3low.close()

similarly for stats, highRates, Rates

A succinct way to interrogate the results via the terminal command line: 
>% grep -m 1  albumname sourceRates.txt & grep -m 1 albumname mp3Rates.txt
"""



# Report the discoveries
additions=[f for f in sourceList if pureMangle(f,filePath=True).replace(".m4a", ".mp3").replace(".M4A", ".mp3") not in mp3List]
removals=[f for f in mp3List if f not in strippedSourceList and f.replace(".mp3", ".m4a") not in strippedSourceList and f.replace(".mp3", ".M4A") not in strippedSourceList ]
updates=[f for f in sourceList if (f not in additions and \
    (sourceDates[f]>mp3Dates[pureMangle(f,filePath=True).replace(".m4a", ".mp3").replace(".M4A", ".mp3")] \
    or\
     sourceDates[f]>mp3Dates[pureMangle(f,filePath=True).replace(".m4a", ".mp3").replace(".M4A", ".mp3")])) ]

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
"""
logger.info("Input Rates are:")
logger.info(pformat(updates[0:3]))
if len(updates)>3: logger.info("of "+str(len(updates)))
"""
logger.info("Source rate statistics: \n"+pformat(dict(sorted(sourceRateStats.items(), key=lambda item: item[1]))))


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

# if python-ffmpeg installed  -> from ffmpeg import FFmpeg
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
            ht=os.path.split(f)
            f = os.path.join(ht[0],pureMangle(ht[1],filePath=True))
            output_path = pureMangle(mp3Dir+"/"+f.replace(".m4a", ".mp3").replace(".M4A", ".mp3"),filePath=True)
            output_dir = "/".join(output_path.split("/")[0:-1])
            os.makedirs(output_dir, exist_ok=True)
            try:
                """
                This is the python-ffmpeg version 
                For full docs see https://python-ffmpeg.readthedocs.io/en/stable/examples/transcoding/
                ffprobe = FFmpeg(executable="ffprobe").input(
                    input_path,
                    print_format="json", # ffprobe will output the results in JSON format
                    show_streams=None,
                )

                media = json.loads(ffprobe.execute())

                bit_rate=int(media['streams'][0]["bit_rate"])
                """
                media = ffmpeg.probe(input_path, cmd='ffprobe')
                bit_rate=int(media['streams'][0]["bit_rate"])
                
                #duffers audio_quality=100, acode='libfaac'
               # ffmpeg.input(input_path).output(output_path,loglevel="quiet", acodec='mp3', audio_bitrate=160000, joint_stereo=1)
                ffmpeg.input(input_path).output(output_path, loglevel="quiet", acodec='mp3', audio_bitrate=bit_rate, joint_stereo=1) \
                    .run(overwrite_output=True) # ouput(,acodec="copy"  causes error
                                                # need to find a way to specify -codec:a libmp3lame  -q:a 3
                                                # and  -joint_stereo 1
                if f in updates: msgInsert = "updated"
                else: msgInsert = "missing"
                transcoded=transcoded+1
                logger.info(f"Successfully converted {msgInsert} {input_path} to {output_path}. ({transcoded+copied} of {len(updates+additions)}). ")
                
            except ffmpeg.errors as e:
                logger.debug(f"An error occurred attempting to transcode {f}: {e}")
                raise Exception(f"An error occurred: {e} attempting to transcode {f}")
            # Decode the metadata
            report=cleaner.report(output_path)
            # Make it palatable to Pure radio
            cleanResult=cleaner.clean(output_path)
            
        elif f.lower().find(".jpg") > -1 or f.lower().find(".pdf") >-1 and copied<=copyConstraint:
                input_path = sourceDir+"/"+f
                output_path = pureMangle(mp3Dir+"/"+f,filePath=True)
                output_dir = "/".join(output_path.split("/")[0:-1])
                os.makedirs(output_dir, exist_ok=True)
                cpout=shutil.copy2(input_path, output_dir)
                rc=shutil.move(cpout, output_path)
                if f in updates: msgInsert = "updated"
                else: msgInsert = "missing"
                if rc==output_path:
                    copied = copied+1
                    logger.info(f"Copied {msgInsert} {f} to {output_path}. ({transcoded+copied+skipped} of {len(updates+additions)}). ")
        
                else:
                    raise Exception(f"Failed copy of {input_path} to {output_path}. cp returned {rc}")
        
        elif f.lower().find(".m3u") >-1 and copied<=copyConstraint: # Playlists with absolute urls (filepaths)
                                                                    # don't work when relocated. Make relocateable and translate to match
                                                                    # the mp3 view of the world.
                input_path = sourceDir+"/"+f
                output_path = pureMangle(mp3Dir+"/"+f,filePath=True)
                output_dir = "/".join(output_path.split("/")[0:-1])
                os.makedirs(output_dir, exist_ok=True)
                
                # Edit the file to replace m4a with mp3 and convert absolute paths to relative.
                fileLines=[]  # Read in the file line by line
                
                with open(input_path, 'r') as file:
                    for line in file: # Replace the target strings
                        fileLines.append(pureMangle(line,filePath=True).replace(sourceDir, '.').replace('.m4a','.mp3'))
                # Write the file out again
                with open(output_path, 'w') as outFile:
                    outFile.writelines(fileLines)
                
                if f in updates: msgInsert = "updated"
                else: msgInsert = "missing"
                
                copied = copied+1
                logger.info(f"Copied/translated {msgInsert} {f} to {output_path}. ({transcoded+copied+skipped} of {len(updates+additions)}). ")
                    
                #else: # HOW CAN THIS FAIL??
                #   raise Exception(f"Failed copy of {input_path} to {output_path}. cp returned {rc}")
        
        else:
            skipped=skipped+1
            logger.info(f"Skipped {f}. Wrong file type. ({transcoded+copied+skipped} of {len(updates+additions)}). ")
            
        
                    
else: logger.info("No transcoding or copying needed. ")

# Clean away emptied directires (due to tweaking of album title, for exmaple.
# If a directory is mentioned in the additions/updates, it probably isn't empty now, so avoid a noisy failed attempt to remove.

emptydirs= [f for f in emptydirs \
    if metadataCleaning.smatch(os.path.split(f)[1], # Look for the album directory name
        updates+additions)==[]]

if len(emptydirs)>0:
    emptied=0
    for f in emptydirs:
        try:
            workdir=os.listdir(f)
            if len(workdir)==1 and '.DS_Store' in workdir:
                shutil.rmtree(f)# , ignore_errors=True)  # Deletes back up the tree if the parent is empty
            else: os.removedirs(f) # If there are any contents, this will fail with "not empty"
        except OSError as e:
            logger.warning(f"Attempt to delete sometime-empty directory {f} failed with error: {e}")
        else: logger.info(f"Deleted empty directory {f}")
        
logger.info(f"Transcoding done")


#This command lists all directories which only have .DS_Store: 
#braces={} find TARGET_PATH -type d \( -empty -o -exec sh -c '
#    echo | find "$1" ! \( -type f -name .DS_Store \) -exec sh -c "
#      for f do read dummy || { kill -s INT \"\$PPID\"; exit 1; } ; done
#   " inner-sh "$braces" +
#' outer-sh {} \; \) -print
#
#From  https://superuser.com/questions/1732756/find-folders-that-contain-only-one-specific-file-ds-store-and-no-others



# References:
"""
This discussion suggests how to do the comparison to detect absences in the transcoded collection using a shell script.
https://unix.stackexchange.com/questions/4362/recursively-compare-directory-contents-by-name-ignoring-file-extensions
"""

