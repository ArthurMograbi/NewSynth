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

    def jsonify(self):
        """Convert the board and all its patches to a JSON-serializable format"""
        # Create a mapping of patches to their IDs for connection references
        patch_ids = {patch: idx for idx, patch in enumerate(self.patches)}
        
        # Serialize all patches
        serialized_patches = []
        for patch in self.patches:
            patch_data = patch.jsonify(patch_ids)
            serialized_patches.append(patch_data)
        
        # Serialize the board itself
        return {
            "sample_rate": self.sample_rate,
            "blocksize": self.blocksize,
            "patches": serialized_patches
        }
    
    def save_to_file(self, filename):
        """Save the board configuration to a JSON file"""
        with open(filename, 'w') as f:
            json.dump(self.jsonify(), f, indent=2)
    
    @classmethod
    def load_from_file(cls, filename):
        """Load a board configuration from a JSON file"""
        with open(filename, 'r') as f:
            data = json.load(f)
        
        # Create patches first
        patches = []
        patch_instances = []
        
        for patch_data in data["patches"]:
            # Import the patch class
            module = __import__('patches', fromlist=[patch_data["type"]])
            patch_class = getattr(module, patch_data["type"])
            
            # Create instance with parameters
            params = patch_data.get("params", {})
            patch = patch_class(**params)
            patches.append(patch)
            patch_instances.append(patch)
        
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
        
        return board