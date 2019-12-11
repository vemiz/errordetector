"""
3D printer error detection application.
This is the main entry for the application.
This application is part of a bachelor thesis project
at NTNU Ålesund Department of ICT and Natural Sciences.
Developed and written by Tomas Paulsen.

RUN:    On Raspberry pi set "useRPI" flag to True
        On PC set "useRPI" flag to False
        Run main.py to start

Usage:  On Raspberry pi a physical button should be used to trigger gathering of images.
        On PC a key button is used to trigger gathering of images.

        Start camera page.
        Apply mask.
        Set HSV threshold values and morphological operations.
        Apply Save Masked Images.

        Start monitoring 3D print.

        The application alert if error is detected.
"""
from GUI import MainWindow
from facade import Facade


useRPi = True
facade = Facade(useRPi=useRPi)
GUIApplication = MainWindow(facade=facade)
GUIApplication.start()
