#patches/VCA.py
from .Patch import Patch

class AddConst(Patch):

    _metadata = {
        "io": {
            "input":"in",
            "val":"in",
            "output":"out"
        }
    }

    def __init__(self,val:float=1.0):
        super().__init__()
        self.input = 0.0
        self.val = val
        self.output = 0.0

    def step(self):
        self.getInputs()
        #print(self.input, self.amplification)
        self.output = self.input + self.val
        self.time+=1
        self.input = 0.0 # Reseting variable input