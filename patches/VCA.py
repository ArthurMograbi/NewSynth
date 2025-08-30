#patches/VCA.py
from .Patch import Patch

class VCA(Patch):

    _metadata = {
        "io": {
            "input":"in",
            "amplification":"in",
            "output":"out"
        }
    }

    def __init__(self,amplification:float=1.0):
        super().__init__()
        self.input = 0.0
        self.amplification = amplification
        self.output = 0.0

    def step(self):
        self.getInputs()
        #print(self.input, self.amplification)
        self.output = self.input * self.amplification
        self.time+=1