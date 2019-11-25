"""
GUI applikasjon for deteksjon av feil i 3d-printing.
Den skal ha eit konfigurerings vindu, der bruker kan gi input til hsv terskling og cropping,
samt lagringssted for timelapsen/bilda.
Den skal ha eit preview vindu av camera feeden.
Den skal ha eit vindu for å loope timelapsen.
Den skal ha ei status linje, som skal varsle om feil blir oppdaga. Denne skal vere synlig i alle vindu.
Den skal ha knappar for å skifte vindu.
"""
import tkinter as tk
from tkinter import ttk, filedialog
from tkinter import *
import numpy as np
from PIL import ImageTk, Image
from facade import Facade
import json

camerapageopen = False
applymask = False
invertedmask = False


# TODO: Sjekk om ej trenge å arve threding
class MainApplication():

    def __init__(self):
        self.facade = Facade()
        self.root = Tk()
        self.mainwindow = MainWindow(self.root, facade=self.facade)

    def run(self):
        self.mainwindow.run()

    def getfacade(self):
        return self.facade()

    def getcamera(self):
        return self.facade.getcameraframe()

    def getprocessor(self):
        return self.facade.getprocessor()


class MainWindow:

    def __init__(self, root, facade):
        self.facade = facade
        self.root = root
        self.root.geometry("800x400")
        self.root.title("3D print error detection")
        self.label1 = Label(self.root, text="Error detection", fg='black')
        self._hsvpreset = {}
        self._hsvpresets = [
            "Color1",
            "Color2",
            "Color3",
        ]

        self._hsvcolor = tk.StringVar(self.root)

    def run(self):
        # Buttons
        self.startcamerabtn = Button(self.root, text="Start camera", width=14,
                                     relief="raised", fg='black', command=self.opencamerapage)
        self.quitbtn = Button(self.root, text="Quit", fg='black', command=self.quit)
        self.starttimelapsebtn = Button(self.root, text="Start timelapse", fg='black', command=self.starttimelapse)
        self.stoptimelapsebtn = Button(self.root, text="Stop timelapse", fg='black', command=self.stoptimelapse)
        self.addmaskbtn = Button(self.root, text="Add Mask", width=14, relief="raised", fg='black',
                                 command=self.addmask)
        self.invertmaskbtn = Button(self.root, text="Invert Mask", width=14, relief="raised", fg='black',
                                 command=self.invertmask)
        self.hsvresetbtn = Button(self.root, text="Reset HSV", fg='black', command=self.hsvreset)
        self.hsvpresetbtn = Button(self.root, text="Save HSV Preset", fg='black', command=self.savehsvpreset)
        self.usehsvpresetbtn = Button(self.root, text="Use HSV Preset", fg='black', command=self.usehsvpreset)
        self.presetmenu = OptionMenu(self.root, self._hsvcolor, self._hsvpresets[0], self._hsvpresets[1], self._hsvpresets[2])

        self._hsvcolor.set(self._hsvpresets[0])
        self._hsvcolor.trace("w", self.setpreset)

        # Placing elements
        self.label1.grid(row=0, column=2)
        self.startcamerabtn.grid(row=6, column=2)
        self.quitbtn.grid(row=6, column=6)
        self.starttimelapsebtn.grid(row=6, column=4)
        self.stoptimelapsebtn.grid(row=6, column=5)
        self.addmaskbtn.grid(row=7, column=4)
        self.invertmaskbtn.grid(row=7, column=5)
        self.hsvresetbtn.grid(row=8, column=4)
        self.hsvpresetbtn.grid(row=9, column=4)
        self.usehsvpresetbtn.grid(row=10, column=4)
        self.presetmenu.grid(row=11, column=4)

        self.folderPath = StringVar()

        # HSV variables
        self._hue_max = tk.IntVar()
        self._hue_max.set(179)
        self._hue_min = tk.IntVar()
        self._hue_min.set(0)
        self._sat_max = tk.IntVar()
        self._sat_max.set(255)
        self._sat_min = tk.IntVar()
        self._sat_min.set(0)
        self._val_max = tk.IntVar()
        self._val_max.set(255)
        self._val_min = tk.IntVar()
        self._val_min.set(0)

        # Hue, Saturation, Value
        self.hue_max_label = Label(self.root, text="Hue max", fg='black')
        self.hue_max_scale = Scale(self.root, from_=0, to=179, length=200, orient=HORIZONTAL, variable=self._hue_max)
        self.hue_min_label = Label(self.root, text="Hue min", fg='black')
        self.hue_min_scale = Scale(self.root, from_=0, to=179, length=200, orient=HORIZONTAL, variable=self._hue_min)
        self.sat_max_label = Label(self.root, text="Saturation max", fg='black')
        self.sat_max_scale = Scale(self.root, from_=0, to=255, length=200, orient=HORIZONTAL, variable=self._sat_max)
        self.sat_min_label = Label(self.root, text="Saturation min", fg='black')
        self.sat_min_scale = Scale(self.root, from_=0, to=255, length=200, orient=HORIZONTAL, variable=self._sat_min)
        self.val_max_label = Label(self.root, text="Value max", fg='black')
        self.val_max_scale = Scale(self.root, from_=0, to=255, length=200, orient=HORIZONTAL, variable=self._val_max)
        self.val_min_label = Label(self.root, text="Value min", fg='black')
        self.val_min_scale = Scale(self.root, from_=0, to=255, length=200, orient=HORIZONTAL, variable=self._val_min)

        self.hue_max_label.grid(row=7, column=2)
        self.hue_max_scale.grid(row=7, column=3)
        self.hue_min_label.grid(row=8, column=2)
        self.hue_min_scale.grid(row=8, column=3)
        # Saturation
        self.sat_max_label.grid(row=9, column=2)
        self.sat_max_scale.grid(row=9, column=3)
        self.sat_min_label.grid(row=10, column=2)
        self.sat_min_scale.grid(row=10, column=3)
        # Value
        self.val_max_label.grid(row=11, column=2)
        self.val_max_scale.grid(row=11, column=3)
        self.val_min_label.grid(row=12, column=2)
        self.val_min_scale.grid(row=12, column=3)

        # Start it all
        self.updater()
        self.root.mainloop()

    def setpreset(self, *args):
        self.usehsvpreset()

    def hsvreset(self):
        self._hue_max.set(179)
        self._hue_min.set(0)
        self._sat_max.set(255)
        self._sat_min.set(0)
        self._val_max.set(255)
        self._val_min.set(0)

    # https://www.youtube.com/watch?v=rz1NFzMSJGY
    def savehsvpreset(self):
        self._hsvpreset[str(self._hsvcolor.get())] = []
        self._hsvpreset[str(self._hsvcolor.get())].append({
        'Hue max':  str(self._hue_max.get()),
        'Hue min':  str(self._hue_min.get()),
        'Sat max':  str(self._sat_max.get()),
        'Sat min':  str(self._sat_min.get()),
        'Val max':  str(self._val_max.get()),
        'Val min':  str(self._val_min.get())})


        # self._hsvpreset['Hue max'] = str(self._hue_max.get())
        # self._hsvpreset['Hue min'] = str(self._hue_min.get())
        # self._hsvpreset['Sat max'] = str(self._sat_max.get())
        # self._hsvpreset['Sat min'] = str(self._sat_min.get())
        # self._hsvpreset['Val max'] = str(self._val_max.get())
        # self._hsvpreset['Val min'] = str(self._val_min.get())
        with open('hsv_presets.json', 'w') as f:
            json.dump(self._hsvpreset, f)

    def usehsvpreset(self):
        f = open('hsv_presets.json')
        self._hsvpreset = json.load(f)
        for c in self._hsvpreset[str(self._hsvcolor.get())]:
            self._hue_max.set(c['Hue max'])
            self._hue_min.set(c['Hue min'])
            self._sat_max.set(c['Sat max'])
            self._sat_min.set(c['Sat min'])
            self._val_max.set(c['Val max'])
            self._val_min.set(c['Val min'])

    def sethsvvalues(self):
        self.hsv_low = np.array([self._hue_min.get(), self._sat_min.get(), self._val_min.get()])
        self.hsv_high = np.array([self._hue_max.get(), self._sat_max.get(), self._val_max.get()])
        self.facade.sethsvlow(value=self.hsv_low)
        self.facade.sethsvhigh(value=self.hsv_high)

    def updater(self):
        #self.facade.gettriggerpress()
        self.sethsvvalues()
        self.root.after(1, self.updater)

    def opencamerapage(self):
        global camerapageopen
        if self.startcamerabtn.config('relief')[-1] == 'sunken':
            self.startcamerabtn.config(relief="raised", text="Start Camera")
        else:
            self.startcamerabtn.config(relief="sunken", text="Stop Camera")

        if not camerapageopen:
            self.camerapage = Camerapage(facade=self.facade)
            camerapageopen = True
        else:
            self.stopcamerapage()

    def stopcamerapage(self):
        self.camerapage.destructor()

    def getcamerapage(self):
        return self.camerapage

    def quit(self):
        self.root.destroy()

    def starttimelapse(self):
        folder_selected = filedialog.askdirectory()
        self.folderPath.set(folder_selected)
        pass

    def stoptimelapse(self):
        pass

    def addmask(self):
        if camerapageopen:
            global applymask
            if self.addmaskbtn.config('relief')[-1] == 'sunken':
                self.addmaskbtn.config(relief="raised", text="Add Mask")
                print("[INFO] Removing mask")
                applymask = False
            else:
                self.addmaskbtn.config(relief="sunken", text="Remove Mask")
                applymask = True
                print("[INFO] Adding mask")
        else:
            print("[INFO] Camera page is not open...")

    def invertmask(self):
        global invertedmask
        if self.invertmaskbtn.config('relief')[-1] == 'sunken':
            self.invertmaskbtn.config(relief="raised", text="Invert Mask")
            print("[INFO] Inverting mask")
            invertedmask = False
        else:
            self.invertmaskbtn.config(relief="sunken", text="Revert Mask")
            invertedmask = True
            print("[INFO] Reverting mask")


class Camerapage:
    def __init__(self, facade):
        self.root = Toplevel()
        self.facade = facade
        self.facade.startcamera()
        self.root.title("Camera")

        self.panel = tk.Label(self.root)  # initialize image panel
        self.panel.pack(padx=10, pady=10)

        self.root.protocol('WM_DELETE_WINDOW', self.destructor)
        self.current_image = None
        print("[INFO] starting camera...")
        self.video_loop()

    def video_loop(self):
        global applymask
        global invertedmask
        if self.facade.getcleanvideo():
            if applymask:
                if invertedmask:
                    self.current_image = self.facade.getmaskedvideo(inverted=True)
                else:
                    self.current_image = self.facade.getmaskedvideo(inverted=False)
                imgtk = ImageTk.PhotoImage(image=self.current_image)
                self.panel.imgtk = imgtk
                self.panel.config(image=imgtk)
            else:
                self.current_image = self.facade.getcleanvideo()
                imgtk = ImageTk.PhotoImage(image=self.current_image)
                self.panel.imgtk = imgtk
                self.panel.config(image=imgtk)

        self.root.after(10, self.video_loop)

    def destructor(self):
        """ Destroy the root object and release all resources """
        print("[INFO] closing camera...")
        self.root.destroy()
        global camerapageopen
        camerapageopen = False

