-- In the Music app, export playlists from the "For Export" folder to the Music Library root folder.

set folderName to "For Export"
set musicLibraryRoot to "Media:Shared Music:Music Library:"

set playListNames to {}
tell application "Music"
	
	repeat with aPlaylist in (get every user playlist)
		try
			set p to parent of aPlaylist -- The 'try' catches errors here, but why does it fail?
			if name of p is folderName then
				set end of playListNames to name of aPlaylist
			end if
		end try
	end repeat
	
	-- log playListNames
	
	-- set playListNames to name of every user playlist in folder playlist folderName
	
	repeat with playListName in playListNames -- folder playlist folderName
		
		set outputFile to (musicLibraryRoot & playListName & ".m3u8")
		set aText to "#EXTM3U" & return -- First line of the output file		
		
		set theTracks to every file track in user playlist playListName
		
		repeat with aTrack in theTracks
			set filePlaceholder to POSIX path of (get location of aTrack)
			-- set filePlaceholder to POSIX path of filePlaceholder
			set titlePlaceHolder to (get name of aTrack)
			set durationPlaceHolder to (get duration of aTrack)
			set durationPlaceHolder to round of durationPlaceHolder rounding down
			-- log durationPlaceHolder
			set aText to aText & "#EXTINF:" & durationPlaceHolder & "," & titlePlaceHolder & return & filePlaceholder & return
			-- log aText
		end repeat
		
		
		try -- write text to text file
			set fileReference to open for access outputFile with write permission
			set eof of fileReference to 0
			write aText to fileReference as Çclass utf8È -- EDITED
			close access fileReference
		on error
			try
				close access file outputFile
			end try
		end try
	end repeat
end tell