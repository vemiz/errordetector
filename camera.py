"""
Represents an camera
"""
import cv2
# import picamera
# import picamera.array
import time
from threading import Thread


class Camera:

    def __init__(self, video_source=0):
        self.videosrc = video_source
        self.cam = None
        self.frame = None

    def start(self):
        self.cam = cv2.VideoCapture(self.videosrc, cv2.CAP_DSHOW)
        if not self.cam.isOpened():
            raise ValueError("Unable to open video source", self.videosrc)
        self.cam.set(cv2.CAP_PROP_AUTOFOCUS, False)
        self.cam.set(cv2.CAP_PROP_FOCUS, 0.0)
        self.cam.set(3, 1920)
        self.cam.set(4, 1080)

    def get_video_stream(self):
        ret, frame = self.get_raw_frame()
        return ret, frame

    def get_raw_frame(self):
        while True:
            if self.cam.isOpened():
                ret, self.frame = self.cam.read()
                if ret:
                    return ret, self.frame
                else:
                    return ret, None
            #if self.stop_threads:
            #    break

    def terminate(self):
        self.cam.release()
        #self.stop_threads = True

    def __del__(self):
        if self.cam.isOpened():
            self.cam.release()
