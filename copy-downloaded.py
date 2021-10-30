#!/usr/bin/env python3

# Python script for automating copying of downloaded files to another folder
# Created to automate copying of .uf2 downloads from https://makecode.adafruit.com to the Arduino device mounted as a USB drive
#
# Operation:
# - waits for new .uf2 file in [scan_folder]
# - copies new .uf2 file to device_folder
#
# Dependencies:
# - tkinter: gui
# - watchdog: watches folder for new files

import argparse
import datetime
import os
import shutil
import time
import tkinter as tk        # needs tk enabled version of python
import watchdog.events      # python3 -m pip install watchdog
import watchdog.observers


class MyEventHandler(watchdog.events.PatternMatchingEventHandler):  # {
    """
        Behaviour
        - during local copy to incoming folder
          - get on_created() + on_modified()
        - during download to incoming folder
          - get multiple on_created() & on_modified()
          - observe 4 or 5 of each
    """ 
    def __init__(self, patterns=None, ignore_patterns=None, ignore_directories=False, case_sensitive=False):
        super().__init__(patterns, ignore_patterns, ignore_directories, case_sensitive)
        self.reset()

    def reset(self):
        self.has_new = False
        self.last_timestamp = None
        self.new_fname = None

    def on_created(self, event):
        #print(f"{event.src_path} was created!")
        self.has_new = True
        self.last_timestamp = datetime.datetime.now()
        self.new_fname = event.src_path

    def on_modified(self, event):
        #print(f"{event.src_path} was modified!")
        self.has_new = True
        self.last_timestamp = datetime.datetime.now()
        self.new_fname = event.src_path

    def on_closed(self, event):
        """ Not seeing this event at all
        """
        print(f"{event.src_path} was closed!")

# this didn't provide any additional functionality/benefit
#   def on_any_event(self, event):
#       print(f"Any event: {event.event_type}")

    def get_new_file(self):
        """ returns name of latest new or modified file
            returns None if no new or modified file (or if new file not complete yet)
        """
        STABLE_THRESH = 1.0     # seconds after last activity till declare file update is done
        if self.has_new:
            delta_time = datetime.datetime.now() - self.last_timestamp
            if delta_time.total_seconds() > STABLE_THRESH:
                ret_val = self.new_fname
                self.reset()
                return ret_val
        return None
# }


def tk_test():  # {
    """ play with tk
    """
    window = tk.Tk()
    window.title("Copy Download")
    font = ("Arial", 30)
    height = 10
    width = 30
    label_scanning = tk.Label(text="Scanning For New File", bg="green")
    label_new_file = tk.Label(text="New File: Reset Device", bg="red")
    label_scanning.config(font=font, height=height, width=width)
    label_new_file.config(font=font, height=height, width=width)

    # tkinter testing
    INTERVAL = 3
    count = 0
    scanning = True
    label_scanning.pack()
    try:  # {
        while True:  # {
            count += 1
            if count == INTERVAL:
                if scanning:
                    cur = label_scanning
                    new = label_new_file
                else:
                    cur = label_new_file
                    new = label_scanning
                scanning = not scanning
                cur.pack_forget()
                new.pack()
                count = 0
            window.update()
            time.sleep(1)
        # }
    # }
    except tk.TclError:
        # user closed tk window
        pass
# }


def loop_gui(device_folder, my_event_handler):  # {
    """ using tkinter
        - close the tk-window to exit
    """
    window = tk.Tk()
    window.title("Copy Download")
    font = ("Arial", 30)
    height = 10
    width = 30
    label_scanning = tk.Label(text="Scanning For New File", bg="green")
    label_new_file = tk.Label(text="New File: Reset Device", bg="red")
    label_scanning.config(font=font, height=height, width=width)
    label_new_file.config(font=font, height=height, width=width)

    label_scanning.pack()
    try:
        while True:
            new_fname = my_event_handler.get_new_file()
            if new_fname:
                #print("Detected new file: %s" % new_fname)
                label_scanning.pack_forget()
                label_new_file.pack()
                while True:
                    if os.path.isdir(device_folder):
                        # device_folder found/mounted
                        break
                    window.update()
                    time.sleep(.1)
                # copy new file to device
                time.sleep(.5)  # need bit of delay here for mounted drive to "settle"
                shutil.copy(new_fname, os.path.join(device_folder, os.path.split(new_fname)[1]))
                label_new_file.pack_forget()
                label_scanning.pack()
            window.update()
            time.sleep(.1)
    except tk.TclError:
        pass
# }


def loop_console(device_folder, my_event_handler):  # {
    """ using console
        - CTRL-C to exit
    """
    ready_msg = "Waiting for new downloaded file"
    print(ready_msg)
    try:
        while True:
            new_fname = my_event_handler.get_new_file()
            if new_fname:
                print("Detected new file: %s" % new_fname)
                print("Reset device to mount as USB drive")
                while True:
                    if os.path.isdir(device_folder):
                        # device_folder found/mounted
                        break
                    time.sleep(.1)
                # copy new file to device
                time.sleep(.5)  # need bit of delay here for mounted drive to "settle"
                shutil.copy(new_fname, os.path.join(device_folder, os.path.split(new_fname)[1]))
                print("wrote file to:", os.path.join(device_folder, os.path.split(new_fname)[1]))
                print(ready_msg)
            time.sleep(.1)
    except KeyboardInterrupt:
        # detected CTRL-C
        pass
# }
    

def main(args):
    patterns = [args.ext]
    ignore_patterns = None
    ignore_directories = False
    case_sensitive = False
    my_event_handler = MyEventHandler(patterns, ignore_patterns, ignore_directories, case_sensitive)

    my_observer = watchdog.observers.Observer()
    my_observer.schedule(my_event_handler, args.scan_folder, recursive=False)
    my_observer.start()

    if args.console:
        loop_console(args.device_folder, my_event_handler)
    else:
        loop_gui(args.device_folder, my_event_handler)

    my_observer.stop()
    my_observer.join()


# defaults
# TODO: detect platform and set reasonable defaults per-platform
SCAN_EXT = '*.uf2'
SCAN_FOLDER = '/Users/albert/Downloads'
DEVICE_FOLDER = '/Volumes/CPLAYBOOT'

if __name__ == '__main__':  # {
    #tk_test()
    #stop

    # parse cmd-line args
    parser = argparse.ArgumentParser()

    # Positional args:
#   parser.add_argument("url",
#           help='youtube url, e.g. https://www.youtube.com/watch?v=Iy8NYRJWDNQ')
#   parser.add_argument("playlists",
#           nargs='+',  # arbitrary number of playlist files
#           help="test specification file(s)")

    # Optional args:
    parser.add_argument("-c", "--console", action='store_true',
            help="Run in console-mode (default is GUI-mode)")

    parser.add_argument("-s", "--scan_folder",
            default=SCAN_FOLDER,
            help='Folder to scan for new files (default = "%s")'%SCAN_FOLDER)
    parser.add_argument("-d", "--device_folder",
            default=DEVICE_FOLDER,
            help='Device folder to copy file to (default = "%s")'%DEVICE_FOLDER)
    parser.add_argument("-e", "--ext",
            default=SCAN_EXT,
            help='File extension to scan for (default = "%s")'%SCAN_EXT)

    args = parser.parse_args()
    main(args)
# }

