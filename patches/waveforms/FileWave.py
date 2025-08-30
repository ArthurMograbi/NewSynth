import librosa
import numpy as np
from .Waveform import Waveform

class FileWave(Waveform):
    def __init__(self, filename: str, sample_rate: int = 22050):
        # Load audio file using librosa
        y, sr = librosa.load(filename, sr=sample_rate, mono=True)
        
        # Calculate duration based on loaded audio
        duration = len(y) / sr
        print(duration)
        # Initialize the Waveform with the correct duration and sample rate
        super().__init__(duration=duration, sample_rate=sr)
        
        # Store the normalized audio data
        self.audio_data = y.astype(np.float32)
        
    def getSample(self, normTime: float):
        # Clamp normalized time between 0 and 1
        normTime = max(0.0, min(1.0, normTime))
        
        # Calculate the exact index in the audio data
        exact_index = normTime * (len(self.audio_data) - 1)
        
        # Get the integer part and fractional part for interpolation
        index = int(exact_index)
        frac = exact_index - index
        
        # Linear interpolation between samples
        if index < len(self.audio_data) - 1:
            return (1 - frac) * self.audio_data[index] + frac * self.audio_data[index + 1]
        else:
            return self.audio_data[index]