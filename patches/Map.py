#patches/Map.py
from .Patch import Patch

class Map(Patch):

    _metadata = {
        "io": {
            "input":"in",
            "inlower":"in",
            "inupper":"in",
            "outlower":"in",
            "outupper":"in",
            "output":"out"
        }
    }

    def __init__(self,input:float=0.0,inlower:float=0.0,inupper:float=1.0,outlower:float=0.0,outupper:float=12.0):
        super().__init__()
        self.input = input
        self.inlower = inlower
        self.inupper = inupper
        self.outlower = outlower
        self.outupper = outupper
        self.output = 0.0

    def step(self):
        self.getInputs()
        scaleMult = (self.outupper-self.outlower)/(self.inupper-self.inlower)
        self.output = (self.input-self.inlower)*scaleMult + self.outlower
        self.time+=1