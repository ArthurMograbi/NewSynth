#patches/ClockedSample.py
from .Patch import Patch

class ClockedSample(Patch):
    threshold = 0.1

    _metadata = {
        "io": {
            "input":"in",
            "clock":"in",
            "output":"out"
        }
    }

    def __init__(self,input:float=0.0,clock:float=0.0):
        super().__init__()
        self.input = input
        self.clock = clock
        self.output = 0.0

    def step(self):
        self.getInputs()
        #print(self.input, self.amplification)
        if self.clock > ClockedSample.threshold:
            self.output = self.input
        self.time+=1