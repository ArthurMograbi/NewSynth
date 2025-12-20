#patches/WalkingNoise.py
from .Patch import Patch
from random import random, choices

class WalkingNoise(Patch):
    centerness = 20

    _metadata = {
        "io": {
            "scale":"in",
            "velocity":"in",
            "output":"out"
        }
    }

    def __init__(self,scale:float=1.0, velocity:float=0.001):
        super().__init__()
        self.scale = scale
        self.velocity = velocity
        self.output = 0.0

    def step(self):
        self.getInputs()
        #print(self.input, self.amplification)
        rel_dist_2_0 = (self.output / self.scale)
        change = self.velocity * random() * choices([-1,1],[rel_dist_2_0+WalkingNoise.centerness, WalkingNoise.centerness+1-rel_dist_2_0])[0]
        self.output = max(0,min(self.scale, self.output + change))
        self.time+=1