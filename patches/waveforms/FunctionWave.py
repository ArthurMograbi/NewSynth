#patches/waveforms/FunctionWave.py
from .Waveform import Waveform
import inspect

class FunctionWave(Waveform):

    def __init__(self,func, duration:float = 1.0, sample_rate:int = 22050):
        super().__init__(duration, sample_rate)
        self.func = func
        # Store the function source code if possible
        try:
            self.func_source = inspect.getsource(func)
        except:
            self.func_source = None

    def getSample(self, normTime):
        return self.func(normTime)
    
    def jsonify(self, position=None):
        """Convert the FunctionWave to a JSON-serializable format"""
        data = super().jsonify(position)
        data["func_source"] = self.func_source
        return data