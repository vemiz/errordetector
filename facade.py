
import cv2

from camera import Camera
from imageprocessor import Processor
from tkinter import *
from imageregister import Imageregister
from trigger import Trigger
import threading


class Facade(threading.Thread):
    """
    Represents the facade that connects backend subsystems to an simpler interface.
    """
    def __init__(self, useRPi):
        """
        :param useRPi: Flag for using Raspberry pi or pc
        """
        threading.Thread.__init__(self)
        self._useRPi = useRPi

        # Instantiates subsystems
        self._camera = Camera(self._useRPi)
        self._processor = Processor(self)
        self._trigger = Trigger(self._useRPi)
        self._imageregister = Imageregister()

        # Mask handling flags
        self._applymask = False
        self._invertedmask = False
        self._binarymask = False
        self.savemaskedon = False

    def run(self):
        self.gettriggerpress()

    def setlogfilename(self, name):
        self._processor.setlogfilename(name)

    def erode(self, flag):
        """
        Set erode flag in processor instance
        :param flag:
        """
        self._processor.seterode(flag)

    def dilate(self, flag):
        """
        Set dilate flag in processor instance
        :param flag:
        """
        self._processor.setdilate(flag)

    def open(self, flag):
        """
        Set open flag in processor instance
        :param flag:
        """
        self._processor.setopen(flag)

    def close(self, flag):
        """
        Set close flag in processor instance
        :param flag:
        """
        self._processor.setcolse(flag)

    def setthresh(self, thresh):
        """
        Set treshold value in processor instance
        :param thresh: Threshold value
        """
        self._processor.setthresh(thresh)

    def chechsimilarity(self):
        """
        Send two last images in register to processor
        for checking how similar they are.
        """
        image1 = self.getlastimage(index=-1)
        image2 = self.getlastimage(index=-2)
        similarity = self._processor.chechsimilarity(image1, image2)
        print("Diff = " + str(round(similarity, 5)))

    def setapplymask(self, flag):
        """
        Set apply mask flag
        :param flag:
        """
        self._applymask = flag

    def getapplymask(self):
        """
        :return: Apply mask flag
        """
        return self._applymask

    def setinvertedmask(self, flag):
        """
         Set inverted mask flag
         :param flag:
         """
        self._invertedmask = flag

    def getinvertedmask(self):
        """
        :return: inverted mask flag
        """
        return self._invertedmask

    def setbinarymask(self, flag):
        """
         Set binary mask flag
         :param flag:
         """
        self._binarymask = flag

    def getbinarymask(self):
        """
        :return: binary mask flag
        """
        return self._binarymask

    def getcameraframe(self):
        """
        :return: Frame from the camera
        """
        return self._camera.get_video_frame()

    def sethsvhigh(self, value):
        """
        :param value: HSV upper range
        """
        self.hsvhigh = value

    def sethsvlow(self, value):
        """
        :param value: HSV lower range
        """
        self.hsvlow = value

    def getmaskedframe(self, inverted):
        """
        Gets masked frame from the processor
        :param inverted: Flag for inverting mask
        :return: Masked frame
        """
        self._processor.updatehsv(hsvlow=self.hsvlow, hsvhigh=self.hsvhigh)
        self.maskedframe = self._processor.get_masked_video(inverted=inverted)
        return self.maskedframe

    def getbinaryvideo(self):
        """
        Gets the binary frame from the processor
        :return: Binary frame
        """
        self._processor.updatehsv(hsvlow=self.hsvlow, hsvhigh=self.hsvhigh)
        self.binaryframe = self._processor.getrawmask()
        return self.binaryframe

    def getcleanframe(self):
        """
        Gets the unaltered frame from the processor
        :return: Clean frame
        """
        self.cleanframe = self._processor.get_clean_video_stream()
        return self.cleanframe

    def onbuttonpress(self):
        """
        Saves current frame to the image register
        """
        if self.savemaskedon:
            frame = self.getmaskedframe(False)
        else:
            frame = self.getcleanframe()
        self._imageregister.addimg(frame)
        print("[INFO] The button was pressed")
        if self._imageregister.getlength() > 1:
            self.chechsimilarity()

    def gettriggerpress(self):
        """
        Listens for trigger press and calls onbuttonpress()
        """
        if True:
            if self._trigger.pressed():
                self.onbuttonpress()

    #  https://stackoverflow.com/questions/11541154/checking-images-for-similarity-with-opencv
    # TODO: Implement or remove.
    def comparelastimages(self):
        currentframe = self._imageregister.getframe()
        lastframe = self._imageregister.getlastframe()
        diff = self._processor.get_image_diff(currentframe, lastframe)
        print(diff)

    def getlastimage(self, index):
        """
        Gets image from register
        :param index: Index of the image to return. Use negative index to retrive from the end of the register
        :return: Image from register
        """
        frame = self._imageregister.getframe(index=index)
        #image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        return frame

    def printregister(self):
        """
        Tells the register to print its length
        """
        self._imageregister.printlist()

    def isregempty(self):
        """
        Asks the imageregister if it is empty
        :return: True is reg is empty, False otherwise
        """
        return self._imageregister.isempty()

    def setsavemasked(self, flag):
        """
        Set save mask flag
        :param flag:
        """
        self.savemaskedon = flag

    def quit(self):
        self._camera.terminate()


