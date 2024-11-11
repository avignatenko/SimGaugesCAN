
from .sim import Sim
from .can import Can

class Device:

    def __init__(self, sim: Sim, can: Can):
        self._sim = sim
        self._can = can

