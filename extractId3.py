##!/usr/bin/env python3
"""
//
//  Refresh Music Server
//
//  Utility to
//  o Extract Id3 tags to Json
//  o Transcode file to AIFF (or WAV?) - which doesn;t support metadata
//    and back to m4a
//  o Re-attach the metadata
//  With luck, the files will then be playable on Pure radio!  
//
//  Created by Timothy Banks on 16/04/2025.
//
"""

import os.path, pprint

import ffmpeg
from PIL import Image
from io import BytesIO
import metadataCleaning

import os, sys, logging, json
from pathlib import Path
from pprint import pformat, pprint
from mutagen.id3 import ID3, TALB, TCOM, TIT1, TIT2, TIT3, TRCK, TPOS, APIC, TPE1, TPE2, TXXX, TCON, TDRC, TENC, TSSE
from mutagen.mp3 import MP3
from functools import reduce

# Match a string in any item in a list of strings
def smatch(string,matchList):
    rlist=[]
    for m in matchList:
        if m in string: rlist.append(m)
    return rlist

def main():
    file_handler = logging.FileHandler(filename='extractId3.log')
    stdout_handler = logging.StreamHandler(stream=sys.stdout)
    handlers = [file_handler, stdout_handler]
    logging.basicConfig(
            format='[%(asctime)s] {%(filename)s:%(lineno)d} %(levelname)s - %(message)s',
            handlers=handlers,
            level=logging.DEBUG)
    logger = logging.getLogger(__name__)

    cleaner=metadataCleaning.MDcleaner(logger)
    cleaner.logger.setLevel(logging.DEBUG)

    # Extract metadata including artwork
    libraryPath = os.path.join('/Volumes',
                        'Media',
                        'Shared Music',
                        'MusicMP3',
                        )

    metaDataRootPath = os.path.join('/Volumes',
                            'Media',
                            'Shared Music',
                            'm4a Archive',
                            'iTunes',
                            'metaData'
                            )
                            

    albumNamesTracks={   # Match partial album name (distinct values) and track number prefix
                    #"Sonatas and Partitas":"2-08",
                    "Sonatas and Partitas":"2-16",
                    "Goldberg Variations!":"3-04",
                    "Nocturnes!":"",
                    "Best Of Satie!":"",
                    "Rake's Progress!":"1-0"
                    }
                    
    
    cleaner.logger.info(f"Searching for paths in {cleaner.dir} matching any of {pformat(albumNamesTracks)}.")
    for (r,ds,ls) in os.walk(cleaner.dir,topdown=True):
        #if ds==[]:
        for an in smatch(r,albumNamesTracks.keys()):
            for l in filter(lambda m: m.endswith(".mp3") and m not in cleaner.fnameExclusions, ls):
                filePath = os.path.join(r,l)#  lcleaner.dir+"/"+r[cleaner.dlen+1:]+"/"+l
                if l.startswith(albumNamesTracks[an]):
                    
                    if cleaner.report(filePath).startswith("Overlength"):
                        cleaner.longList.append(filePath)
                    
                    
                    
                    
                    
                    #if len(sys.argv)>1 and sys.argv[1]=="clean":
                    #    cleaner.clean(filePath) # Cleans all frames (including dubious TXXX and  frames) and creates a new ID3v2.2 tag
                                                # using simplified original data.
                     
                        frames = ID3(filePath)
                        picframes=frames.getall("APIC")
                        if(len(picframes)>0):
                            breakpoint()
                            # Compress the image
                            img = Image.open(BytesIO(picframes[0].data))
                            
                            ###imgPath=os.path.join(r,l.split()[0]+" Cover.jpg")
                            ###img.save(imgPath)
                        
                            byteIO = BytesIO()
                            img.save(byteIO, format='JPEG', optimize=True)
                            picframes[0].data=byteIO.getvalue()
                            picframes[0].mime="image/jpeg"
                            desc="compressed by metadataCleaning"
                            frames.save(filePath)
                    
                    
                    
                    
if __name__ == "__main__":
    main()
    exit
