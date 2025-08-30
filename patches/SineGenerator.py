import numpy as np
from .Patch import Patch

class SineGenerator(Patch):
    """Generates a sine wave that can be connected to other patches."""
    
    _metadata = {
        "io": {
            "output": "out",
            "frequency": "in",
            "amplitude": "in"
        }
    }
    
    def __init__(self, frequency=440, amplitude=0.5, sample_rate=44100):
        super().__init__()
        self.frequency = frequency
        self.amplitude = amplitude
        self.sample_rate = sample_rate
        self.phase = 0.0
        self.output = 0.0
        self.step_size = 2 * np.pi * frequency / sample_rate
        
    
    def step(self):
        # Update parameters if connected to other patches
        self.getInputs()
        #print(self.frequency, self.amplitude)
        # Update step size if frequency has changed
        if hasattr(self, 'frequency_input') and self.frequency_input is not None:
            self.step_size = 2 * np.pi * self.frequency_input / self.sample_rate
        else:
            self.step_size = 2 * np.pi * self.frequency / self.sample_rate
        
        # Generate the next sample
        self.output = self.amplitude * np.sin(self.phase)
        
        # Update phase, keeping it within [0, 2π)
        self.phase = (self.phase + self.step_size) % (2 * np.pi)
        self.time += 1