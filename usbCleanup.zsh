#!/bin/zsh

# ._ files (which are numerous) are not useful to a media player but are visible in the UI during media selection. 
# This script cleans the Music folders of these files.

# This script may run as root when called as a postflight script by Carbon Copy Cloner

cd /Users/timbanks/MyWork/Refresh\ Music\ Server


# This dot_clean command gets rid of the extraneous files.
dot_clean /Volumes/Portable/MusicMP3 

exit
