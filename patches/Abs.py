#patches/Abs.py
from .Patch import Patch

class Abs(Patch):

    _metadata = {
        "io": {
            "input":"in",
            "output":"out"
        }
    }

    def __init__(self,input:float=0.0):
        super().__init__()
        self.input = input
        self.output = 0.0

    def step(self):
        self.getInputs()
        #print(self.input, self.amplification)
        self.output = abs(self.input)
        self.time+=1