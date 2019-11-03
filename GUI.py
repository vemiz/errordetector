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
from tkinter import ttk
from tkinter import *
import cv2
import imutils as imutils

from camera import Camera
from PIL import ImageTk, Image

LARGE_FONT = ("Verdana", 12)
NORMAL_FONT = ("Verdana", 10)
SMALL_FONT = ("Verdana", 8)


def getbuttons(page, controller):
    if page == StartPage:
        button1 = ttk.Button(page, text="Preview",
                             command=lambda: controller.show_frame(Preview))
        button1.pack()
        button2 = ttk.Button(page, text="Timelapse",
                             command=lambda: controller.show_frame(Timelapse))
        button2.pack()
        button3 = ttk.Button(page, text="Config",
                             command=lambda: controller.show_frame(Config))
        button3.pack()


def popupmsg(msg):
    popup = tk.Tk()
    popup.wm_title("!")
    label = ttk.Label(popup, text=msg, font=NORMAL_FONT)
    label.pack(side="top", fill="x", pady=10)
    B1 = ttk.Button(popup, text="Okay", command=popup.destroy())
    B1.pack()
    popup.mainloop()


class MainApplication(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)

        tk.Tk.iconbitmap(self, default="clienticon.ico")
        tk.Tk.wm_title(self, "3D print error detection")
        tk.Tk.geometry(self, "1280x720")

        menubar = tk.Menu(self)
        filemenu = tk.Menu(menubar, tearoff=0)
        filemenu.add_command(label="Save settings", command=lambda: popupmsg("Not supported yet!"))
        filemenu.add_separator()
        filemenu.add_command(label="Exit", command=quit)
        menubar.add_cascade(label="File", menu=filemenu)
        tk.Tk.config(self, menu=menubar)

        notebook = ttk.Notebook(self)
        notebook.pack(fill="both", expand=True)
        rows = 0
        while rows < 1:
            self.rowconfigure(rows, weight=1)
            self.columnconfigure(rows, weight=1)
            rows += 1
        self.DISPPLAYLABEL_WIDTH = 7
        self.WHITE = "White"
        self.GRAY = '#424242'

        startpage = ttk.Frame(notebook)
        previewpage = ttk.Frame(notebook)
        timelapsepage = ttk.Frame(notebook)
        configpage = ttk.Frame(notebook)
        notebook.add(startpage, text='Start Page')
        notebook.add(previewpage, text='Preview')
        notebook.add(timelapsepage, text='Timelapse')
        notebook.add(configpage, text='Config')

        previewtab = PanedWindow(previewpage)
        previewtab.configure(bg=self.GRAY)
        previewtab.pack(fill="both", expand=True)

        leftpreviewtabmain = PanedWindow(previewtab, orient=VERTICAL, bg=self.GRAY)
        leftpreviewtabmain.configure(bg=self.GRAY, relief='groove', borderwidth='2')
        previewtab.add(leftpreviewtabmain)
        buttonpanel = PanedWindow(leftpreviewtabmain)
        optionlabel = Label(buttonpanel, text="Options", bg=self.GRAY, fg=self.WHITE,
                            font=("Arial", "11"))

        optionbutton = Button(buttonpanel, text='Option', bg=self.GRAY, fg='Orange',
                              height=2, width=20, font=('Arial', '11'), state='disable')
        optionlabel.pack(padx=5, pady=5)
        optionbutton.pack(padx=10, pady=10)


    def show_frame(self, cont):
        frame = self.frames[cont]
        frame.tkraise()


class StartPage(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        label = tk.Label(self, text="Start Page", font=LARGE_FONT)
        label.pack(pady=10, padx=10)

        getbuttons(self, controller)


class Preview(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        label = tk.Label(self, text="Preview", font=LARGE_FONT)
        label.pack(pady=10, padx=10)

        button1 = ttk.Button(self, text="StartPage",
                             command=lambda: controller.show_frame(StartPage))
        button1.pack()

        button2 = ttk.Button(self, text="Timelapse",
                             command=lambda: controller.show_frame(Timelapse))
        button2.pack()

        button3 = ttk.Button(self, text="Config",
                             command=lambda: controller.show_frame(Config))
        button3.pack()


class Timelapse(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        label = tk.Label(self, text="Timelapse", font=LARGE_FONT)
        label.pack(pady=10, padx=10)

        button1 = ttk.Button(self, text="StartPage",
                             command=lambda: controller.show_frame(StartPage))
        button1.pack()

        button2 = ttk.Button(self, text="Preview",
                             command=lambda: controller.show_frame(Preview))
        button2.pack()

        button3 = ttk.Button(self, text="Config",
                             command=lambda: controller.show_frame(Config))
        button3.pack()


class Config(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        label = tk.Label(self, text="Config", font=LARGE_FONT)
        label.pack(pady=10, padx=10)

        button1 = ttk.Button(self, text="StartPage",
                             command=lambda: controller.show_frame(StartPage))
        button1.pack()

        button2 = ttk.Button(self, text="Preview",
                             command=lambda: controller.show_frame(Preview))
        button2.pack()

        button3 = ttk.Button(self, text="Timelapse",
                             command=lambda: controller.show_frame(Timelapse))
        button3.pack()


def run():
    app = MainApplication()
    app.mainloop()
