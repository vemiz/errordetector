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
        t1 = Thread(target=self.get_video_stream, args=(), daemon=True)
        t1.start()

    def get_video_stream(self):
        while True:
            if self.cam.isOpened():
                ret, self.frame = self.cam.read()
                if ret:
                    return ret, self.frame
                else:
                    return ret, None

    def terminate(self):
        self.cam.release()

    def __del__(self):
        if self.cam.isOpened():
            self.cam.release()
