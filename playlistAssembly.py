#!/usr/bin/env python3
"""  main.py

   Exports playlists from the Music app to m3u8 file
 
   and (maybe...)

   Assembles playlist media files into consolidated folders so they can be
   played from a usb Flash drive



"""

from CalendarStore import CalCalendarStore

store = CalCalendarStore.defaultCalendarStore()

for calendar in store.calendars():
    print("")
    print("Name:", calendar._.title)
    print("UUID:", calendar._.uid)
    print("Type:", calendar._.type)




#import AppleScriptKit   # The way to invoke applescript?
import iTunesLibrary



#??? lib=iTunesLibrary.libraryWithAPIVersion()

for itrf in dir(iTunesLibrary): #print(itrf)
 
    if  itrf.find("Playlist")>-1 : print(itrf)
"""        #print(f"{itrf.localizedName()} -> {itrf.localizedName()}")
        print(itrf)
"""
# From
#https://pyobjc.readthedocs.io/en/latest/examples/core/Scripts/HelloWorld/index.html
from Cocoa import NSObject, NSApplication, NSApp

# Seek app root

for att in dir(NSApplication):

    if att.find("ppl")>-1 : print(att)

#How to get the app object???
app = NSApplication.sharedApplication.init()

# Translated by ASTtranslate

playlists= app('Music').user_playlists[(its.special_kind == aem.AEEnum(b'kNon')).NOT].name.get()

# For exporting playlists from Music app, see:
# https://www.macscripter.net/t/apple-music-export-playlist/72126/19



# for running applescript from python see:
# https://stackoverflow.com/questions/2940916/how-do-i-embed-an-applescript-in-a-python-script
# and
# https://www.devasking.com/issue/calling-applescript-from-python-without-using-osascript-or-appscript
