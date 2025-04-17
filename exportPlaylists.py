#!/usr/bin/env python3
from AppKit import NSWorkspace
for nsapp in NSWorkspace.sharedWorkspace().runningApplications(): 
	if "Music" == nsapp.localizedName() : print(f"{nsapp.localizedName()} -> {nsapp.bundleIdentifier()}")
