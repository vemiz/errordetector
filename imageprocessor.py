import cv2
import numpy as np
from PIL import ImageTk, Image
import threading


class Processor(threading.Thread):
    def __init__(self, facade):
        threading.Thread.__init__(self)
        self.facade = facade
        self.daemon = True
        self.start()

    def get_clean_video_stream(self):
        frame = self.facade.getcameraframe()
        # Check if frame is empty. The first few at camera startup will be.
        if np.any(frame):
            image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            self.current_image = Image.fromarray(image)
            return self.current_image

    def get_masked_video(self, hsvlow, hsvhigh, inverted=False):
        hsv_low = hsvlow
        hsv_high = hsvhigh
        frame = self.facade.getcameraframe()
        if hsv_low is not None:
            hsvimage = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
            rgbimage = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            mask = cv2.inRange(hsvimage, hsv_low, hsv_high)
            if inverted:
                mask = cv2.bitwise_not(mask)

            maskedimg = cv2.bitwise_and(rgbimage, rgbimage, mask=mask)
            self.current_image = Image.fromarray(maskedimg)
            return self.current_image
        else:
            print("[INFO] Missing HSV mask!")

    def getbinaryframe(self, hsvlow, hsvhigh):
        hsv_low = hsvlow
        hsv_high = hsvhigh
        frame = self.facade.getcameraframe()
        hsvimage = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsvimage, hsv_low, hsv_high)
        return mask

    # https://stackoverflow.com/questions/11541154/checking-images-for-similarity-with-opencv
    def get_image_diff(self, img1, img2):
        image1 = img1
        image2 = img2
        diffimg = cv2.subtract(image1, image2)
        diff = np.count_nonzero(diffimg)
        return diff
