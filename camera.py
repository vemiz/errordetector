"""
Represents an camera
"""
import cv2
import time
from threading import Thread


class Camera:
    def __init__(self, useRPi):
        self.videosrc = 0
        self.resolution = (640, 480)  # (3280, 2464) (1088, 720) (640, 480)
        self.framerate = 30
        self.usepicamera = useRPi
        self.frame = None
        self.stopped = False
        if self.usepicamera:
            from picamera.array import PiRGBArray
            from picamera import PiCamera
            self.cam = PiCamera()
            self.cam.resolution = self.resolution
            self.cam.framerate = self.framerate
            self.cam.awb_mode = 'incandescent'
            self.cam.shutter_speed = 8000
            self.cam.iso = 100
            self.rawcapture = PiRGBArray(self.cam, size=self.resolution)
            self.stream = self.cam.capture_continuous(self.rawcapture, format="bgr", use_video_port=True)
            # self.frame = self.stream.array
            time.sleep(1)
        else:
            self.cam = cv2.VideoCapture(self.videosrc, cv2.CAP_DSHOW)
            if not self.cam.isOpened():
                raise ValueError("Unable to open video source", self.videosrc)
            self.cam.set(cv2.CAP_PROP_AUTOFOCUS, False)
            self.cam.set(cv2.CAP_PROP_FOCUS, 0.0)
            #self.cam.set(3, self.resolution[0])
            #self.cam.set(4, self.resolution[1])
            #self.cam.set(cv2.CAP_PROP_FPS, self.framerate)
            # self.cam.set(cv2.CAP_PROP_BUFFERSIZE, 10
        # Start deamon thread when camera initialises
        self.t1 = Thread(target=self.update, daemon=True, args=())
        self.t1.start()

    def start(self):
        self.stopped = False


    def update(self):
        if self.usepicamera:
            for f in self.stream:
                self.frame = f.array
                self.rawcapture.truncate(0)

                if self.stopped:
                    self.stream.close()
                    self.rawcapture.close()
                    self.cam.close()
                    return
        else:
            while True:
                if self.cam.isOpened():
                    self.ret, self.frame = self.cam.read()
                    if not self.ret:
                        print("[ERROR] Cant read frame from camera")

    def get_video_frame(self):
        # return the frame most recently read
        return self.frame

    def terminate(self):
        self.stopped = True
        # self.cam.release()


    def __del__(self):
        if not self.usepicamera:
            if self.cam.isOpened():
                self.cam.release()