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
import threading
import PIL
import numpy as np
from PIL import ImageTk, Image
from facade import Facade
import json


camerapageopen = False
imagepageopen = False
secondimagepageopen = False


class MainWindow(threading.Thread):

    def __init__(self, facade):
        threading.Thread.__init__(self)
        self.facade = facade

        self._hsvpreset = {}
        self._hsvpresets = [
            "Color1",
            "Color2",
            "Color3",
        ]

    def run(self):

        self.root = Tk()
        self.root.geometry("800x400")
        self.root.title("3D print error detection")
        self.label1 = Label(self.root, text="Error detection", fg='black')
        self.root.protocol('WM_DELETE_WINDOW', self.quit)
        # Buttons
        self._hsvcolor = tk.StringVar(self.root)


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
        self.presetmenu = OptionMenu(self.root, self._hsvcolor, self._hsvpresets[0], self._hsvpresets[1],
                                     self._hsvpresets[2])
        self.prntbtn = Button(self.root, text="Print", command=self.facade.printregister)
        self.startlastimgpagebtn = Button(self.root, text="Start Last Image", relief="raised",
                                          command=self.openimagepage)
        self.startsecondlastimgpagebtn = Button(self.root, text="Start Second to Last Image", relief="raised",
                                                command=self.opensecondimagepage)
        self.binarybtn = Button(self.root, text="Binary Mask", relief="raised", fg='black', command=self.invertmask)

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
        self.prntbtn.grid(row=12, column=4)
        self.startlastimgpagebtn.grid(row=8, column=5)
        self.startsecondlastimgpagebtn.grid(row=8, column=6)
        self.binarybtn.grid(row=9, column=5)

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
        #self.updater()
        #self.root.after(30, self.updater)
        self.root.mainloop()

    def updater(self):
        self.facade.gettriggerpress()
        self.sethsvvalues()
        #self.root.after(30, self.updater())

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
            'Hue max': str(self._hue_max.get()),
            'Hue min': str(self._hue_min.get()),
            'Sat max': str(self._sat_max.get()),
            'Sat min': str(self._sat_min.get()),
            'Val max': str(self._val_max.get()),
            'Val min': str(self._val_min.get())})

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

    def opencamerapage(self):
        global camerapageopen
        if self.startcamerabtn.config('relief')[-1] == 'sunken':
            self.startcamerabtn.config(relief="raised", text="Start Camera")
        else:
            self.startcamerabtn.config(relief="sunken", text="Stop Camera")

        if not camerapageopen:
            self.camerapage = Camerapage(facade=self.facade, parent=self)
            camerapageopen = True
        else:
            self.stopcamerapage()

    def openimagepage(self):
        global imagepageopen
        if self.startlastimgpagebtn.config('relief')[-1] == 'sunken':
            self.startlastimgpagebtn.config(relief="raised", text="Start Image display")
        else:
            self.startlastimgpagebtn.config(relief="sunken", text="Stop Image display")

        if not imagepageopen:
            if not self.facade.isregempty():
                self.imagepageopen = Imagepage(facade=self.facade, reversedindex=-1)
                imagepageopen = True
            else:
                print("Image register is empty!!")
        else:
            self.stopimagepage()

    def opensecondimagepage(self):
        global secondimagepageopen
        if self.startlastimgpagebtn.config('relief')[-1] == 'sunken':
            self.startlastimgpagebtn.config(relief="raised", text="Start Image display")
        else:
            self.startlastimgpagebtn.config(relief="sunken", text="Stop Image display")

        if not secondimagepageopen:
            if not self.facade.isregempty():
                self.imagepageopen = Imagepage(facade=self.facade, reversedindex=-2)
                secondimagepageopen = True
            else:
                print("Image register is empty!!")
        else:
            self.stopimagepage()

    def stopcamerapage(self):
        self.camerapage.destructor()

    def stopimagepage(self):
        self.imagepageopen.destructor()

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
            if self.addmaskbtn.config('relief')[-1] == 'sunken':
                self.addmaskbtn.config(relief="raised", text="Add Mask")
                print("[INFO] Removing mask")
                self.facade.setapplymask(flag=False)
            else:
                self.addmaskbtn.config(relief="sunken", text="Remove Mask")
                self.facade.setapplymask(flag=True)
                print("[INFO] Adding mask")
        else:
            print("[INFO] Camera page is not open...")

    def invertmask(self):
        if self.facade.getapplymask():
            if self.invertmaskbtn.config('relief')[-1] == 'sunken':
                self.invertmaskbtn.config(relief="raised", text="Invert Mask")
                print("[INFO] Reverting mask")
                self.facade.setinvertedmask(flag=False)
            else:
                self.invertmaskbtn.config(relief="sunken", text="Revert Mask")
                self.facade.setinvertedmask(flag=True)
                print("[INFO] Inverting mask")
        else:
            print("Mask not applied...")


class Camerapage():  # threading.Thread):
    def __init__(self, facade, parent):
        # threading.Thread.__init__(self)
        self.root = Toplevel()
        self.facade = facade
        self.parent = parent
        self.root.title("Camera")
        self.root.lift()
        self.root.focus_force()
        self.root.grab_set()
        self.root.grab_release()
        self.panel = tk.Label(self.root)  # initialize image panel
        self.panel.pack(padx=10, pady=10)

        self.root.protocol('WM_DELETE_WINDOW', self.destructor)
        self.current_image = None
        print("[INFO] starting camera...")

        self.run()

    def run(self):
        self.parent.updater()
        if self.facade.getapplymask():
            if self.facade.getbinarymask():
                self.current_image = self.facade.getbinaryvideo()
            else:
                if self.facade.getinvertedmask():
                    self.current_image = self.facade.getmaskedvideo(inverted=True)
                elif not self.facade.getinvertedmask():
                    self.current_image = self.facade.getmaskedvideo(inverted=False)

            imgtk = ImageTk.PhotoImage(image=self.current_image)
            self.panel.imgtk = imgtk
            self.panel.config(image=imgtk)
        else:
            self.current_image = self.facade.getcleanvideo()
            imgtk = ImageTk.PhotoImage(image=self.current_image)
            self.panel.imgtk = imgtk
            self.panel.config(image=imgtk)

        self.root.after(30, self.run)

    def destructor(self):
        """ Destroy the root object and release all resources """
        print("[INFO] closing camera...")
        self.root.destroy()
        global camerapageopen
        camerapageopen = False


class Imagepage():  # threading.Thread):
    def __init__(self, facade, reversedindex):
        # threading.Thread.__init__(self)
        self.root = Toplevel()
        self.facade = facade
        self.reversedindex = reversedindex
        if reversedindex == -1:
            self.root.title("Last Image Captured")
        elif reversedindex == -2:
            self.root.title("Second to Last Image Captured")
        else:
            self.root.title("Un indexed Image")

        self.panel = tk.Label(self.root)  # initialize image panel
        self.panel.pack(padx=10, pady=10)

        self.root.protocol('WM_DELETE_WINDOW', self.destructor)
        self.current_image = None

        self.run()
        # self.daemon = True
        # self.start()

    def run(self):

        self.current_image = self.facade.getlastimage(index=self.reversedindex)
        imgtk = ImageTk.PhotoImage(image=PIL.Image.fromarray(self.current_image))
        self.panel.imgtk = imgtk
        self.panel.config(image=imgtk)

        self.root.after(1000, self.run)

    def destructor(self):
        """ Destroy the root object and release all resources """
        print("[INFO] closing image...")
        self.root.destroy()
        global imagepageopen
        imagepageopen = False
