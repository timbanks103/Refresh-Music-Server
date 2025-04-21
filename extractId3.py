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
import os, sys, logging
# One of the following may work... (tbc)
from mutagen.id3  import ID3
from mutagen.mp4 import MP4

import eyed3
import eyed3.plugins.jsontag as jsontag
from tinytag import TinyTag
import audio_metadata

import json

file_handler = logging.FileHandler(filename='extractId3.log')
stdout_handler = logging.StreamHandler(stream=sys.stdout)
handlers = [file_handler, stdout_handler]
logging.basicConfig(
        format='[%(asctime)s] {%(filename)s:%(lineno)d} %(levelname)s - %(message)s',
        handlers=handlers,
        level=logging.INFO)
logger = logging.getLogger(__name__)

def show_info(path):
    
    audio.tag=TinyTag.get(path)
    """
    audio = eyed3.load(path)
    if not hasattr(audio, 'tag'):
            audio.tag= ID3(path)
            if not hasattr(audio, 'tag'):
                audio.initTag()
    """
            
    #audio.tag.release_date="1991"
    #audio.tag.save()
    #pprint.pprint(dir(audio.tag))
    
    """print(audio.tag.getBestDate())
    print(audio.tag.artist)
    print(audio.tag.album)
    print(audio.tag.title)
    """
    
    return  jsonaudio.tag
    
def json(path):
    import json
    import audio_metadata
    

    #audioTag=TinyTag.get(path)
    """
    audio = eyed3.load(path)
    if not hasattr(audio, 'tag'):
            audio.tag= ID3(path)
            if not hasattr(audio, 'tag'):
                audio.initTag()
    """
    """
    if path.lower().endswith("m4a"): audioTag=MP4(path)
    elif path.lower().endswith("mp3"): audioTag= ID3(path)
    """
    #audio.tag.release_date="1991"
    #audio.tag.save()
    #pprint.pprint(dir(audio.tag))
    
    """print(audio.tag.getBestDate())
    print(audio.tag.artist)
    print(audio.tag.album)
    print(audio.tag.title)
    """
    metadata = audio_metadata.load(path)
    breakpoint()
    return  json.dumps(metadata)  #jsontag.audioFileToJson(audio)
        
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
for (r,ds,ls) in os.walk(libraryPath,topdown=True):
  #  if len(ds)==0:
        for l in ls:
            if (l.find(".m4a") > -1 or l.find(".mp3") > -1 ):
                jsonTags = json(os.path.join(libraryPath,r,l))
                breakpoint()
                output_path = os.path.join(metaDataRootPath,r,l)
                output_dir = "/".join(output_path.split("/")[0:-1])
                os.makedirs(output_dir, exist_ok=True)
                with open(output_path, 'w') as f:
                    f.write(jsonTags)

# mutagen seems an easier module to use than eyed3


#                ffmpeg.input(input_path).output(output_path,loglevel="quiet").run(overwrite_output=True"""-map_metadata -1  -f ffmetadata metadata.txt    """)

"""  Take note of encoder and bit rate parameters
Encoder    Param    Qmin    Qmax    Qdef    Recommended    Notes
libfdk_aac    -vbr    1    5    ?    4 (~128kbps)    Currently the highest quality encoder.
"""
