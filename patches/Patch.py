#patches/Patch.py
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

    def jsonify(self, patch_ids=None, position=None):
        """Convert the patch to a JSON-serializable format"""
        # Get all parameters that are not connected
        params = {}
        metadata = getattr(self, '_metadata', {})
        
        # Collect regular IO parameters
        io_data = metadata.get('io', {})
        for param_name, io_type in io_data.items():
            if io_type == "in" and param_name not in self.inputs:
                # Only save parameters that are not connected
                if hasattr(self, param_name):
                    value = getattr(self, param_name)
                    # Convert to JSON-serializable types
                    if isinstance(value, (int, float, str, bool, type(None))):
                        params[param_name] = value
        
        # Collect wave IO parameters
        waveio_data = metadata.get('waveio', {})
        for param_name, io_type in waveio_data.items():
            if io_type == "in" and param_name not in self.inputs:
                # Only save parameters that are not connected
                if hasattr(self, param_name):
                    value = getattr(self, param_name)
                    # For waveforms, we need special handling
                    if hasattr(value, 'jsonify'):
                        params[param_name] = value.jsonify()
        
        # Collect connections
        connections = {}
        if patch_ids is not None:
            for input_name, source_patch in self.inputs.items():
                if source_patch in patch_ids:
                    source_output = source_patch.outputs.get(self, "")
                    connections[input_name] = {
                        "source_index": patch_ids[source_patch],
                        "source_output": source_output
                    }
        
        result = {
            "type": self.__class__.__name__,
            "params": params,
            "connections": connections
        }
        
        # Add position if provided
        if position is not None:
            result["position"] = position
            
        return result