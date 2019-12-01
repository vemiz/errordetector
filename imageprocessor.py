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
        self.kernal = np.ones((5, 5), np.uint8)
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
            mask = cv2.inRange(hsvimage, self.hsv_low, self.hsv_high)
            if inverted:
                mask = cv2.bitwise_not(mask)

            maskedimg = cv2.bitwise_and(rgbimage, rgbimage, mask=mask)
            self.current_image = Image.fromarray(maskedimg)
            return self.current_image
        else:
            print("[INFO] Missing HSV mask!")

    def getbinaryframe(self):
        frame = self.facade.getcameraframe()
        hsvimage = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsvimage, self.hsv_low, self.hsv_high)
        return mask

    # https://stackoverflow.com/questions/11541154/checking-images-for-similarity-with-opencv
    def get_image_diff(self, img1, img2):
        image1 = img1
        image2 = img2
        #diffimg = cv2.subtract(image1, image2)
        image1hist = cv2.calcHist([image1], [0], None, [256], [0, 256])
        image2hist = cv2.calcHist([image2], [0], None, [256], [0, 256])
        diffimg = cv2.matchTemplate(image1hist, image2hist, cv2.TM_CCOEFF_NORMED)[0][0]
        diff = 1 - diffimg
        #diff = np.count_nonzero(diffimg)
        return diff

    def chechsimilarity(self, img1, img2):
        image1 = np.array(img1)
        image2 = np.array(img2)
        similarity = self.get_image_diff(image1, image2)
        return similarity

    def updatehsv(self, hsvlow, hsvhigh):
        self.hsv_low = hsvlow
        self.hsv_high = hsvhigh

    def erodemask(self, mask):
        eroded = cv2.erode(mask, self.kernal, iterations=1)
        return eroded

    def dilatemask(self, mask):
        dilated = cv2.dilate(mask, self.kernal, iterations=1)
        return dilated

    def openmask(self, mask):
        opened = cv2.morphologyEx(mask, cv2.MORPH_OPEN, self.kernal)
        return opened

    def closemask(self, mask):
        closed = cv2.morphologyEx(mask, cv2.MORPH_Close, self.kernal)
        return closed

    def getcontours(self, mask):
        _, contours = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
        return contours

    def getcontoursarea(self, mask):
        contours = self.getcontours(mask)
        area = cv2.contourArea(contours)
        return area
