"""
Represents a trigger.
Used to trigger camera on physical button press
"""
import RPi.GPIO as GPIO
import threading
from time import sleep

GPIO.setmode(GPIO.BOARD)


class Trigger(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self._pressed = False
        self.channel = 16
        # print("[INFO] Trigger started")

        GPIO.setup(self.channel, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        # GPIO.add_event_detect(self.channel, GPIO.RISING, callback= , bouncetime=3000)
        self.daemon = True
        self.start()

    def pressed(self):
        if self._pressed:
            self._pressed = False
            return True
        else:
            return False

    def run(self):
        previous = None
        while 1:
            current = GPIO.input(self.channel)
            sleep(0.01)

            if current == True and previous == False:
                self._pressed = True

                while self._pressed:
                    sleep(0.1)
            previous = current



