#patches/EveryN.py
from .Patch import Patch

class EveryN(Patch):

    _metadata = {
        "io": {
            "input":"in",
            "n":"in",
            "output":"out"
        }
    }

    def __init__(self,input:float=0.0,n:float=2.0):
        super().__init__()
        self.input = input
        self.n = n
        self.output = 0.0
        self.cur_n = 0

    def step(self):
        self.getInputs()
        if self.input> 0:
            if self.cur_n>= self.n-1:
                self.output = 1.0
            else:
                self.output = 0.0
            self.cur_n+=1
            self.cur_n%= self.n
        else:
            self.output = 0.0
        self.time+=1