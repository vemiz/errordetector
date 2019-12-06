
import time
from threading import Thread
import cv2


class Camera:
    """
    A class representing a camera.
    """
    def __init__(self, useRPi):
        """
        :param useRPi: Flag for using raspberry pi or pc
        """
        self.videosrc = 0
        self.resolution = (640, 480)  # (3280, 2464) (1088, 720) (640, 480) (1280, 720)
        self.framerate = 30
        self.usepicamera = useRPi
        self.frame = None
        self.stopped = False
        # Imports necessary packages If raspberry pi is used.
        if self.usepicamera:
            from picamera.array import PiRGBArray
            from picamera import PiCamera
            self.camera = PiCamera()
            self.camera.resolution = self.resolution
            self.camera.framerate = self.framerate
            self.camera.awb_mode = 'incandescent'
            self.camera.shutter_speed = 8000
            self.camera.iso = 100
            self.rawcapture = PiRGBArray(self.camera, size=self.resolution)
            self.stream = self.camera.capture_continuous(self.rawcapture,
                                                      format="bgr", use_video_port=True)
            time.sleep(1)
        else:  # Imports necessary packages If raspberry pi is not used.
            self.cam = cv2.VideoCapture(self.videosrc, cv2.CAP_DSHOW)
            if not self.cam.isOpened():
                raise ValueError("Unable to open video source", self.videosrc)
            self.cam.set(cv2.CAP_PROP_AUTOFOCUS, False)
            self.cam.set(cv2.CAP_PROP_FOCUS, 0.0)
            self.cam.set(3, self.resolution[0])
            self.cam.set(4, self.resolution[1])
            self.cam.set(cv2.CAP_PROP_FPS, self.framerate)

        # Start deamon thread when camera initialises
        self.th = Thread(target=self.update, daemon=True, args=())
        self.th.start()

    def start(self):
        self.stopped = False

    def update(self):
        """
        Reads frames from the camera
        """
        if self.usepicamera:
            for f in self.stream:
                self.frame = f.array
                self.rawcapture.truncate(0)

                if self.stopped:
                    self.stream.close()
                    self.rawcapture.close()
                    self.camera.close()
                    return
        else:
            while True:
                if self.stopped:
                    return

                self.ret, self.frame = self.cam.read()
                if not self.ret:
                    print("[ERROR] Cant read frame from camera")

    def get_video_frame(self):
        """
        :return: the frame most recently read frame
        """
        return self.frame

    def terminate(self):
        self.stopped = True

    def __del__(self):
        self.stopped = True
        if not self.usepicamera:
            if self.cam.isOpened():
                self.cam.release()
                cv2.destroyAllWindoes()

