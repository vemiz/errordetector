

class Imageregister:
    def __init__(self):
        self._imglist = []
        self._currentframe = None
        self._lastframe = None

    def addimg(self, image):
        self._imglist.append(image)

    def getcurrentframe(self):
        self._currentframe = self._imglist[-1]
        return self._currentframe

    def getlastframe(self):
        self._lastframe = self._imglist[-2]
        return self._lastframe

    # For debugging TODO: Remove when satisfying result
    def printlist(self):
        print(self._imglist)