#patches/VCA.py
from .Patch import Patch

class ThreeMix(Patch):

    _metadata = {
        "io": {
            "in1":"in",
            "in2":"in",
            "in3":"in",
            "output":"out"
        }
    }

    def __init__(self):
        super().__init__()
        self.in1 = 0.0
        self.in2 = 0.0
        self.in3 = 0.0
        self.output = 0.0

    def step(self):
        self.getInputs()
        #print(self.input, self.amplification)
        self.output = self.in1 + self.in2 + self.in3
        self.time+=1