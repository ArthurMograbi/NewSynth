#patches/Filter.py
from .Patch import Patch
import math

class Filter(Patch):
    """A simple low-pass and high-pass filter implementation."""

    _metadata = {
        "io": {
            "input": "in",
            "cutoff": "in",
            "resonance": "in",
            "low_pass": "out",
            "high_pass": "out",
            "band_pass": "out"
        }
    }

    def __init__(self, cutoff=1000, resonance=0.5):
        super().__init__()
        self.cutoff = cutoff
        self.resonance = resonance
        self.input = 0.0
        self.low_pass = 0.0
        self.high_pass = 0.0
        self.band_pass = 0.0
        
        # Filter state variables
        self.low_pass_prev = 0.0
        self.band_pass_prev = 0.0
        
    def step(self):
        self.getInputs()
        
        # Calculate filter coefficients based on cutoff frequency
        # Using a state variable filter design
        f = 2 * math.sin(math.pi * min(0.25, self.cutoff / (self.board.sample_rate * 2)))
        q = 1.0 - self.resonance
        
        # Filter processing
        self.low_pass = self.low_pass_prev + f * self.band_pass_prev
        self.high_pass = self.input - self.low_pass - q * self.band_pass_prev
        self.band_pass = f * self.high_pass + self.band_pass_prev
        
        # Update state variables for next iteration
        self.low_pass_prev = self.low_pass
        self.band_pass_prev = self.band_pass
        
        self.time += 1