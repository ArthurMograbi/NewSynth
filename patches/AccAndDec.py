from .Patch import Patch

class AccAndDec(Patch):

    _metadata = {
        "io": {
            "input":"in",
            "output":"out"
        }
    }

    def __init__(self,scale:float=1.0,falloff:float=0.00005,limitLower:float=0.0,limitUpper:float=1.0,absolute=True):
        super().__init__()
        self.scale = scale
        self.falloff = falloff
        self.limitLower = limitLower
        self.limitUpper = limitUpper
        self.input = 0.0
        self.output = 0.0
        self.deltaF = (lambda i,s,f: abs(i)*s-f) if absolute else (lambda i,s,f: i*s-f)

    def step(self):
        self.getInputs()
        self.output += self.deltaF(self.input,self.scale,self.falloff)
        self.output=min(max(self.output,self.limitLower),self.limitUpper)
        self.time+=1