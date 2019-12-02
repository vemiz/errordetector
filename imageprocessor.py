import cv2
import numpy as np
from PIL import ImageTk, Image
import threading


class Processor(threading.Thread):
    def __init__(self, facade):
        threading.Thread.__init__(self)
        self.facade = facade
        self.hsv_low = None
        self.hsv_high = None
        self.kernal = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
        self.rawmask = None
        #Flags
        self.eroded = False
        self.dilated = False
        self.open = False
        self.close = False
        self.thresh = 10000

        self.daemon = True
        self.start()

    def get_clean_video_stream(self):
        frame = self.facade.getcameraframe()
        # Check if frame is empty. The first few at camera startup will be.
        if np.any(frame):
            image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            self.current_image = Image.fromarray(image)
            return self.current_image

    def get_masked_video(self, inverted=False):
        frame = self.facade.getcameraframe()
        if self.hsv_low is not None:
            hsvimage = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
            rgbimage = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            self.rawmask = cv2.inRange(hsvimage, self.hsv_low, self.hsv_high)
            if self.eroded:
                self.mask = self.erodemask(self.rawmask)
            if self.dilated:
                self.mask = self.dilatemask(self.rawmask)
            if self.open:
                self.mask = self.openmask(self.rawmask)
            if self.close:
                self.mask = self.closemask(self.rawmask)
            if not self.eroded and not self.dilated and not self.open and not self.close:
                self.mask = cv2.inRange(hsvimage, self.hsv_low, self.hsv_high)
            if inverted:
                self.mask = cv2.bitwise_not(self.mask)

            #maskedimg = cv2.bitwise_and(rgbimage, rgbimage, mask=self.mask)
            self.current_image = Image.fromarray(self.mask)
            return self.current_image
        else:
            print("[INFO] Missing HSV mask!")

    def getrawmask(self):
        frame = self.facade.getcameraframe()
        hsvimage = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        self.mask = cv2.inRange(hsvimage, self.hsv_low, self.hsv_high)
        return self.mask

    # https://stackoverflow.com/questions/11541154/checking-images-for-similarity-with-opencv
    def get_image_diff(self, img1, img2):
        image1 = cv2.GaussianBlur(img1, (5, 5), cv2.BORDER_DEFAULT)
        image2 = cv2.GaussianBlur(img2, (5, 5), cv2.BORDER_DEFAULT)
        #diffimg = cv2.subtract(image2, image1)
        diffimg = np.subtract(image1, image2)
        #diff = 1 - diffimg
        yderivate = cv2.Sobel(diffimg, cv2.CV_64F, 0, 1, ksize=5)
        xderivate = cv2.Sobel(diffimg, cv2.CV_64F, 1, 0, ksize=5)
        cv2.imshow("Diff image", diffimg)
        cv2.imshow("Y-Derivate image", yderivate)
        cv2.imshow("X-Derivate image", xderivate)

        diff = np.count_nonzero(diffimg)
        return diff

    def chechsimilarity(self, img1, img2):
        image1 = np.array(img1)
        image2 = np.array(img2)
        similarity = self.get_image_diff(image1, image2)
        if similarity > self.thresh:
            print("Motinon is bigger than threshold. Check printer")
        return similarity

    # def get_image_diff(self, img1, img2):
    #     image1 = img1
    #     image2 = img2
    #     #diffimg = cv2.subtract(image1, image2)
    #     image1hist = cv2.calcHist([image1], [0], None, [256], [0, 256])
    #     image2hist = cv2.calcHist([image2], [0], None, [256], [0, 256])
    #     diffimg = cv2.matchTemplate(image1hist, image2hist, cv2.TM_CCOEFF_NORMED)[0][0]
    #     diff = 1 - diffimg
    #     #diff = np.count_nonzero(diffimg)
    #     return diff

    def updatehsv(self, hsvlow, hsvhigh):
        self.hsv_low = hsvlow
        self.hsv_high = hsvhigh

    def getcontours(self, mask):
        _, contours = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
        return contours

    def getcontoursarea(self, mask):
        contours = self.getcontours(mask)
        area = cv2.contourArea(contours)
        return area

    #Morph operations
    def erodemask(self, rawmask):
        mask = cv2.erode(rawmask, self.kernal, iterations=1)
        return mask

    def dilatemask(self, rawmask):
        dilated = cv2.dilate(rawmask, self.kernal, iterations=1)
        return dilated

    def openmask(self, rawmask):
        opened = cv2.morphologyEx(rawmask, cv2.MORPH_OPEN, self.kernal)
        return opened

    def closemask(self, rawmask):
        closed = cv2.morphologyEx(rawmask, cv2.MORPH_CLOSE, self.kernal)
        return closed

    def seterode(self, flag):
        self.eroded = flag

    def setdilate(self, flag):
        self.dilated = flag

    def setopen(self, flag):
        self.open = flag

    def setcolse(self, flag):
        self.close = flag

    def setthresh(self, thresh):
        self.thresh = thresh