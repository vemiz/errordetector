"""
Facaden skal koble GUIen til ei rekke av klasser for å beholde lesbarheit og struktur i programmet.
Denne makerer meir komplekse underliggende strukturer, og gjer at ein får enkapsling. Altså eit interface for subsystem.
"""
from camera import Camera

class Facade:
    def __init__(self):
        self.camera = Camera()
        #self._subsystem_2 = Subsystem2()

    def get_camera_frame(self):
        self.camera.get_frame()

