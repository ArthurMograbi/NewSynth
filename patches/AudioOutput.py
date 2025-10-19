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
    
    def __init__(self, input:float=0.0, blocksize:int=1024,log_time:bool=True,log_interval:float=1.0):
        super().__init__()
        self.input = input
        self.stream = None
        self.blocksize = blocksize
        self.buffer = np.zeros(blocksize, dtype=np.float32)
        self.buffer_index = 0
        self.log_time = log_time
        self.log_interval = log_interval
        self.last_log = 0.0
        self.num_callbacks = 0

    def audio_callback(self, outdata, frames, time, status):
        if self.log_time and (time.currentTime - self.last_log) >= self.log_interval:
            print(self.num_callbacks / (time.currentTime - self.last_log))
            self.last_log = time.currentTime
            self.num_callbacks = 0
        self.num_callbacks += 1
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
        # Always stop existing stream first to ensure clean state
        if self.stream is not None:
            try:
                self.stream.stop()
                self.stream.close()
            except:
                pass
            self.stream = None
        
        # Initialize the buffer with silence
        self.buffer = np.zeros(self.blocksize, dtype=np.float32)
        self.buffer_index = 0
        
        # Create and start the stream
        try:
            self.stream = sd.OutputStream(
                samplerate=self.board.sample_rate,
                channels=1,
                dtype=np.float32,
                callback=self.audio_callback,
                blocksize=self.blocksize
            )
            
            print("Starting audio stream...")
            self.stream.start()
        except Exception as e:
            print(f"Error starting audio stream: {e}")
            self.stream = None
    
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