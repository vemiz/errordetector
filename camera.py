"""
Represents an camera
"""
import cv2
#import picamera
#import picamera.array
import time


class Camera:

    def __init__(self, video_source=0):
        self.cam = cv2.VideoCapture(video_source, cv2.CAP_DSHOW)
        if not self.cam.isOpened():
            raise ValueError("Unable to open video source", video_source)
        self.frame = None
        self.cam.set(cv2.CAP_PROP_AUTOFOCUS, False)
        self.cam.set(cv2.CAP_PROP_FOCUS, 0.0)
        self.cam.set(3, 1920)
        self.cam.set(4, 1080)

    def get_video_stream(self):
        ret, frame = self.get_raw_frame()
        return ret, frame

    def get_raw_frame(self):
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
