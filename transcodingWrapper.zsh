#!/bin/zsh
# This script may run as root when called as a preflight script by Carbon Copy Cloner

cd /Users/timbanks/MyWork/Refresh\ Music\ Server

echo $PATH

export PATH=/Library/Frameworks/Python.framework/Versions/3.13/bin:/usr/local/bin:/usr/local/sbin:/System/Cryptexes/App/usr/bin:/usr/bin:/bin:/usr/sbin:/sbin:/var/run/com.apple.security.cryptexd/codex.system/bootstrap/usr/local/bin:/var/run/com.apple.security.cryptexd/codex.system/bootstrap/usr/bin:/var/run/com.apple.security.cryptexd/codex.system/bootstrap/usr/appleinternal/bin:/Library/Apple/usr/bin

# see https://unix.stackexchange.com/questions/688048/modulenotfounderror-when-running-bash-shell-script-but-works-fine-when-running

/Library/Frameworks/Python.framework/Versions/3.13/bin/python3  transcoding.py  >transcoding.log 2>&1


exit $?
