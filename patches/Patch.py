#patches/Patch.py
from typing import Dict, List
from abc import ABC, abstractmethod

# Modified Patch class to support audio streaming
class Patch(ABC):
    _metadata = {}
    
    # Cached metadata keys for fast access (populated by __init_subclass__)
    _io_inputs = ()        # Tuple of input parameter names from "io"
    _io_outputs = ()       # Tuple of output parameter names from "io"
    _waveio_inputs = ()    # Tuple of input parameter names from "waveio"
    _waveio_outputs = ()   # Tuple of output parameter names from "waveio"
    
    def __init_subclass__(cls, **kwargs):
        """Automatically initialize metadata cache when a patch class is defined"""
        super().__init_subclass__(**kwargs)
        cls._init_metadata_cache()
    
    @classmethod
    def _init_metadata_cache(cls):
        """Cache metadata keys as tuples for O(1) lookup performance"""
        metadata = cls._metadata or {}
        io = metadata.get('io', {})
        waveio = metadata.get('waveio', {})
        
        cls._io_inputs = tuple(k for k, v in io.items() if v == "in")
        cls._io_outputs = tuple(k for k, v in io.items() if v == "out")
        cls._waveio_inputs = tuple(k for k, v in waveio.items() if v == "in")
        cls._waveio_outputs = tuple(k for k, v in waveio.items() if v == "out")

    
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
        # Use cached metadata for fast validation (O(1) tuple membership test vs dict lookup)
        if propIn in patchIn._io_inputs and propOut in patchOut._io_outputs:
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
        
        # Collect regular IO parameters using cached input keys
        for param_name in self._io_inputs:
            if param_name not in self.inputs:
                # Only save parameters that are not connected
                if hasattr(self, param_name):
                    value = getattr(self, param_name)
                    # Convert to JSON-serializable types
                    if isinstance(value, (int, float, str, bool, type(None))):
                        params[param_name] = value
        
        # Collect wave IO parameters using cached waveform input keys
        for param_name in self._waveio_inputs:
            if param_name not in self.inputs:
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


# Initialize cache for the base Patch class itself (since it's not a subclass, __init_subclass__ won't be called)
Patch._init_metadata_cache()