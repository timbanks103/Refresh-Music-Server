#!/usr/bin/env python3
"""  main.py
//  Compare historical Music directories to identify lost contents
//
//  Created by Timothy Banks on 30/03/2025.
//
//  This script can be run
//     by invoking python3 with this file as the mail argument.  It runs in terminal mode.
//
//  Examines the master library directory for files that are missing compared to a candidate 
//  directory, preferring .m4a encoded if these are found.     
//
//  Copies the music file to the "Batched Automatically Add to Music" directory of the master collection. 
//  Files can be inspected there before moving to the "Automatically Add to Music" directory.
//
//  Ancilliary files  (.jpg and .pdf) are copied to the appropriate library subdirectory.  It helps to ensure 
//  metadata is correctly set to justify this location. 
//
//
"""

# Get the list of albums, then tracks and for each and determine what needs to be done.

import os, sys, logging
import pdb # debugger   - use breakpoint()
from pprint import pformat

import unicodedata
def strip_accents(s):
    return ''.join(c for c in unicodedata.normalize('NFD', s)
                            if unicodedata.category(c) != 'Mn')


file_handler = logging.FileHandler(filename='findForgotten.log')
stdout_handler = logging.StreamHandler(stream=sys.stdout)
handlers = [file_handler, stdout_handler]
logging.basicConfig(
        format='[%(asctime)s] {%(filename)s:%(lineno)d} %(levelname)s - %(message)s',
        handlers=handlers,
        level=logging.INFO)
logger = logging.getLogger(__name__)


masterDir = '/Volumes/Media/Shared Music/Music Library' # Master - curated source of all music
candidateDir = '/Volumes/Media/Shared Music/Hidden-m4a/iTunes/Music' # A historical version, hopefully uncorrupted.
#candidateDir = '/Volumes/Media/Shared Music/iTunesMP3 - retired/Music'
addToLibraryDir =  '/Volumes/Media/Shared Music/Music Library/Batched Automatically Add to Music.localized' # Holding area
fnameExclusions=[".DS_Store",
                "Folder.jpg",  # Preserves existing artwork not present in Mac OS  Music.app
                "folder.jpg" ]
dnameExclusions=["Automatically Add to Music.localized",
                "Automatically Add to iTunes.localized",
                "Music Library.musiclibrary",
                ".localized",
                ".AppleDouble"
                ]
#examConstraint = 10000000
copyConstraint = 300
improveConstraint=0

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
            """if "Automatically Add to iTunes.localized" in r:
                print("found auto add to it")
                breakpoint()
            """
            if l not in fnameExclusions and r[dlen+1:].replace("/.AppleDouble","").rsplit("/")[0] not in dnameExclusions and not l.startswith("."):
                # and len(candidateList) <= examConstraint:
                    candidateDates[r[dlen+1:]+"/"+l]=os.path.getmtime(r+"/"+l)
                    candidateList.append(r[dlen+1:]+"/"+l)# l.replace(".mp3", ""))
                
candidateList.sort()

# Avoid confusion created by accented characters
candidateListStripped=[strip_accents(s) for s in candidateList]
masterListStripped=[strip_accents(s) for s in masterList]

masterListNoType = [f[0:-4] for f in masterList]  # ignores file type
masterListStrippedNoType = [f[0:-4] for f in masterListStripped]  # ignores file type

# Report the discoveries


missingm4a=[f for f in candidateList if f.replace("/.AppleDouble","") not in masterList #was stripped/stripped
        and f.lower().endswith(".m4a")
        ]
        
missingm4aLower= [f.replace(".M4A",".m4a") for f in missingm4a]

missing=[f for f in candidateList if not f.lower().endswith(".m4a") # was stripped
        and f[:-4].replace("/.AppleDouble","") not in masterListNoType  # was stripped
        and f.replace(".M4A",".m4a") not in missingm4aLower
        ]

improvements = [f for f in candidateListStripped if f[-4:].lower()=="m4a"
                and f[0:-4].replace("/.AppleDouble","") in masterListStrippedNoType  # The type-less name is there but...
                and f.replace("/.AppleDouble","") not in masterListStripped   # not in an m4a version.
                ]
    
w=220 # Width of output - some filenames are very long.

logger.info(' ')
logger.info("m4a or M4A Files in "+candidateDir+" missing from "+masterDir+":")
logger.info(pformat(missingm4a[0:300],width=w))
if len(missingm4a)>3 : print ("of "+str(len(missingm4a)))

logger.info(' ')
logger.info("Non m4a/M4A files in "+candidateDir+" missing from "+masterDir+"(ignoring actual file type): ")
logger.info(pformat(missing[0:300],width=w))
if len(missing)>3 : print ("of "+str(len(missing)))


logger.info(' ')
logger.info("Files in "+masterDir+" which have m4a versions in "+candidateDir+": ")
logger.info(pformat(improvements[0:10],width=w))
if len(improvements)>3 : print ("of "+str(len(improvements)))

##############sys.exit("mp3 upgrade supressed") # For now


# Convert video format

import shutil
# Input and output file paths
if len(missing+missingm4a)>0:
    copied=0
    for f in missing+missingm4a:
        # take care with file types in case we collected extraneous stuff
        if (f.lower().endswith(".mp3") or f.lower().endswith(".m4a") or f.lower().endswith(".jpg") or f.lower().endswith(".pdf")) and copied<=copyConstraint:
                """if f.lower().endswith(".mp3"):
                    print("This is mp3")
                    breakpoint()
                """
                input_path = (candidateDir+"/"+f).replace("/.AppleDouble","")
                if (f.lower().endswith(".mp3") or f.lower().endswith(".m4a")):
                    output_path = (addToLibraryDir+"/"+f).replace("/.AppleDouble","") # .AppleDouble is an impediment to regular cp
                    output_dir = "/".join(output_path.split("/")[0:-1])
                elif (f.lower().endswith(".jpg") or f.lower().endswith(".pdf")):
                    output_path = (masterDir+"/"+f).replace("/.AppleDouble","") # .AppleDouble is an impediment to regular cp
                    output_dir = "/".join(output_path.split("/")[0:-1])
                
                os.makedirs(output_dir, exist_ok=True)
                """print(">>>>>>>>>>>>>>>>>>about to copy to "+output_path)
                breakpoint()
                """
                if not os.path.exists(output_path):
                    rc=shutil.copy2(input_path, output_dir)
                    copied = copied+1
                else: rc=output_path+" (already exists). "  #  Don't replace it  - that's mission creep
        
                if output_path in rc:
                    logger.info(f"Copied {f} to {output_path}. ({copied} of {len(missing)+len(missingm4a)}). ")
            
                else:
                    raise Exception(f"Failed copy of {input_path} to {output_path}. cp returned {rc}")
              
        
else: logger.info("No copying needed. ")

sys.exit("incomplete") # for now

if len(improvements)>0:
        improved=0
        for f in improvements:
            if f.lower().endswith(".m4a") and improved<=improveConstraint:
                input_path = (candidateDir+"/"+f).replace("/.AppleDouble","")
                output_path = (addToLibraryDir+"/"+f).replace("/.AppleDouble","")
                output_dir = "/".join(output_path.split("/")[0:-1])
                shutil.copy2(input_path, output_dir)

                if rc==output_path:
                    copied = copied+1
                    logger.info(f"Copied {f} to {output_path}. ({copied} of {len(additions)}). ")
                    
                else:
                    raise Exception(f"Failed copy of {input_path} to {output_path}. cp returned {rc}")
                    
else: logger.info("No improvements available. ")
# References:
"""
This discussion suggests how to do the comparison to detect absences in the transcoded collection using a shell script.
https://unix.stackexchange.com/questions/4362/recursively-compare-directory-contents-by-name-ignoring-file-extensions
"""


