#!/bin/zsh
# This script may run as root when called as a postflight script by Carbon Copy Cloner

cd /Users/timbanks/MyWork/Refresh\ Music\ Server


export PATH=/Library/Frameworks/Python.framework/Versions/3.13/bin:/usr/local/bin:/usr/local/sbin:/System/Cryptexes/App/usr/bin:/usr/bin:/bin:/usr/sbin:/sbin:/var/run/com.apple.security.cryptexd/codex.system/bootstrap/usr/local/bin:/var/run/com.apple.security.cryptexd/codex.system/bootstrap/usr/bin:/var/run/com.apple.security.cryptexd/codex.system/bootstrap/usr/appleinternal/bin:/Library/Apple/usr/bin

# see https://unix.stackexchange.com/questions/688048/modulenotfounderror-when-running-bash-shell-script-but-works-fine-when-running

# Make a timestamp and identifier for the log
date="["`date "+%Y %b %d %X"`"]"
source=" {minimRescanWrapper.zsh} " 
echo $date$source >> transcoding.log 2>&1

# Rescan the server library.  Annoyingly... minim will not execute commands as root.
sudo -u timbanks /Applications/MinimServer.app/Contents/mscript -a 192.168.0.16:9790 -c rescan
exit $?
