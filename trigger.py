"""
Represents a trigger.
Used to trigger camera on physical button press
"""

import threading
from time import sleep


class Trigger(threading.Thread):
    def __init__(self, useRPi):
        threading.Thread.__init__(self)
        self._pressed = False
        self._useRPi = useRPi
        self.channel = 16
        self._keybtn = 'b'

        if self._useRPi:
            import RPi.GPIO as GPIO
            GPIO.setmode(GPIO.BOARD)
            GPIO.setup(self.channel, GPIO.IN, pull_up_down=GPIO.PUD_UP)

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
            if self._useRPi:
                import RPi.GPIO as GPIO  # Second import as workaround for NameError: name 'GPIO' is not defined
                current = GPIO.input(self.channel)
                sleep(0.01)
            else:
                import keyboard
                current = keyboard.is_pressed(self._keybtn)
                pass

            if current == True and previous == False:
                self._pressed = True

                while self._pressed:
                    sleep(0.1)
            previous = current
