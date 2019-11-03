#! /usr/bin/env python
#  -*- coding: utf-8 -*-
#
# Support module generated by PAGE version 4.26
#  in conjunction with Tcl version 8.6
#    Nov 02, 2019 12:55:42 PM CET  platform: Windows NT

import sys

try:
    import Tkinter as tk
except ImportError:
    import tkinter as tk

try:
    import ttk
    py3 = False
except ImportError:
    import tkinter.ttk as ttk
    py3 = True

def set_Tk_var():
    global huemin
    huemin = tk.DoubleVar()
    global huemax
    huemax = tk.DoubleVar()
    global saturationmax
    saturationmax = tk.DoubleVar()
    global saturationmin
    saturationmin = tk.DoubleVar()
    global valuemax
    valuemax = tk.DoubleVar()
    global valuemin
    valuemin = tk.DoubleVar()

def exit():
    print('first_GUI.exit')
    destroy_window()
    sys.stdout.flush()

def init(top, gui, *args, **kwargs):
    global w, top_level, root
    w = gui
    top_level = top
    root = top

def destroy_window():
    # Function which closes the window.
    global top_level
    top_level.destroy()
    top_level = None

def displayCameraFrame():
    first_GUI.Toplevel1.Camera_frame

if __name__ == '__main__':
    import first_GUI
    first_GUI.vp_start_gui()



