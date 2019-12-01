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
        img = image
        self._imglist.append(img)

    def getframe(self, index):
        self.index = index
        self._currentframe = self._imglist[self.index]
        return self._currentframe

    # Mabye not necessary with indexing in method over
    def getlastframe(self):
        self._lastframe = self._imglist[-2]
        return self._lastframe

    # For debugging TODO: Remove when satisfying result
    def printlist(self):
        print(len(self._imglist))
        # cv2.imshow('Current Image', self._imglist[-1])

    def getlength(self):
        return len(self._imglist)