#patches/AudioOutput
import sounddevice as sd
import numpy as np
from .Patch import Patch

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