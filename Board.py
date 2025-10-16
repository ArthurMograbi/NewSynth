#Board.py
from patches import Patch
from typing import List
import json

class Board:
    sample_rate=22050
    blocksize=1024

    def __init__(self,patches:List=[]):
        self.patches=[]
        for patch in patches: self.add_patch(patch)

    def play(self):
        for patch in self.patches:
            if hasattr(patch,"play") and callable(getattr(patch,"play")):
                patch.play()

    def stop(self):
        for patch in self.patches:
            if hasattr(patch,"stop") and callable(getattr(patch,"stop")):
                patch.stop()

    def add_patch(self,patch:Patch):
        self.patches.append(patch)
        patch.board=self

    def remove_patch(self,patch:Patch):
        self.patches.remove(patch)
        
    def handle_key(self, key: str):
        if key == 's':
            self.play()
        elif key == 'e':
            self.stop()

    def jsonify(self, patch_positions=None, waveform_positions=None):
        """Convert the board and all its patches to a JSON-serializable format"""
        # Create a mapping of patches to their IDs for connection references
        patch_ids = {patch: idx for idx, patch in enumerate(self.patches)}
        
        # Serialize all patches
        serialized_patches = []
        for idx, patch in enumerate(self.patches):
            # Get position for this patch if available
            position = patch_positions.get(patch) if patch_positions else None
            patch_data = patch.jsonify(patch_ids, position)
            serialized_patches.append(patch_data)
        
        # Serialize the board itself
        result = {
            "sample_rate": self.sample_rate,
            "blocksize": self.blocksize,
            "patches": serialized_patches
        }
        
        # Add waveform positions if provided
        if waveform_positions:
            result["waveform_positions"] = waveform_positions
            
        return result
    
    def save_to_file(self, filename, patch_positions=None, waveform_positions=None):
        """Save the board configuration to a JSON file"""
        with open(filename, 'w') as f:
            json.dump(self.jsonify(patch_positions, waveform_positions), f, indent=2)
    
    @classmethod
    def load_from_file(cls, filename):
        """Load a board configuration from a JSON file"""
        with open(filename, 'r') as f:
            data = json.load(f)
        
        # Extract positions correctly - they're stored within each patch
        patch_positions = {}
        waveform_positions = data.get("waveform_positions", {})
        
        # Create patches first
        patches = []
        patch_instances = []
        
        for i, patch_data in enumerate(data["patches"]):
            # Import the patch class
            module = __import__('patches', fromlist=[patch_data["type"]])
            patch_class = getattr(module, patch_data["type"])
            
            # Create instance with parameters
            params = patch_data.get("params", {})
            
            # Handle waveform parameters specially
            for param_name, param_value in params.items():
                if isinstance(param_value, dict) and "type" in param_value:
                    # This is a waveform parameter
                    wave_module = __import__('patches.waveforms', fromlist=[param_value["type"]])
                    wave_class = getattr(wave_module, param_value["type"])
                    
                    if param_value["type"] == "FileWave":
                        # Make sure filename exists in the param_value
                        if "filename" in param_value:
                            params[param_name] = wave_class(param_value["filename"])
                        else:
                            print(f"Warning: FileWave missing filename, using default")
                            params[param_name] = wave_class("default.wav")  # or handle appropriately
                    elif param_value["type"] == "FunctionWave":
                        # Note: Function reconstruction from source is complex
                        # For now, we'll just create a default function
                        params[param_name] = wave_class(lambda x: x)
                    else:
                        params[param_name] = wave_class()
            
            patch = patch_class(**params)
            patches.append(patch)
            patch_instances.append(patch)
            
            # Store position for this patch
            if "position" in patch_data:
                patch_positions[patch] = tuple(patch_data["position"])
        
        # Create board
        board = cls(patches)
        board.sample_rate = data.get("sample_rate", cls.sample_rate)
        board.blocksize = data.get("blocksize", cls.blocksize)
        
        # Restore connections
        for i, patch_data in enumerate(data["patches"]):
            if "connections" in patch_data:
                for input_name, connection in patch_data["connections"].items():
                    source_patch = patch_instances[connection["source_index"]]
                    source_output = connection["source_output"]
                    
                    # Connect the patches
                    Patch.connect(patch_instances[i], source_patch, input_name, source_output)
        
        return board, patch_positions, waveform_positions