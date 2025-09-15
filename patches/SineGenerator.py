#patches/SineGenerator.py
import numpy as np
from .Patch import Patch

class SineGenerator(Patch):
    """Generates a sine wave that can be connected to other patches."""
    
    _metadata = {
        "io": {
            "output": "out",
            "frequency": "in",
            "amplitude": "in",
            "phase_offset": "in"
        }
    }
    
    def __init__(self, frequency:float=440, amplitude:float=0.5):
        super().__init__()
        self.frequency = frequency
        self.amplitude = amplitude
        self.phase = 0.0
        self.phase_offset = 0.0
        self.output = 0.0
        
    
    def step(self):
        # Update parameters if connected to other patches
        self.getInputs()
        
        self.step_size = 2 * np.pi * self.frequency / self.board.sample_rate
        
        # Generate the next sample
        self.output = self.amplitude * np.sin(self.phase+self.phase_offset)
        
        # Update phase, keeping it within [0, 2π)
        self.phase = (self.phase + self.step_size) % (2 * np.pi)
        self.time += 1