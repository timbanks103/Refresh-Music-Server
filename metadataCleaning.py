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
from mutagen.id3 import ID3, TALB, TCOM, TIT1, TIT2, TIT3, TRCK, TPOS, APIC, TPE1, TPE2, TXXX, TCON, TDRC, TENC, TSSE, TSOC, TSOA, COMM
from mutagen.mp3 import MP3
from PIL import Image
from io import BytesIO
from functools import reduce
import unicodedata
import urllib.parse


# Debussy Pelléas et Mélissande created problems for Pure radio...
def pureMangle(text,filePath=False):
    """
    Pure radios can't accept long metadata or urls
    Modify the input string to be consumable.  The length restrictions on metadata fields were
    discovered by experiment, so can't be explained and could be over-zealous.

    :param text: The input string.
    :type text: String.

    :returns: The processed String.
    :rtype: String.
    """
    if filePath:
        if text.endswith("\n"):
            newline="\n"
            text=text[0:-1]
        else: newline=""
        pathParts = list(Path(text).parts)
        root = pathParts[0:-3] if len(pathParts)>3 else []
        artistDir=pathParts[-3] if len(pathParts)>2 else ""
        albumDir=pathParts[-2] if len(pathParts)>1 else ""
        file = pathParts[-1]
        """
        root,file=os.path.split(text) # One of these operations strips newline from the end
        root,album=os.path.split(root)
        root,artist=os.path.split(root)
        """
        fn,ext=os.path.splitext(file)
        text=os.path.join(  *root,
                            artistDir[0:MDcleaner.class_slimit],
                            albumDir[0:MDcleaner.class_alimit],
                            fn[0:MDcleaner.class_tlimit]+ext+newline)
        
    try:
        text = unicode(text, 'utf-8')
    except (TypeError, NameError): # unicode is a default on python 3
        pass
    text = unicodedata.normalize('NFD', text)
    text = text.encode('ascii', 'ignore')
    text = text.decode("utf-8")
    
    return str(text)

class Metadata:
    def __init__(self, frames):
        # Notes are from
        #   https://id3.org/id3v2.3.0#Declared_ID3v2_frames
        
        ks = frames.keys()
        if "TALB" in ks: self.album = frames["TALB"].text[0] # Album/Movie/Show title
        if "TSOA" in ks: self.albumSort = frames["TSOA"].text[0] # Album sort order
        elif "TXXX:sort_album" in ks:
            self.albumSort = frames["TXXX:sort_album"].text[0] # early ID3V2.3? Used by Mac OS Music
        if "TIT1" in ks: self.grouping = frames["TIT1"].text[0] # TIT1 Content group description
        if "TIT2" in ks: self.title = frames["TIT2"].text[0] # Title/songname/content description
        if "TCOM" in ks: self.composer = frames["TCOM"].text[0] # Compose
        elif "TXXX:TCM" in ks:
            self.composer = frames["TXXX:TCM"].text[0] # early ID3V2.3?  Used by Mac OS Music
        if "TSOC" in ks: self.composerSort = frames["TSOC"].text[0] # Composer sort order
        elif "TXXX:sort_composer" in ks:
            self.composerSort = frames["TXXX:sort_composer"].text[0] # Used by Mac OS Music
        
        if "TRCK" in ks: self.trackNo = frames["TRCK"].text[0] # Track number/Position in set
        elif "TXXX:TPA" in ks:
            self.trackNo = frames["TXXX:TPA"].text[0]
        if "TPOS" in ks: self.diskNo = frames["TPOS"].text[0] # Disk no in set
        if "TDRC" in ks: self.recDate = frames["TDRC"].text[0] # Date of recording
        if "TIT3" in ks: self.subtitle = frames["TIT3"].text[0] # Subtitle/Description refinement
        if len([k for k in filter(lambda x: x.startswith("APIC"), ks)])>0:
                    self.artworks = frames.getall("APIC") # Attached pictures
                    aws={f.desc:len(f.data) for f in self.artworks}
                    self.awMax=max(list(aws.values())) # Max length of any artwork (there may be multiple)
                    self.sumAwLength = sum(list(aws.values()))
                    if "" in list(aws.keys()): self.coverAwLength=aws[""]
                    else: self.coverAwLength=aws[list(aws.keys())[0]] # The previous clean may have produced a more informative desc
        if "TPE1" in ks: self.leadArtist = frames["TPE1"].text[0] # Lead artist(s)/Lead performer(s)/Soloist(s)/Performing group
        if "TPE2" in ks: self.albumArtist = frames["TPE2"].text[0] # Album Artist/Band/Orchestra/Accompaniment
        if "TENC" in ks: self.encoder = frames["TENC"].text[0] # Encoded by
        if "TSSE" in ks: self.encoderSettings = frames["TSSE"].text[0] # Software/Hardware and settings used for encoding
        txs={}
        txs.update({tx.desc:tx.text[0] for tx in frames.getall("TXXX") if tx.desc=="comment"})
        txs.update({tx.desc:tx.text[0] for tx in frames.getall("COMM") if tx.desc=="comment"})
        if "comment" in txs.keys(): self.comment = txs["comment"]
        #frames['TYER'] # year
        
class CleaningReport:
    def __init__(self):
        self.overlengthSomething=False
        self.overlengthAlbum=False
        self.overlengthAlbumSort=False
        self.overlengthArtist=False
        self.overlengthAlbumArtist=False
        self.overlengthTitle=False
        self.repetitiveTitle=False
        self.overlengthGrouping=False
        self.overlengthPicture=False
        self.overlengthComposer=False
        self.overlengthComposerSort=False # Probably(?) never transmitted to the renderer and only used in the server for creating indices.
        self.overlengthUrl=False


class MDcleaner:
    class_alimit=40 # Longest text for album name
    class_glimit=40 # Longest text for grouping name
    class_tlimit=63 # Longest text for track title
    class_slimit=30 # Longest text for lead/album artist
    class_climit=20 # Longest text for composer
    class_plimit=20000 # Longest header size allowed (bytes).  Picture resizing and compression is done beyond this (it may not succeed in reducing the size)
    class_psize=250 # New picture size (pixels, longest edge) for shrinking. This produces an compressed picture about 8K long.
    # Total length of url components (album artist/album/title) = 133 + 4 for file extension + root directory length (on server - about 37) total about 204
    class_ulimit=215 # Url limit check - a longer URL causes a warning (and should be impossible)
    #Make-ready for reporting of lengths.
    maxes={
            "TALB":class_alimit,
            "TSOA":class_alimit,
            "TIT1":class_glimit,
            "TIT2":class_tlimit,
            "TPE1":class_slimit,
            "TPE2":class_slimit,
            "TCOM":class_climit,
            "TSOC":class_climit
    }
    """ 
        The length, plus the added length of the root directory and path serparators must be limited. 
        Experiments have shown that with a root diretory on the server of "/http://192.168.0.52:9795/minimserver/*/", (40 characters)  
        the known limit for music library components is reached near 215 characters.  (total 255)
        
        Observations show that minimserver seems to mangle/truncate urls to achieve a length near to 172 characters.
    """
    class_chlimit=5000 # Maximum number of files to be cleaned.
    
    
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
            warnings_handler = logging.FileHandler(filename='Warnings.log')
            warnings_handler.setLevel(logging.WARNING)
            
            handlers = [file_handler, stdout_handler, warnings_handler]
            logging.basicConfig(
                    format='[%(asctime)s] {%(filename)s:%(lineno)d} %(levelname)s - %(message)s',
                    handlers=handlers,
                    level=logging.INFO)
            self.logger = logging.getLogger(__name__)
        else: self.logger=logger
        self.logWidth=1220 # Width of output - some filenames are very long.
        self.tlimit=MDcleaner.class_tlimit # Longest text length allowed. Truncation is done to this length
        self.alimit=MDcleaner.class_alimit # Longest text for album name
        self.glimit=MDcleaner.class_glimit # Longest text for grouping name
        self.slimit=MDcleaner.class_slimit # Longest text for lead artist (a folder name if Music organises the folders (it does))
        self.plimit=MDcleaner.class_plimit # Largest picture allowed. If in excess, the image is compressed. Or deleted?
        self.psize= MDcleaner.class_psize # Embedded picture size if resizing happens.
        self.ulimit=MDcleaner.class_ulimit # Largest encoded filepath. Maybe Pure can tolerate bigger - certainly lower that 229 # NB old limit was 256
        self.climit=MDcleaner.class_climit # Longest text for composer name.
        self.logger.debug(f"Metadatacleaning for files with ?? maybe over-long metadata (title over {self.tlimit} characters):")
        self.longList=[]
        self.bigPicList=[]
               
        self.changeLimit=MDcleaner.class_chlimit
        self.changes=0
        self.inspections=0
        


    def clean(self,filePath):
        pathcs = list(Path(filePath).parts)
        cr=CleaningReport()
        if pathcs[-1] not in self.fnameExclusions and pathcs[-2] not in self.dnameExclusions and pathcs[-1] not in self.dnameExclusions:
            try:
                frames = ID3(filePath)
                metadata = Metadata(frames)
               
                if self.changes < self.changeLimit:
                    if hasattr(metadata,'comment') and "nplayable" in metadata.comment:  # Unplayable or unplayable
                       
                        self.logger.warning(pformat(f"Deleting unplayable {filePath} ({metadata.comment})",width=self.logWidth))
                        os.remove(filePath)
                        self.changes=self.changes+1
                        return("Cleaned - deleted unplayable file") # Brutal, but true
                    
                    # Try to extract/create a meaningful but short title algorithmicly. These are compoinents of the Url (in minimserver)
                    # This matches what happens in the filename mangler.
                    
                    if hasattr(metadata,"album"):
                        if len(metadata.album)>self.alimit:
                            # It's best to keep the album name close to it's full title sort spot for easy recognition
                            metadata.album = metadata.album[0:self.alimit]
                            cr.overlengthAlbum=True
                    else: metadata.album=""
                    if hasattr(metadata,"albumSort") and len(metadata.albumSort)> self.alimit:
                        metadata.albumSort = metadata.albumSort[0:self.alimit]
                        cr.overlengthAlbumSort=True
                    if hasattr(metadata,"composer") and len(metadata.composer)> self.climit:
                        metadata.composer = metadata.composer[0:self.climit]
                        cr.overlengthComposer=True
                    if hasattr(metadata,"title"):
                        for albWord in metadata.album.split(" "):  # Remove selected repetitive information.
                            if albWord in metadata.title and albWord.endswith(":"):
                                metadata.title=metadata.title.replace(albWord+" ","")
                                cr.overlengthTitle=True # Note that the title was changed.
                        if len(metadata.title)>self.tlimit: # Still too long?
                            metadata.title = metadata.title[0:self.tlimit]
                            cr.overlengthTitle=True
                    if hasattr(metadata,"leadArtist") and len(metadata.leadArtist)>self.slimit:
                        metadata.leadArtist = metadata.leadArtist[0:self.slimit]
                        cr.overlengthArtist=True
                    if hasattr(metadata,"albumArtist") and len(metadata.albumArtist)>self.slimit:
                        metadata.albumArtist = metadata.albumArtist[0:self.slimit]
                        cr.overlengthAlbumArtist=True
                    if hasattr(metadata,"composerSort") and len(metadata.composerSort)> self.climit:
                        metadata.composerSort = metadata.composerSort[0:self.climit]
                        cr.overlengthComposerSort=True
                    if hasattr(metadata,"grouping") and len(metadata.grouping)> self.glimit:
                        metadata.grouping = metadata.grouping[0:self.glimit]
                        cr.overlengthGrouping=True
                        
                    newFrames=ID3()
                    
                    # Consider adding the pictures to the new tag.
                    # ... if they're too long (tbd) this can makes files unplayable on Pure radio
                    if (hasattr(metadata,"coverAwLength") and metadata.coverAwLength<self.plimit) \
                        and (not hasattr(metadata,'comment') or (hasattr(metadata,'comment') and "no artwork" not in metadata.comment)):
                        for a in frames.getall("APIC"): newFrames.add(APIC(encoding=a.encoding, mime=a.mime, type=a.type, desc=a.desc, data=a.data))
                    else: # Compress the picture(s)
                        self.logger.info(pformat(f"Cover artwork too large (>{self.plimit}) in {filePath}.",width=self.logWidth))
                        self.bigPicList.append(filePath)
                        cr.overlengthPicture=True
                        for a in frames.getall("APIC"):
                            img = Image.open(BytesIO(a.data))
                            self.logger.info(pformat(f"Image metadata: size={img.size}."))
                            byteIO = BytesIO()
                            # Make sure it's suitable for conversion to jpg (remove the alpha channel if there is one)
                            if img.mode in ("RGBA", "P"): img = img.convert("RGB")
                            
                            width, height = img.size[:2]
                            nwidth, nheight = self.psize, self.psize
                            if height > width:
                                baseheight = self.psize
                                hpercent = (baseheight/float(img.size[1]))
                                wsize = int((float(img.size[0])*float(hpercent)))
                                img = img.resize((wsize, baseheight), Image.Resampling.LANCZOS)
                                nwidth=wsize
                            else:
                                basewidth = self.psize
                                wpercent = (basewidth/float(img.size[0]))
                                hsize = int((float(img.size[1])*float(wpercent)))
                                img = img.resize((basewidth,hsize), Image.Resampling.LANCZOS)
                                nheight=hsize
                            
                            img.save(byteIO, format='JPEG', optimize=True)
                            a.data=byteIO.getvalue()
                            a.mime="image/jpeg"
                            a.desc="compressed by metadataCleaning"
                            newFrames.add(a)
                            self.logger.info(pformat(f"Artwork type {a.type} compressed by jpeg to {len(a.data)} bytes, size(wxh) = {nwidth}x{nheight}. ", width=self.logWidth))
                    
                    # Apply carefully pruned and curated values to new frames
                    if hasattr(metadata,"album"): frames.add(TALB(text=[pureMangle(metadata.album)]))
                    if hasattr(metadata,"albumSort"): frames.add(TSOA(text=[pureMangle(metadata.albumSort)]))
                    if hasattr(metadata,"grouping"):  frames.add(TIT1(text=[pureMangle(metadata.grouping)]))
                    if hasattr(metadata,"title"):  frames.add(TIT2(text=[pureMangle(metadata.title)]))
                    if hasattr(metadata,"leadArtist"): frames.add(TPE1(text=[pureMangle(metadata.leadArtist)]))
                    if hasattr(metadata,"albumArtist"): frames.add(TPE2(text=[pureMangle(metadata.albumArtist)]))
                    if hasattr(metadata,"composer"): frames.add(TCOM(text=[pureMangle(metadata.composer)]))
                    if hasattr(metadata,"composerSort"): frames.add(TSOC(text=[pureMangle(metadata.composerSort)]))
                    elif hasattr(metadata,"composer"):
                        # Does it look like "Firstname Lastname"?  If so - reverse it to Lastname, Firstname
                        if len(metadata.composer.split(" "))==2: frames.add(TSOC(text=[  ", ".join(pureMangle(metadata.composer).split(" ")[::-1])]))
                        # Otherwise use the composer info as-is.
                        else: frames.add(TSOC(text=[pureMangle(metadata.composer)]))
                    if hasattr(metadata,"trackNo"): frames.add(TRCK(text=[metadata.trackNo]))
                    if hasattr(metadata,"diskNo"): frames.add(TPOS(text=[metadata.diskNo]))
                    else: frames.add(TPOS(text=["1/1"]))
                    if hasattr(metadata,"encoder"): frames.add(TENC(text=["py-ffmpeg"]))
                                                            
                    # Copy the minimum necessary old frames to the new tag and the apply the standard text limit for all of them.
                    # This clears extraneous TXXX frames (in case it matters)
                    fidVals={k:frames[k].text[0][0:self.tlimit] for k in \
                        filter(lambda kl: kl in ["TALB","TIT1","TIT2","TPE1","TPE2",
                             "TCOM","TCON",
                             "TRCK", "TPOS",
                             "TENC", "TSSE",
                             "TSOC", "TSOA"
                            ], frames.keys())}
                   
                    for k in fidVals.keys(): newFrames.add(eval(k)(text=[fidVals[k]]))
                    
                    # Special case for timestamps
                    if frames.get("TDRC"): newFrames.add(frames.get("TDRC"))
            
                    frames.delete() # Scrap the whole old thing...
                    newFrames.save(filePath,v2_version=3) # and re-create it
                    results=[k for k in vars(cr).keys() if getattr(cr,k)]
                    if any(results): self.changes=self.changes+1
                    self.logger.info(f"Overlength: {results}" if any(results) else "No Cleaning needed")
                    return(f"Overlength: {results}" if any(results) else "No Cleaning needed")
                else:
                    self.logger.info(f"Cleaning change limit ({self.changeLimit}) reached")
                    return("Limit Reached")
                    
            except Exception as e:
                self.logger.warning(f"File {filePath} could not be cleaned: {e}. The file will be removed if it exists. ")
                self.changes=self.changes+1
                if os.path.isfile(filePath): os.remove(filePath)
                return
                
    def clean2(self,filePath):
        
        return("Cleaned") # For debugging/fix-up use - pretend it worked.  Cleaning can be done separately.

    def report(self,filePath):
    
        rr=CleaningReport()
        pathcs = list(Path(filePath).parts)
        if pathcs[-1] not in self.fnameExclusions and pathcs[-2] not in self.dnameExclusions and pathcs[-1] not in self.dnameExclusions:
            frames = ID3(filePath)
            
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
            for item in ["version","unknown_frames","size"]: headerReport[item] = getattr(frames,item)
            self.logger.info(f"\nID3 Header report for {filePath}:\n{pformat(headerReport, depth=2, indent=0, sort_dicts=True)}\n\n\n")
            self.logger.info(f"\nMP3 info: \n  {pformat(vars(mp3.info))}\n\n\n")
            
            # Report Picture frame header info
            datalessPics = [{"encoding":a.encoding,"mime":a.mime,"type":a.type,"desc":a.desc,"pictureSize":len(a.data) } for a in frames.getall("APIC")]
            self.logger.debug("\nPictures: \n"+json.dumps(datalessPics)+"\n\n\n")
            
            # Use the mp3 header length as a clue to the size of the included picture
            if mp3.info.frame_offset>self.plimit:
                rr.overlengthPicture=True
            else: pass
            
            # Report the frame text lengths
            reportFrameIds =["TALB","TIT1","TIT2","TCOM","TPE1","TPE2"]
            fidReport={k:len(frames[k].text[0]) for k in filter(lambda kl: kl in reportFrameIds, frames.keys())}
            url=urllib.parse.quote(filePath)
            fidTextReport= {k:f"{len(frames[k].text[0]):02} / {MDcleaner.maxes[k]} {('*') if (len(frames[k].text[0]) >  MDcleaner.maxes[k]) else ('') }" for k in filter(lambda kl: kl in reportFrameIds, frames.keys())}

            self.logger.info("\nFrame contents: \n"+frames.pprint())
            self.logger.info("Text lengths: \n"+json.dumps(fidTextReport, indent=4)+ f"\nURL length: {len(url)} / {self.ulimit}  {('*') if (len(url) >  self.ulimit) else ('') }    " + "\n\n")# , sort_keys=True))
            if any(fidReport[k] > MDcleaner.maxes[k] for k in iter(fidReport.keys())):
                rr.overlengthSomething=True # This should report the correct field...
                for k in iter(fidReport.keys()):
                    pass
            else: pass
            
            if pathcs[-2].split(" ")[0] == pathcs[-1].split(" ")[1]: # Track name (omitting track number) begins like album name.
                rr.repetitiveTitle=True

            if len(url)>self.ulimit: self.logger.warning(f"\n{filePath} encodes to a url of length {len(url)} which exceeds the limit of {self.ulimit}. Truncation of titles and/or artist info will be applied.")
            results=[k for k in vars(rr).keys() if getattr(rr,k)]
            return(f"Overlength: {results}" if any(results) else None )

# Match a string in any item in a list of strings
def smatch(string,matchList):
    rlist=[]
    for m in matchList:
        if m in string: rlist.append(m)
    return rlist
            
def main():
    albumNamesTracks={   # Match partial album name (distinct values) and track number prefix
                    #"Sonatas and Partitas":"2-08",
                    #"Tosca":"2-03",
                    "Unforgettable":"", # If blank, do Everything
                    "!":""
                    }
    cleaner=MDcleaner()
    cleaner.logger.setLevel(logging.DEBUG)
    cleaner.logger.info(f"Searching for paths in {cleaner.dir} matching any of {pformat(albumNamesTracks)}.")
    filesCount=sum(1 for x in Path(cleaner.dir).rglob('*') if x.is_file() and smatch(str(x),albumNamesTracks.keys())  )
    
    if len(sys.argv)>1 and sys.argv[1]=="clean":
        function="Clean"
    else: function="Report"
    
    for (r,ds,ls) in os.walk(cleaner.dir,topdown=True):
        #if ds==[]:
        for an in smatch(r,albumNamesTracks.keys()):
            for l in filter(lambda m: m.endswith(".mp3") and m not in cleaner.fnameExclusions, ls):
                filePath = os.path.join(r,l)
                if l.startswith(albumNamesTracks[an]):
                    
                    cleaner.logger.info(pformat(f"Inspecting {filePath} - {cleaner.inspections+1} of {filesCount}. ",
                        width=cleaner.logWidth))
                    rep=cleaner.report(filePath)
                    cleaner.inspections=cleaner.inspections+1
                    
                    if rep: cleaner.longList.append(filePath+" "+pformat(rep))
                    
                    if function=="Clean" and rep:
                        cleaner.logger.info(f"Reported: {rep} - Cleaning.")
                        cleaner.clean(filePath) # Cleans all frames (including dubious TXXX and  frames) and creates a new ID3v2.2 tag
                                                # using simplified original data.
                                                
                        cleaner.logger.info(pformat(f"Cleaned {cleaner.changes} of {min([cleaner.changeLimit])}. ",
                        width=cleaner.logWidth))
                    elif function=="Clean" and not rep: cleaner.logger.info(pformat(f"Nothing reported, no Cleaning needed."))
    
   
    if len(cleaner.longList)==0:
        cleaner.logger.info("No updates")
    else:
        cleaner.logger.info(f"{function}ed {len(cleaner.longList)} files: \n{pformat(cleaner.longList)} ")
    

    
if __name__ == "__main__":
    main()
    exit
