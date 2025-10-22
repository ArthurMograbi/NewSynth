#patches/Clock.py
from .Patch import Patch
import time


class Clock(Patch):

    _metadata = {
        "io": {
            "frequency":"in",
            "output":"out"
        }
    }

    def __init__(self,frequency:float=1.0):
        super().__init__()
        self.frequency = frequency
        self.period = 1_000_000_000.0/frequency
        self.last_time = 0.0
        self.output = 0.0

    @property
    def frequency(self):
        return self._frequency

    @frequency.setter
    def frequency(self, value: float):
        self._frequency = value
        if value>0:
            self.period = 1_000_000_000.0 / value

    def step(self):
        self.getInputs()
        tnow = time.time_ns()
        if tnow  -  self.last_time> self.period:
            self.output = 1.0
            self.last_time = tnow
        else:
            self.output = 0.0
        self.time+=1