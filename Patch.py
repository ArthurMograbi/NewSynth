import sounddevice as sd
import numpy as np
from typing import Dict, List
from abc import ABC, abstractmethod

# Modified Patch class to support audio streaming
class Patch(ABC):
    _metadata = {}
    
    def __init__(self, inputs: Dict[str, 'Patch'] | None= None, outputs: Dict['Patch', str] | None= None):
        self.inputs = inputs or  dict()
        self.outputs = outputs or dict()
        self.time = 0
        self.board = None
    
    def getInputs(self):
        for k, v in self.inputs.items():
            setattr(self, k, v.getOutput(self))
    
    def getOutput(self, patch: 'Patch'):
        while self.time < patch.time:
            self.step()
        return getattr(self, self.outputs[patch])
    
    def connect(patchIn: 'Patch', patchOut: 'Patch', propIn: str, propOut: str):
        print(patchIn,patchOut)
        if patchIn==patchOut: raise RecursionError("Conecting patch to self")
        if patchIn._metadata["io"][propIn] == "in" and patchOut._metadata["io"][propOut] == "out":
            patchIn.inputs[propIn] = patchOut
            
            patchOut.outputs[patchIn] = propOut
        else:
            raise UserWarning("Tried to connect input to input or output to output")
    
    @abstractmethod
    def step(self):
        pass


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


class AudioOutput(Patch):
    """Outputs audio to the sound device using a non-blocking stream."""
    
    _metadata = {
        "io": {
            "input": "in"
        }
    }
    
    def __init__(self, blocksize=1024):
        super().__init__()
        self.input = 0.0
        self.stream = None
        self.blocksize = blocksize
        self.buffer = np.zeros(blocksize, dtype=np.float32)
        self.buffer_index = 0
    
    def audio_callback(self, outdata, frames, time, status):
        if status:
            print(f"Status: {status}")
        
        # Fill the output buffer with samples from our buffer
        outdata[:] = self.buffer.reshape(-1, 1)
        
        # Generate new samples for the next callback
        for i in range(self.blocksize):
            # Step all patches in the board
            for patch in self.board.patches:
                if patch != self:  # Don't step ourselves
                    patch.step()
            
            # Get the input value
            self.getInputs()
            self.buffer[i] = self.input
    
    def play(self):
        """Start the audio stream."""
        if self.stream is not None and self.stream.active:
            print("Stream is already active.")
            return
        
        # Initialize the buffer with silence
        self.buffer = np.zeros(self.blocksize, dtype=np.float32)
        self.buffer_index = 0
        
        # Create and start the stream
        self.stream = sd.OutputStream(
            samplerate=self.board.sample_rate,
            channels=1,
            dtype=np.float32,
            callback=self.audio_callback,
            blocksize=self.blocksize
        )
        
        print("Starting audio stream...")
        self.stream.start()
    
    def stop(self):
        """Stop the audio stream."""
        if self.stream is not None:
            print("Stopping audio stream.")
            self.stream.stop()
            self.stream.close()
            self.stream = None
    
    def step(self):
        # AudioOutput doesn't need to do anything in step
        # The audio callback handles the stepping of other patches
        pass