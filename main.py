"""
Kravspec:
Deteksjon av feil i 3d-printing. Programmet skal monitorere 3d-printing ved kamera.
Det skal oppdage om det blir feil på printet, og varsle brukeren.
Det skal sammenligne bilde med gitt mellomrom for å finne endring som er større enn ein gitt terskel.
Det skal vise live feed frå kamera. Det skal lage timelapse av bilda, og loope det til brukeren.
Det skal ha muligheit for å sette parameter som hsv-verdiar, manuellt croppe bilde.
Det skal også croppe dysa ut av bilde ved å spore ein aruco tag.
Det skal lagre timelapsen når printet er ferdig (bruker styrt).
"""
import first_GUI
from facade import Facade

def main():
    first_GUI.vp_start_gui()

if __name__ == "__main__":
    main()
