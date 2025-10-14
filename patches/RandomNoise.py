#patches/RandomNoise.py
from .Patch import Patch
import random

class RandomNoise(Patch):

    _metadata = {
        "io": {
            "scale":"in",
            "random":"out",
            "normal":"out"
        }
    }

    def __init__(self):
        super().__init__()
        self.scale = 1.0
        self.output = 0.0

    def step(self):
        self.getInputs()
        self.random = self.scale * random.uniform(-1, 1)
        self.normal =random.normalvariate(0.5,0.5)
        self.time+=1