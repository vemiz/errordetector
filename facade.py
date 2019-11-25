"""
Facaden skal koble GUIen til ei rekke av klasser for å beholde lesbarheit og struktur i programmet.
Denne makerer meir komplekse underliggende strukturer, og gjer at ein får enkapsling. Altså eit interface for subsystem.
"""
from camera import Camera
from imageprocessor import Processor
from tkinter import *
from imageregister import Imageregister
from trigger import Trigger

class Facade:
    def __init__(self, useRPi):
        self._useRPi = useRPi
        self._camera = Camera(self._useRPi)
        self._processor = Processor(self)
        self._trigger = Trigger(self._useRPi)
        self._imageregister = Imageregister()

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

    def getmaskedvideo(self, inverted):
        self.maskedframe = self._processor.get_masked_video(hsvhigh=self.hsvhigh,hsvlow=self.hsvlow, inverted=inverted)
        return self.maskedframe

    def getcleanvideo(self):
        self.cleanframe = self._processor.get_clean_video_stream()
        return self.cleanframe

    def terminatecamera(self):
        self._camera.terminate()

    def onbuttonpress(self):
        frame = self.getcameraframe()
        self._imageregister.addimg(frame)
        print("[INFO] The button was pressed")

    def gettriggerpress(self):
        if True:
            if self._trigger.pressed():
                self.onbuttonpress()
        # else:
        #    print("RPi not in use!!!!!!")

    # https://stackoverflow.com/questions/11541154/checking-images-for-similarity-with-opencv
    def comparelastimages(self):
        currentframe = self._imageregister.getcurrentframe()
        lastframe = self._imageregister.getlastframe()
        diff = self._processor.get_image_diff(currentframe, lastframe)
        print(diff)

    def getlastimage(self):
        return self._imageregister.getcurrentframe()

    def printregister(self):
        self._imageregister.printlist()

    def isregempty(self):
        return self._imageregister.isempty()


