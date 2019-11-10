"""
GUI applikasjon for deteksjon av feil i 3d-printing.
Den skal ha eit konfigurerings vindu, der bruker kan gi input til hsv terskling og cropping,
samt lagringssted for timelapsen/bilda.
Den skal ha eit preview vindu av camera feeden.
Den skal ha eit vindu for å loope timelapsen.
Den skal ha ei status linje, som skal varsle om feil blir oppdaga. Denne skal vere synlig i alle vindu.
Den skal ha knappar for å skifte vindu.
"""
import threading
import tkinter as tk
from tkinter import ttk, filedialog
from tkinter import *
import cv2
import imutils as imutils
from camera import Camera
from PIL import ImageTk, Image


class MainApplication:

    def __init__(self, master):
        self.master = master
        self.master.geometry("640x480")
        self.master.title("3D print error detection")

        self.label1 = Label(self.master, text="Error detection",
                            fg='black').grid(row=0, column=2)
        self.startcamerabtn = Button(self.master, text="Start camera",
                                     fg='black', command=self.gotocamerapage).grid(row=6, column=2)
        self.quitbtn = Button(self.master, text="Quit", fg='black',
                              command=self.quit).grid(row=6, column=3)
        self.starttimelapsebtn = Button(self.master, text="Start timelapse", fg='black',
                                        command=self.starttimelapse).grid(row=6, column=4)
        self.stoptimelapsebtn = Button(self.master, text="Stop timelapse", fg='black',
                                        command=self.stoptimelapse).grid(row=6, column=5)

        self.folderPath = StringVar()

        # HSV variables. TODO: Sjekk om dei bør flyttast til fasade/GUIsupportmodule
        hue_max = tk.DoubleVar()
        hue_max.set(179)
        hue_min = tk.DoubleVar()
        hue_min.set(0)
        sat_max = tk.DoubleVar()
        sat_max.set(255)
        sat_min = tk.DoubleVar()
        sat_min.set(0)
        val_max = tk.DoubleVar()
        val_max.set(255)
        val_min = tk.DoubleVar()
        val_min.set(0)

        # Hue
        self.hue_max_label = Label(self.master, text="Hue max", fg='black').grid(row=7, column=2)
        self.hue_max_scale = Scale(self.master, from_=0, to=179, length=200,
                                   orient=HORIZONTAL, variable=hue_max).grid(row=7, column=3)
        self.hue_min_label = Label(self.master, text="Hue min", fg='black').grid(row=8, column=2)
        self.hue_min_scale = Scale(self.master, from_=0, to=179, length=200,
                                   orient=HORIZONTAL, variable=hue_min).grid(row=8, column=3)
        # Saturation
        self.sat_max_label = Label(self.master, text="Saturation max", fg='black').grid(row=9, column=2)
        self.sat_max_scale = Scale(self.master, from_=0, to=255, length=200,
                                   orient=HORIZONTAL, variable=sat_max).grid(row=9, column=3)
        self.sat_min_label = Label(self.master, text="Saturation min", fg='black').grid(row=10, column=2)
        self.sat_min_scale = Scale(self.master, from_=0, to=255, length=200,
                                   orient=HORIZONTAL, variable=sat_min).grid(row=10, column=3)
        # Value
        self.val_max_label = Label(self.master, text="Value max", fg='black').grid(row=11, column=2)
        self.val_max_scale = Scale(self.master, from_=0, to=255, length=200,
                                   orient=HORIZONTAL, variable=val_max).grid(row=11, column=3)
        self.val_min_label = Label(self.master, text="Value min", fg='black').grid(row=12, column=2)
        self.val_min_scale = Scale(self.master, from_=0, to=255, length=200,
                                   orient=HORIZONTAL, variable=val_min).grid(row=12, column=3)

    def gotocamerapage(self):
        root2 = Toplevel(self.master)
        myGUI = Camerapage(root2)

    def quit(self):
        self.master.destroy()

    def starttimelapse(self):
        folder_selected = filedialog.askdirectory()
        self.folderPath.set(folder_selected)
        pass

    def stoptimelapse(self):
        pass


class Camerapage:
    def __init__(self, master):
        self.master = master
        self.master.geometry("1280x720")
        self.master.title("Camera")

        self.label1 = Label(self.master, text="Put camera frame here!!", font=10).grid(row=2, column=2)


def run():
    root = Tk()
    app = MainApplication(root)
    root.mainloop()
