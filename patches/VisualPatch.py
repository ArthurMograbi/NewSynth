#patches/VisualPatch.py
from .Patch import Patch

class VisualPatch(Patch):
    """Base class for patches with visual elements"""
    
    def __init__(self):
        super().__init__()
        self.visual_element = None
        
    def get_visual_element(self):
        """Return the visual element for this patch"""
        return self.visual_element