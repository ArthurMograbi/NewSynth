

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

