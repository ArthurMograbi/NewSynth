#patches/VCA.py
from .Patch import Patch
from math import pow

class Note2Pitch(Patch):

    _metadata = {
        "io": {
            "input":"in",
            "base_pitch":"in",
            "output":"out"
        }
    }

    def __init__(self,base_pitch=110):
        super().__init__()
        self.base_pitch = base_pitch
        self.input = 0.0
        self.output = 0.0

    def step(self):
        self.getInputs()
        self.output = self.base_pitch * pow(2.0,self.input/12)
        self.time+=1