##patches/ChromaticFrequencyStepper.py
from .Patch import Patch

class ChromaticFrequencyStepper(Patch):
    """Outputs mouse X and Y positions as properties."""

    _metadata = {
        "io": {
            "input":"in",
            "output":"out"
        }
    }

    def __init__(self,octaves=8):
        super().__init__()
        self.notes = [22.5 * pow(2,i/12) for i in range(octaves*12)]
        self.input = 0.0
        self.output= 0.0

    def step(self):
        self.getInputs()
        nearest_note = min(self.notes, key=lambda note: abs(note - self.input))
        self.output = nearest_note
        self.time+=1