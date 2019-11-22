import cv2
import numpy as np
from PIL import ImageTk, Image

from camera import Camera


class Processor:
    def __init__(self):
        self.current_image = None

    def get_clean_video_stream(self, camera):
        cam = camera
        ret, frame = cam.get_video_stream()
        if ret:
            image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            self.current_image = Image.fromarray(image)
            return self.current_image

    def get_masked_video(self, camera, hsvlow, hsvhigh):
        cam = camera
        self.hsv_low = hsvlow
        self.hsv_high = hsvhigh
        ret, frame = cam.get_video_stream()
        if ret and (self.hsv_low is not None):
            hsvimage = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
            rgbimage = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            mask = cv2.inRange(hsvimage, self.hsv_low, self.hsv_high)
            maskedimg = cv2.bitwise_and(rgbimage, rgbimage, mask=mask)
            self.current_image = Image.fromarray(maskedimg)
            return self.current_image
        else:
            print("[INFO] Missing HSV mask!")
