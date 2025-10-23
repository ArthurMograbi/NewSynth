#patches/SkipN.py
from .Patch import Patch

class SkipN(Patch):

    _metadata = {
        "io": {
            "input":"in",
            "n":"in",
            "every":"in",
            "output":"out"
        }
    }

    def __init__(self,input:float=0.0,n:int=1,every:int=8):
        super().__init__()
        self.input = input
        self.n = n
        self.every = every
        self.output = 0.0
        self.cur_n = 0

    def step(self):
        self.getInputs()
        if self.input> 0:
            if self.cur_n>= self.every-self.n-1:
                self.output = 0.0
            else:
                self.output = 1.0
            self.cur_n+=1
            self.cur_n%= self.every
        else:
            self.output = 0.0
        self.time+=1