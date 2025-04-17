##!/usr/bin/env python3
"""
//
//  Refresh Music Server
//
//  Utility to Id3 tags to Json

//  Created by Timothy Banks on 16/04/2025.
//
"""

import eyed3, os.path, pprint
import eyed3.plugins.jsontag as jsontag

def show_info(path):
    audio = eyed3.load(path)

    if not audio.tag:
            audio.initTag()
            
    #audio.tag.release_date="1991"
    #audio.tag.save()
    #pprint.pprint(dir(audio.tag))
    
    """print(audio.tag.getBestDate())
    print(audio.tag.artist)
    print(audio.tag.album)
    print(audio.tag.title)
    """
    breakpoint()
    
    return audio.tag
    
def json(path):
    audio = eyed3.load(path)

    if not audio.tag:
            audio.initTag()
            
    #audio.tag.release_date="1991"
    #audio.tag.save()
    #pprint.pprint(dir(audio.tag))
    
    """print(audio.tag.getBestDate())
    print(audio.tag.artist)
    print(audio.tag.album)
    print(audio.tag.title)
    """
    breakpoint()
    
    return jsontag.audioFileToJson(audio)
        
tags = json(os.path.join('/Volumes',
                                'Media',
                                'Shared Music',
                                'Music Library',
                                'LydiaM',
                                'Bach S and Ps for solo Violin',
                                 '01 Adagio  BWV 1001.mp3' # '02 Adagio BWV 1001 Bounced.m4a',
                                ))
                                
pprint.pprint(tags)


