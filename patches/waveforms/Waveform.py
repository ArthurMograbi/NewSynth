from abc import ABC, abstractmethod

class Waveform(ABC):

    def __init__(self,duration:float=1.0,sample_rate:int=22050,blocksize:int = 1024):
        self.duration = duration
        self.sample_rate = sample_rate
        self.blocksize = blocksize

    @abstractmethod
    def getSample(self,normTime:float):
        pass

    def __getitem__(self,i):
        return self.getSample(i/len(self))
    
    def __len__(self):
        return int((self.sample_rate)*self.duration)