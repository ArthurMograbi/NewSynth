from .Patch import Patch

class Printer(Patch):

    _metadata = {
        "io": {
            "input":"in",
            "output":"out"
        }
    }

    def __init__(self,interval:int=1000):
        super().__init__()
        self.input = 0.0
        self.interval = interval
        self.output = 0.0

    def step(self):
        self.getInputs()
        #print(self.input, self.interval)
        if not self.time%self.interval: print("Input",self.input)
        self.output = self.input
        self.time+=1