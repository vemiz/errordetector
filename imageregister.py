import cv2

class Imageregister:
    def __init__(self):
        self._imglist = []
        self._currentframe = None
        self._lastframe = None

    def isempty(self):
        if len(self._imglist) == 0:
            return True
        else:
            False

    def addimg(self, image):
        img = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        self._imglist.append(img)

    def getcurrentframe(self):
        self._currentframe = self._imglist[-1]
        return self._currentframe

    def getlastframe(self):
        self._lastframe = self._imglist[-2]
        return self._lastframe

    # For debugging TODO: Remove when satisfying result
    def printlist(self):
        print(len(self._imglist))
        # cv2.imshow('Current Image', self._imglist[-1])