#patches/MajorQuantitizer.py
from .Patch import Patch
from math import floor

class MajorQuantitizer(Patch):
    major_tones = [0, 2, 4, 5, 7, 9, 11]

    _metadata = {
        "io": {
            "in_note":"in",
            "scale_root":"in",
            "out_note":"out"
        }
    }

    def __init__(self,in_note:float=0.0, scale_root:float=0.0):
        super().__init__()
        self.in_note = in_note 
        self.scale_root = scale_root
        self.out_note = 0.0

    def step(self):
        self.getInputs()
        adj_note = floor(self.in_note - 1)
        self.out_note = MajorQuantitizer.major_tones[adj_note%7]+12*(adj_note//7) + self.scale_root
        self.time+=1