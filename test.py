import sounddevice as sd
import numpy as np

class SineGenerator:
    """Generates sine wave samples with continuous phase tracking."""
    
    def __init__(self, frequency=440, amplitude=0.5, sample_rate=44100):
        """
        Initialize the sine wave generator.
        
        Args:
            frequency: Frequency of the sine wave in Hz (default: 440)
            amplitude: Amplitude of the sine wave (0.0 to 1.0, default: 0.5)
            sample_rate: Sample rate in Hz (default: 44100)
        """
        self.frequency = frequency
        self.amplitude = amplitude
        self.sample_rate = sample_rate
        self.phase = 0.0
        self.step = 2 * np.pi * frequency / sample_rate
    
    def generate(self, frames):
        """
        Generate a chunk of sine wave samples.
        
        Args:
            frames: Number of frames to generate
            
        Returns:
            numpy array of shape (frames, 1) containing the generated samples
        """
        # Generate sine wave for the requested number of frames
        t = self.phase + self.step * np.arange(frames)
        samples = self.amplitude * np.sin(t).reshape(-1, 1)
        
        # Update phase, keeping it within [0, 2π) to prevent precision loss
        self.phase = (self.phase + frames * self.step) % (2 * np.pi)
        
        return samples.astype(np.float32)
    
    def set_frequency(self, frequency):
        """Update the frequency of the sine wave."""
        self.frequency = frequency
        self.step = 2 * np.pi * frequency / self.sample_rate
    
    def set_amplitude(self, amplitude):
        """Update the amplitude of the sine wave."""
        self.amplitude = amplitude


class AudioOutput:
    """Handles audio output using a non-blocking stream."""
    
    def __init__(self, generator, sample_rate=44100, blocksize=1024):
        """
        Initialize the audio output.
        
        Args:
            generator: Instance of SineGenerator (or similar) that provides audio samples
            sample_rate: Sample rate in Hz (default: 44100)
            blocksize: Number of frames per block (default: 1024)
        """
        self.generator = generator
        self.sample_rate = sample_rate
        self.blocksize = blocksize
        self.stream = None
    
    def audio_callback(self, outdata, frames, time, status):
        """Callback function for the audio stream."""
        if status:
            print(f"Status: {status}")
        
        # Generate audio data and write to output buffer
        outdata[:] = self.generator.generate(frames)
    
    def start(self):
        """Start the audio stream."""
        if self.stream is not None and self.stream.active:
            print("Stream is already active.")
            return
        
        self.stream = sd.OutputStream(
            samplerate=self.sample_rate,
            channels=1,  # Mono audio
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


# Example usage
if __name__ == "__main__":
    # Create a sine wave generator
    sine_gen = SineGenerator(frequency=440, amplitude=0.3)
    
    # Create an audio output with the generator
    audio_out = AudioOutput(sine_gen, blocksize=512)
    
    try:
        # Start the audio stream
        audio_out.start()
        
        # Keep the program running until interrupted
        while True:
            sd.sleep(1000)
            
    except KeyboardInterrupt:
        print("\nInterrupted by user.")
    
    finally:
        # Ensure the stream is stopped
        audio_out.stop()