#patches/VCA.py
from .Patch import Patch

class CountTo(Patch):

    _metadata = {
        "io": {
            "speed":"in",
            "limit":"in",
            "output":"out"
        }
    }

    def __init__(self,speed:float=1.0,limit:float=100000):
        super().__init__()
        self.speed = speed
        self.limit = limit
        self.output = 0.0

    def step(self):
        self.getInputs()
        self.output = (self.output+self.speed) %self.limit
        self.time+=1