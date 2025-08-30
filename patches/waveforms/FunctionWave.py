from .Waveform import Waveform

class FunctionWave(Waveform):

    def __init__(self,func, duration:float = 1.0, sample_rate:int = 22050):
        super().__init__(duration, sample_rate)
        self.func = func

    def getSample(self, normTime):
        return self.func(normTime)