"""
Facaden skal koble GUIen til ei rekke av klasser for å beholde lesbarheit og struktur i programmet.
Denne makerer meir komplekse underliggende strukturer, og gjer at ein får enkapsling. Altså eit interface for subsystem.
"""

class Facade:
    def __init__(self):
        self._subsystem_1 = Subsystem1()
        self._subsystem_2 = Subsystem2()

    def operation(self):
        self._subsystem_1.operation1()
        self._subsystem_1.operation2()
        self._subsystem_2.operation1()
        self._subsystem_2.operation2()

