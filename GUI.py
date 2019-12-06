"""
This GUI package is the frontend of the 3D printer error detection application.
"""
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from tkinter import *
import ttkthemes
import threading
import PIL
import numpy as np
from PIL import ImageTk, Image
from facade import Facade
import json


class MainWindow(threading.Thread):
    """
    A class representing the Main window of the application.
    """

    def __init__(self, facade):
        """
        :param facade: Facade instance that connects backend functionality
        """
        threading.Thread.__init__(self)
        self.facade = facade

        self._hsvpreset = {}
        self._hsvpresets = [
            "Color1",
            "Color2",
            "Color3",
        ]
        # GUI handling flags
        self._camerapage = None
        self._imagepage = None
        self._secondimagepage = None
        self._camerapageopen = False
        self._imagepageopen = False
        self._secondimagepageopen = False
        self._savemaskedon = False

    def run(self):
        """
        Starts the application
        """
        # Setup window
        self.root = Tk()
        self.root.iconbitmap(self, default="clienticon.ico")
        self.root.style = ttkthemes.ThemedStyle()
        self.root.style.theme_use('black')
        # self.root.geometry("800x400")
        self.root.title("3D print error detection")
        self.label1 = Label(self.root, text="3D print Error Detection Application", font=2)
        self.root.protocol('WM_DELETE_WINDOW', self.quit)

        self._folderPath = StringVar()

        # HSV Presets
        self._hsvcolor = tk.StringVar(self.root)
        self._hsvcolor.set(self._hsvpresets[0])
        self._hsvcolor.trace("w", self.setpreset)

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
        # Frames
        self.cameracontrolframe = Frame(self.root)
        self.cameracontrolframe.grid(row=1, column=1, columnspan=4)
        self.hsvframe = Frame(self.root)
        self.hsvframe.grid(row=3, column=1, rowspan=8, columnspan=3)
        self.maskbtnframe = Frame(self.hsvframe)
        self.maskbtnframe.grid(row=7, column=2, rowspan=2)
        self.hsvpresetframe = Frame(self.root)
        self.hsvpresetframe.grid(row=4, column=4, rowspan=4, sticky="W")
        self.morphframe = Frame(self.root)
        self.morphframe.grid(row=8, column=4, rowspan=4, sticky="W")

        self.hsvlabel = Label(self.hsvframe, text="HSV thresholding", font=2)
        self.hsvlabel.grid(row=0, column=0, columnspan=3, pady=5, sticky="S")
        # Buttons
        self.startcamerabtn = Button(self.cameracontrolframe, text="Start camera", width=14,
                                     relief="raised", fg='black', command=self.opencamerapage)
        self.savemaskedbtn = Button(self.cameracontrolframe, text="Save Masked Images", width=18,
                                    relief="raised", fg='black', command=self.savemasked)
        self.startlastimgpagebtn = Button(self.cameracontrolframe, text="Latest Image", width=14,
                                          relief="raised", command=self.openimagepage)
        self.startsecondlastimgpagebtn = Button(self.cameracontrolframe, text="Second to Last Image", width=18,
                                                relief="raised", command=self.opensecondimagepage)
        self.quitbtn = Button(self.cameracontrolframe, text="Quit", width=10, fg='black', command=self.quit)

        self.starttimelapsebtn = Button(self.root, text="Start timelapse", fg='black', command=self.starttimelapse)
        self.stoptimelapsebtn = Button(self.root, text="Stop timelapse", fg='black', command=self.stoptimelapse)
        self.addmaskbtn = Button(self.maskbtnframe, text="Add Mask", width=14, relief="raised", fg='black',
                                 command=self.addmask)
        self.invertmaskbtn = Button(self.maskbtnframe, text="Invert Mask", width=14, relief="raised", fg='black',
                                    command=self.invertmask)
        self.hsvresetbtn = Button(self.hsvpresetframe, text="Reset HSV", fg='black', width=12, command=self.hsvreset)
        self.hsvpresetbtn = Button(self.hsvpresetframe, text="Save HSV Preset", fg='black', width=12,
                                   command=self.savehsvpreset)
        self.usehsvpresetbtn = Button(self.hsvpresetframe, text="Use HSV Preset", fg='black', width=12,
                                      command=self.usehsvpreset)
        self.presetmenu = OptionMenu(self.hsvpresetframe, self._hsvcolor, self._hsvpresets[0], self._hsvpresets[1],
                                     self._hsvpresets[2])
        self.presetmenu.config(width=9)
        self.prntbtn = Button(self.root, text="Print", command=self.facade.printregister)

        self.chechsimilaritybtn = Button(self.root, text="Similarity", fg='black', command=self.chechsimilarity)

        self.erodebtn = Button(self.morphframe, text="Erode",width=12, relief="raised", command=self.erode)
        self.dilateebtn = Button(self.morphframe, text="Dilate", width=12, relief="raised", command=self.dilate)
        self.openbtn = Button(self.morphframe, text="Open", width=12, relief="raised", command=self.open)
        self.closebtn = Button(self.morphframe, text="Close", width=12, relief="raised", command=self.close)

        self.threshenter = Button(self.root, text="Enter", command=self.enterthresh)
        self.threshentry = Entry(self.root)
        self.threshlabel = Label(self.root, text="Set thresh: ", fg='black')

        self.aboutbtn = Button(self.root, text="About", command=self.showaboutinfo)

        # Placing elements
        self.label1.grid(row=0, column=1, columnspan=5, pady=10)

        self.startcamerabtn.grid(row=0, column=0)
        self.savemaskedbtn.grid(row=0, column=1)
        self.startlastimgpagebtn.grid(row=0, column=2)
        self.startsecondlastimgpagebtn.grid(row=0, column=3)
        self.quitbtn.grid(row=0, column=4)

        # self.starttimelapsebtn.grid(row=6, column=4)
        # self.stoptimelapsebtn.grid(row=6, column=5)

        self.hsvresetbtn.grid(row=4, column=1)
        self.hsvpresetbtn.grid(row=3, column=1)
        self.usehsvpresetbtn.grid(row=1, column=1)
        self.presetmenu.grid(row=2, column=1)

        self.prntbtn.grid(row=14, column=3, sticky="E")
        self.chechsimilaritybtn.grid(row=14, column=4, sticky="W")

        self.addmaskbtn.grid(row=1, column=1, rowspan=2, sticky="E")
        self.invertmaskbtn.grid(row=1, column=2, rowspan=2, sticky="W")

        self.erodebtn.grid(row=11, column=5)
        self.dilateebtn.grid(row=12, column=5)
        self.openbtn.grid(row=13, column=5)
        self.closebtn.grid(row=14, column=5)
        self.threshlabel.grid(row=13, column=2)
        self.threshentry.grid(row=14, column=2)
        self.threshenter.grid(row=15, column=2)

        self.aboutbtn.grid(row=0, column=4, sticky="E")

        # Hue, Saturation, Value
        self.hue_max_label = Label(self.hsvframe, text="Hue max")
        self.hue_max_scale = Scale(self.hsvframe, from_=0, to=179, length=200, orient=HORIZONTAL,
                                   variable=self._hue_max)
        self.hue_min_label = Label(self.hsvframe, text="Hue min")
        self.hue_min_scale = Scale(self.hsvframe, from_=0, to=179, length=200, orient=HORIZONTAL,
                                   variable=self._hue_min)
        self.sat_max_label = Label(self.hsvframe, text="Saturation max")
        self.sat_max_scale = Scale(self.hsvframe, from_=0, to=255, length=200, orient=HORIZONTAL,
                                   variable=self._sat_max)
        self.sat_min_label = Label(self.hsvframe, text="Saturation min")
        self.sat_min_scale = Scale(self.hsvframe, from_=0, to=255, length=200, orient=HORIZONTAL,
                                   variable=self._sat_min)
        self.val_max_label = Label(self.hsvframe, text="Value max")
        self.val_max_scale = Scale(self.hsvframe, from_=0, to=255, length=200, orient=HORIZONTAL,
                                   variable=self._val_max)
        self.val_min_label = Label(self.hsvframe, text="Value min")
        self.val_min_scale = Scale(self.hsvframe, from_=0, to=255, length=200, orient=HORIZONTAL,
                                   variable=self._val_min)
        # Hue
        self.hue_max_label.grid(row=1, column=1, sticky="E")
        self.hue_max_scale.grid(row=1, column=2)
        self.hue_min_label.grid(row=2, column=1, sticky="E")
        self.hue_min_scale.grid(row=2, column=2)
        # Saturation
        self.sat_max_label.grid(row=3, column=1, sticky="E")
        self.sat_max_scale.grid(row=3, column=2)
        self.sat_min_label.grid(row=4, column=1, sticky="E")
        self.sat_min_scale.grid(row=4, column=2)
        # Value
        self.val_max_label.grid(row=5, column=1, sticky="E")
        self.val_max_scale.grid(row=5, column=2)
        self.val_min_label.grid(row=6, column=1, sticky="E")
        self.val_min_scale.grid(row=6, column=2)


        # Start GUI mainloop
        self.root.mainloop()

    def updater(self):
        """
        Tells facade to listen for button press.
        Sets the hsvvalues
        """
        self.facade.gettriggerpress()
        self.sethsvvalues()

    def showaboutinfo(self):
        """
        Pop-up message box containing About info
        """
        messagebox.showinfo("About", "3D print error detection\n"
                                     "Author: Tomas Paulsen\n"
                                     "Version: 1.0")

    def enterthresh(self):
        """
        Sends entry threshold to facade.
        """
        threshstring = self.threshentry.get()
        threshint = int(threshstring)
        self.facade.setthresh(threshint)

    def erode(self):
        """
        Button handling relief and set flag.
        """
        if self.erodebtn.config('relief')[-1] == 'sunken':
            self.erodebtn.config(relief="raised", text="Erode")
            self.facade.erode(flag=False)
        else:
            self.erodebtn.config(relief="sunken", text="UnErode")
            self.facade.erode(flag=True)

    def dilate(self):
        """
        Button handling relief and set flag.
        """
        if self.dilateebtn.config('relief')[-1] == 'sunken':
            self.dilateebtn.config(relief="raised", text="Dilate")
            self.facade.dilate(flag=False)
        else:
            self.dilateebtn.config(relief="sunken", text="UnDilate")
            self.facade.dilate(flag=True)

    def open(self):
        """
        Button handling relief and set flag.
        """
        if self.openbtn.config('relief')[-1] == 'sunken':
            self.openbtn.config(relief="raised", text="Open")
            self.facade.open(flag=False)
        else:
            self.openbtn.config(relief="sunken", text="UnOpen")
            self.facade.open(flag=True)

    def close(self):
        """
        Button handling relief and set flag.
        """
        if self.closebtn.config('relief')[-1] == 'sunken':
            self.closebtn.config(relief="raised", text="Close")
            self.facade.close(flag=False)
        else:
            self.closebtn.config(relief="sunken", text="UnClose")
            self.facade.close(flag=True)

    def chechsimilarity(self):
        self.facade.chechsimilarity()

    def setpreset(self, *args):
        self.usehsvpreset()

    def hsvreset(self):
        self._hue_max.set(179)
        self._hue_min.set(0)
        self._sat_max.set(255)
        self._sat_min.set(0)
        self._val_max.set(255)
        self._val_min.set(0)

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
        """
        Button handling relief and set flag.
        Instantiates a Camera page if not already opened.
        """
        if not self._camerapageopen:
            self._camerapage = Camerapage(facade=self.facade, parent=self)
            self._camerapageopen = True
        else:
            self.stopcamerapage()
            self._camerapageopen = False

        if self.startcamerabtn.config('relief')[-1] == 'sunken':
            self.startcamerabtn.config(relief="raised", text="Start Camera")
        elif self._camerapageopen:
            self.startcamerabtn.config(relief="sunken", text="Stop Camera")

    def openimagepage(self):
        """
        Button handling relief and set flag.
        Instantiates a Image page if not already opened.
        """
        if not self._imagepageopen:
            if not self.facade.isregempty():
                self._imagepage = Imagepage(facade=self.facade, reversedindex=-1)
                self._imagepageopen = True
            else:
                print("Image register is empty!!")
        else:
            self.stopimagepage()
            self._imagepageopen = False

        if self.startlastimgpagebtn.config('relief')[-1] == 'sunken':
            self.startlastimgpagebtn.config(relief="raised", text="Start Image display")
        elif self._imagepageopen:
            self.startlastimgpagebtn.config(relief="sunken", text="Stop Image display")

    def opensecondimagepage(self):
        """
        Button handling relief and set flag.
        Instantiates a Image page if not already opened.
        """
        if not self._secondimagepageopen:
            if not self.facade.isregempty():
                self._secondimagepage = Imagepage(facade=self.facade, reversedindex=-2)
                self._secondimagepageopen = True
            else:
                print("Image register is empty!!")
        else:
            self.stopsecondimagepage()
            self._secondimagepageopen = False

        if self.startsecondlastimgpagebtn.config('relief')[-1] == 'sunken':
            self.startsecondlastimgpagebtn.config(relief="raised", text="Start Second Image display")
        elif self._secondimagepageopen:
            self.startsecondlastimgpagebtn.config(relief="sunken", text="Stop Second Image display")

    def stopcamerapage(self):
        self._camerapage.destructor()

    def stopimagepage(self):
        self._imagepage.destructor()

    def stopsecondimagepage(self):
        self._secondimagepage.destructor()

    def getcamerapage(self):
        return self._camerapage

    def quit(self):
        self.root.destroy()

    # TODO: Implement or remove Timelapse functionallity
    def starttimelapse(self):
        folder_selected = filedialog.askdirectory()
        self._folderPath.set(folder_selected)
        pass

    def stoptimelapse(self):
        pass

    def addmask(self):
        """
        Button handling relief and set flag.
        """
        if self._camerapageopen:
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
        """
        Button handling relief and set flag.
        """
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

    def savemasked(self):
        """
        Button handling relief and set flag.
        """
        if self.savemaskedbtn.config('relief')[-1] == 'sunken':
            self.savemaskedbtn.config(relief="raised", text="Save Masked Images")
            self._savemaskedon = False
        else:
            self.savemaskedbtn.config(relief="sunken", text="Save Unmasked Images")
            self._savemaskedon = True

        if self._savemaskedon:
            self.facade.setsavemasked(True)
        else:
            self.facade.setsavemasked(False)


class Camerapage():
    """
    A class representing the Camera page of the application.
    """

    def __init__(self, facade, parent):
        """
        :param facade: Facade instance that connects backend functionality
        :param parent: Parent window running GUI mainloop
        """

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
        """
        Pulling frames from facade for displaying.
        Reruns after 30ms to update window.
        """
        self.parent.updater()
        if self.facade.getapplymask():
            if self.facade.getbinarymask():
                self.current_image = self.facade.getbinaryvideo()
            else:
                if self.facade.getinvertedmask():
                    self.current_image = self.facade.getmaskedframe(inverted=True)
                elif not self.facade.getinvertedmask():
                    self.current_image = self.facade.getmaskedframe(inverted=False)

            imgtk = ImageTk.PhotoImage(image=self.current_image)
            self.panel.imgtk = imgtk
            self.panel.config(image=imgtk)
        else:
            self.current_image = self.facade.getcleanframe()
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


class Imagepage():
    """
    A class representing the Image page of the application.
    """

    def __init__(self, facade, reversedindex):

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

    def run(self):
        """
        Pulling frames from facade for displaying.
        Reruns after 1s to update window.
        """
        self.current_image = self.facade.getlastimage(index=self.reversedindex)
        imgtk = ImageTk.PhotoImage(self.current_image)
        self.panel.imgtk = imgtk
        self.panel.config(image=imgtk)

        self.root.after(1000, self.run)

    def destructor(self):
        """ Destroy the root object and release all resources """
        print("[INFO] closing image...")
        self.root.destroy()
        global imagepageopen
        imagepageopen = False
