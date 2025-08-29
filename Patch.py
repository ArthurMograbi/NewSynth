from typing import List, Dict
from abc import ABC, abstractmethod
from __future__ import annotations


class Patch(ABC):
    _metadata = {}

    def __init__(self,inputs:Dict[str,Patch]= {},outputs:Dict[Patch,str] = {}):
        self.inputs = inputs
        self.outputs = outputs
        self.time = 0

    def getInputs(self):
        for k, v in self.inputs.items():
            setattr(self,k,v.getOutput(self))
    
    def getOutput(self,patch:Patch):
        while self.time<patch.time:
            self.step()
        return getattr(self,self.outputs[patch])
    
    def connect(self,patchIn:Patch,patchOut:Patch,propIn:str,propOut:str):
        if patchIn._metadata["io"][propIn]=="in" and patchOut._metadata["io"][propOut]=="out":
            patchIn.inputs[propIn]=patchIn
            patchOut.outputs[patchOut]=propIn
        else:
            raise UserWarning("Tried to connect input to input")

    @abstractmethod
    def step(self):
        pass

