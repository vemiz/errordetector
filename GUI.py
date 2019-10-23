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
import cv2

LARGE_FONT = ("Verdana", 12)


class MainApplication(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        container = tk.Frame(self)

        container.pack(side="top", fill="both", expand=True)

        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}

        frame = StartPage(container, self)

        self.frames[StartPage] = frame

        frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame(StartPage)

    def show_frame(self, cont):
        frame = self.frames[cont]
        frame.tkraise()

        # self.parent = parent
        # self.vid = cv2.VideoCapture(0)
        # if not self.vid.isOpened():
        #     raise ValueError("Unable to open video source")
        # # Get video source width and height
        # self.width = self.vid.get(cv2.CAP_PROP_FRAME_WIDTH)
        # self.height = self.vid.get(cv2.CAP_PROP_FRAME_HEIGHT)

    # def __del__(self):
    #     if self.vid.isOpened():
    #         self.vid.release()


class StartPage(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        label = tk.Label(self, text="Start Page", font=LARGE_FONT)
        label.pack(pady=10, padx=10)

        button1 = tk.Button


def run():
    # root = tk.Tk()
    # root.title("GUI")
    app = MainApplication()
    app.mainloop()
