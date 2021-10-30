# Copy-Downloaded
Python script for automating copying of downloaded files to another folder
Created to automate copying of .uf2 downloads from https://makecode.adafruit.com to the Arduino device mounted as a USB drive

# Operation:
- waits for new .uf2 file in [scan_folder]
	- e.g. ~/Downloads
- copies new .uf2 file to [device_folder]
	- e.g. /Volumes/CPLAYBOOT

# Options
Overrides for default values of:
- file extension to scan for
- scan_folder
- device_folder
- console or GUI mode

# Python Dependencies:
- tkinter: gui library
- watchdog: watches folder for new files

