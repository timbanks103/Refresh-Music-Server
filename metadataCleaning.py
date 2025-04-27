#!/usr/bin/env python3
"""  main.py
//  Cleaning Music
//
//  Created by Timothy Banks on 07/03/2025.
//  
//  This script can be run 
//     by invoking python3 with this file as the mail argument.  It runs in terminal mode.
//
//   These classes havediscovered that chnaging the length of the TIT2 (track title) frame of ID3 from long to short - namely from 
//   "Arib Mit 30 Veranderungen, BWV 988 - "Gildberg Variations": Var. 18 Canone alla Sesta a 1 Clav."
//   to 
//   "Variatio 18. Canone alla Sesta a 1 Clav."   
//   makes the track digestible by Pure radios.  Reversing the change produces re-occurence of indigestion. 
//
//   Annoyingly, only the Apple Music app is able to produce consumable ID3 metadata. Notably, the programmatic approach through 
//   Python and the mutagen package creates similar indigestion problems even when the track title is shortened.
//   (but the vocabulary of frame has always been missing the TIT1 frameID, so this needs to be re-attempted)
//   The order of frames may also be important - in those produced by Apple Music, the TALB, TIT1 and TIT2 appearin the 'correct'
//   order of information hieracrchy (it's a long shot, but worth a try to rearrange the mutagen construction).
// 
//   There's also the suspicion that the TXXX=sort_name frame is present in original failing tracks, but it is removed by Music
//   when the trck title is edited. This may be a red herring. 
//  
"""

# Get the list of albums, then tracks and for each and determine what needs to be done.

import os, sys, logging, json
from pathlib import Path
from pprint import pformat, pprint
from mutagen.id3 import ID3, TALB, TCOM, TIT1, TIT2, TIT3, TRCK, TPOS, APIC, TPE1, TPE2, TXXX  # TPE1, , TYER
from mutagen.mp3 import MP3
from functools import reduce


class Metadata:
    def __init__(self, tags):
        # Notes are from
        #   https://id3.org/id3v2.3.0#Declared_ID3v2_frames
        
        ks = tags.keys()
        if "TALB" in ks: self.album = tags["TALB"].text[0] # Album/Movie/Show title
        if "TIT1" in ks: self.grouping = tags["TIT1"].text[0] # TIT1 Content group description
        if "TIT2" in ks: self.title = tags["TIT2"].text[0] # Title/songname/content description
        if "TCOM" in ks: self.composer = tags["TCOM"].text[0] # Composer
        if "TRCK" in ks: self.trackNo = tags["TRCK"].text[0] # Track number/Position in set
        if "TPOS" in ks: self.diskNo = tags["TPOS"].text[0] # Disk no in set
        if "TIT3" in ks: self.subtitle = tags["TIT3"].text[0] # Subtitle/Description refinement
        if "APIC" in ks: self.artwork = tags["APIC"] # Attached picture
        if "TPE1" in ks: self.leadArtist = tags["TPE1"].text[0] # Lead artist(s)/Lead performer(s)/Soloist(s)/Performing group
        if "TPE2" in ks: self.backingArtist = tags["TPE2"].text[0] # Band/Orchestra/Accompaniment (aka Album artist)
        txs={tx.desc:tx.text[0] for tx in tags.getall("TXXX") if tx.desc=="comment"}
        if "comment" in txs.keys(): self.comment = txs["comment"]
        #tags['TYER'] # year

class MDcleaner:
    def __init__(self,logger=None, dir='/Volumes/Media/Shared Music/MusicMP3'):

    
        #masterDir = '/Volumes/Media/Shared Music/Music Library' # Master - curated source of all music
        self.dir = dir # Server library.
        self.dlen=len(self.dir)
        self.fnameExclusions=[".DS_Store",
                        "Folder.jpg",  # Preserves existing artwork not present in Mac OS  Music.app
                        "folder.jpg" ]
        self.dnameExclusions=["Automatically Add to Music.localized",
                        "Music Library.musiclibrary",
                        ".localized"
                        ]
        if logger==None:
            file_handler = logging.FileHandler(filename='MDclean.log')
            stdout_handler = logging.StreamHandler(stream=sys.stdout)
            handlers = [file_handler, stdout_handler]
            logging.basicConfig(
                    format='[%(asctime)s] {%(filename)s:%(lineno)d} %(levelname)s - %(message)s',
                    handlers=handlers,
                    level=logging.INFO)
            self.logger = logging.getLogger(__name__)
        else: self.logger=logger
        self.w=1220 # Width of output - some filenames are very long.
        self.tlimit=63 # Longest length allowed. Truncation is done to this length
        self.logger.debug(f"Metadatacleaning for files with ?? maybe over-long metadata (title over {self.tlimit} characters):")
        self.longList=[]
               
        self.changeLimit=500
        self.changes=0


    def clean(self,filePath):
        pathcs = list(Path(filePath).parts)
        if pathcs[-1] not in self.fnameExclusions and pathcs[-2] not in self.dnameExclusions and pathcs[-1] not in self.dnameExclusions:
            tags = ID3(filePath)
            metadata = Metadata(tags)
            if self.changes < self.changeLimit:
                if hasattr(metadata,'comment') and "Unplayable" in metadata.comment:
                    breakpoint() # Unplayable detected
                    self.logger.warning(pformat(f"Deleting {filePath} ({metadata.comment})",width=self.w))
                    os.remove(filePath)
                    self.changes=self.changes+1
                    return("Cleaned") # Brutal, but true
                self.logger.info(pformat("Cleaning "+filePath,width=self.w))
                # Try to extract/create a meaningful title algorithmicly
                if hasattr(metadata,'grouping') and (metadata.grouping=='Italian Concerto in F, BWV 971' or metadata.grouping=='Aria mit 30 Veränderungen, BWV 988 "Goldberg Variations"'):
                    if metadata.title.find('ations": ')>0:
                        metadata.title = metadata.title[metadata.title.find('ations": ')+9:]
                        metadata.title= metadata.title.replace('Var. ','Variatio ')
                    else:
                        metadata.title=metadata.title[-self.tlimit:]
                
                else: # The default, brutal approach
                    metadata.title = metadata.title[-self.tlimit:] # The most pertinent title information is often at the end.
                    metadata.album = metadata.album[0:self.tlimit] # It's best to keep the album name close to it's full title sort spot.
                    
                # Apply final, strict limits for the tags used in Pure and clear the TXXX frames (in case it matters)
                fidVals={k:tags[k].text[0][0:self.tlimit] for k in \
                    filter(lambda kl: kl in ["TALB","TIT1","TIT2","TCOM"], tags.keys())}
                for k in fidVals.keys(): tags.add(eval(k)(text=[fidVals[k]]))
                tags.delall("TXXX") # They could be converted to COMM frames
                tags.delall("APIC")  # Try it - some pictures are seemingly huge.
                
                tags.delete() # NEW! Scrap the whole thing...
                
                
                tags.save(filePath,v2_version=3)
                self.changes=self.changes+1
                return("Cleaned")
            else:
                self.logger.info(f"Change limit ({self.changeLimit}) reached")
                return("Limit Reached")
                
                
    def clean2(self,filePath):
        
        return

    def report(self,filePath):
        pathcs = list(Path(filePath).parts)
        if pathcs[-1] not in self.fnameExclusions and pathcs[-2] not in self.dnameExclusions and pathcs[-1] not in self.dnameExclusions:
            tags = ID3(filePath)
            #breakpoint() # MD inspection point
            mp3 = MP3(filePath)
            f=open(filePath,"rb")
            baseHeader=f.read(10)
            
            headerReport={}
            # Decode the header bytes
            headerReport["headerID"] =", ".join(hex(b) for b in baseHeader[0:3]) +" ( = \""+baseHeader[0:3].decode("ascii") +"\")"
            headerReport["headerVersion"] = (", ".join(hex(b) for b in baseHeader[3:5])) + \
                "  (means ID3v2."+ str(int.from_bytes(baseHeader[3:4])) +"."+str(int.from_bytes(baseHeader[4:5]))+")"
            headerReport["headerFlags"]=", ".join(hex(b) for b in baseHeader[5:6]) + \
                " The header is extended: "+ str(bool(int.from_bytes(baseHeader[5:6])>> 6 &1 ))
            headerReport["tagSize"]=", ".join(hex(b) for b in baseHeader[6:]) +" (= decimal "+str( reduce(lambda a,b: a*128+b, baseHeader[6:], 0))+" excluding 10 bytes for header)"
            headerReport["mp3Score"] = MP3.score(filePath,f,baseHeader)
            
            # Also report the decoding done by mutagen
            for item in ["version","unknown_frames","size"]: headerReport[item] = getattr(tags,item)
            self.logger.info(f"\n\n\nHeader report for {filePath}:\n{pformat(headerReport, depth=2, indent=0, sort_dicts=True)}")
            self.logger.info(f"\n\nMP3 info: \n  {pformat(vars(mp3.info))}")
            
            # Report the frame text lengths
            fidReport={k:len(tags[k].text[0])for k in filter(lambda kl: kl in ["TALB","TIT1","TIT2","TCOM"], tags.keys())}
            if any(l > self.tlimit for l in iter(fidReport.values())):
                self.logger.info("\n\n\nFrame contents: \n"+tags.pprint())
                self.logger.info("Text lengths: \n"+json.dumps(fidReport, indent=4, sort_keys=True))
                return("Overlength")
            else:
                self.logger.debug("\n\n\nFrame contents: \n"+tags.pprint())
                self.logger.debug("Text lengths: \n"+json.dumps(fidReport, indent=4, sort_keys=True))
                return
                
# Match a string in any item in a list of strings
def smatch(string,matchList):
    rlist=[]
    for m in matchList:
        if m in string: rlist.append(m)
    return rlist
            
def main():
    albumNamesTracks={"Sonatas and Partitas?":"2-02","Goldberg Variation":"3-10"} # Match partial album name (distinct values) and track number prefix
    cleaner=MDcleaner()
    cleaner.logger.setLevel(logging.DEBUG)
    cleaner.logger.info(f"Searching for paths in {cleaner.dir} matching any of {pformat(albumNamesTracks)}.")
    for (r,ds,ls) in os.walk(cleaner.dir,topdown=True):
        #if ds==[]:
        for an in smatch(r,albumNamesTracks.keys()):
            for l in filter(lambda m: m.endswith(".mp3") and m not in cleaner.fnameExclusions, ls):
                filePath = os.path.join(r,l)#  lcleaner.dir+"/"+r[cleaner.dlen+1:]+"/"+l
                if l.startswith(albumNamesTracks[an]):
                    
                    if cleaner.report(filePath)=="Overlength" :#and cleaner.clean(filePath) == "Cleaned":
                        cleaner.longList.append(filePath)
                    else:
                        cleaner.report(filePath)
                       # cleaner.clean(filePath) == "Cleaned" # Cleans dubious TXXX frames
                        
                    
                    
    if len(cleaner.longList)==0:
        cleaner.logger.info("No updates")
    else:
        cleaner.logger.info(f"Changed {len(cleaner.longList)} files: \n{cleaner.longList} ")
    

    
if __name__ == "__main__":
    main()
    exit
