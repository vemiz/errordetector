"""
Facaden skal koble GUIen til ei rekke av klasser for å beholde lesbarheit og struktur i programmet.
Denne makerer meir komplekse underliggende strukturer, og gjer at ein får enkapsling. Altså eit interface for subsystem.
"""
from camera import Camera
from imageprocessor import Processor
from tkinter import *


class Facade:
    def __init__(self):
        self._camera = Camera()
        self._processor = Processor(self)

    def startcamera(self):
        self._camera.start()

    def getprocessor(self):
        return self._processor()

    def getcameraframe(self):
        return self._camera.get_video_frame()

    def sethsvhigh(self, value):
        self.hsvhigh = value

    def sethsvlow(self, value):
        self.hsvlow = value

    def getmaskedvideo(self):
        self.maskedframe = self._processor.get_masked_video(hsvhigh=self.hsvhigh,hsvlow=self.hsvlow)
        return self.maskedframe

    def getcleanvideo(self):
        self.cleanframe = self._processor.get_clean_video_stream()
        return self.cleanframe

    def terminatecamera(self):
        self._camera.terminate()
