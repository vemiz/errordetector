"""
Facaden skal koble GUIen til ei rekke av klasser for å beholde lesbarheit og struktur i programmet.
Denne makerer meir komplekse underliggende strukturer, og gjer at ein får enkapsling. Altså eit interface for subsystem.
"""
import cv2

from camera import Camera
from imageprocessor import Processor
from tkinter import *
from imageregister import Imageregister
from trigger import Trigger
import threading


class Facade(threading.Thread):
    def __init__(self, useRPi):
        threading.Thread.__init__(self)
        self._useRPi = useRPi
        self._camera = Camera(self._useRPi)
        self._processor = Processor(self)
        self._trigger = Trigger(self._useRPi)
        self._imageregister = Imageregister()
        self._applymask = False
        self._invertedmask = False
        self._binarymask = False
        self.savemaskedon = False

    def run(self):
        self.gettriggerpress()

    def erode(self, flag):
        self._processor.seterode(flag)

    def dilate(self, flag):
        self._processor.setdilate(flag)

    def open(self, flag):
        self._processor.setopen(flag)

    def close(self, flag):
        self._processor.setcolse(flag)

    def setthresh(self, thresh):
        self._processor.setthresh(thresh)

    def chechsimilarity(self):
        image1 = self.getlastimage(index=-1)
        image2 = self.getlastimage(index=-2)
        similarity = self._processor.chechsimilarity(image1, image2)
        print("Diff = " + str(round(similarity, 5)))

    def setapplymask(self, flag):
        self._applymask = flag

    def getapplymask(self):
        return self._applymask

    def setinvertedmask(self, flag):
        self._invertedmask = flag

    def getinvertedmask(self):
        return self._invertedmask

    def setbinarymask(self, flag):
        self._binarymask = flag

    def getbinarymask(self):
        return self._binarymask

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

    def getmaskedframe(self, inverted):
        self._processor.updatehsv(hsvlow=self.hsvlow, hsvhigh=self.hsvhigh)
        self.maskedframe = self._processor.get_masked_video(inverted=inverted)
        return self.maskedframe

    def getbinaryvideo(self):
        self._processor.updatehsv(hsvlow=self.hsvlow, hsvhigh=self.hsvhigh)
        self.binaryframe = self._processor.getrawmask()
        return self.binaryframe

    def getcleanframe(self):
        self.cleanframe = self._processor.get_clean_video_stream()
        return self.cleanframe

    def terminatecamera(self):
        self._camera.terminate()

    def onbuttonpress(self):
        if self.savemaskedon:
            frame = self.getmaskedframe(False)
        else:
            frame = self.getcleanframe()
        self._imageregister.addimg(frame)
        print("[INFO] The button was pressed")
        if self._imageregister.getlength() > 3:
            self.chechsimilarity()

    def gettriggerpress(self):
        if True:
            if self._trigger.pressed():
                self.onbuttonpress()
        # else:
        #    print("RPi not in use!!!!!!")

    # https://stackoverflow.com/questions/11541154/checking-images-for-similarity-with-opencv
    def comparelastimages(self):
        currentframe = self._imageregister.getframe()
        lastframe = self._imageregister.getlastframe()
        diff = self._processor.get_image_diff(currentframe, lastframe)
        print(diff)

    def getlastimage(self, index):
        frame = self._imageregister.getframe(index=index)
        #image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        return frame

    def printregister(self):
        self._imageregister.printlist()

    def isregempty(self):
        return self._imageregister.isempty()

    def setsavemasked(self, flag):
        self.savemaskedon = flag

