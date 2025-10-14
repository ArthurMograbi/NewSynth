# gui/PatchFactory.py
import importlib
import inspect
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel

class PatchFactory:
    """Factory for creating patches and their UI components"""
    
    @staticmethod
    def get_available_patches():
        """Get all available patch types"""
        patch_types = {}
        
        try:
            patches_module = importlib.import_module('patches')
            
            for name, obj in inspect.getmembers(patches_module):
                if (inspect.isclass(obj) and 
                    hasattr(obj, '_metadata') and 
                    issubclass(obj, patches_module.Patch) and 
                    obj != patches_module.Patch):
                    patch_types[name] = obj
                    
        except ImportError as e:
            print(f"Error discovering patch types: {e}")
            
        return patch_types
    
    @staticmethod
    def create_patch_ui(patch, parent=None):
        """Create a custom UI widget for a patch"""
        widget = QWidget(parent)
        layout = QVBoxLayout(widget)
        
        # Basic info
        info_label = QLabel(f"Type: {patch.__class__.__name__}")
        layout.addWidget(info_label)
        
        # Add parameter controls based on patch metadata
        metadata = getattr(patch, '_metadata', {})
        io_data = metadata.get('io', {})
        
        for param_name, io_type in io_data.items():
            if io_type == "in" and not hasattr(patch.inputs, param_name):
                # This is an input parameter that's not connected
                param_label = QLabel(f"{param_name}: {getattr(patch, param_name, 'N/A')}")
                layout.addWidget(param_label)
        
        return widget
    
    @staticmethod
    def create_patch(patch_class, **kwargs):
        """Create a new patch instance"""
        return patch_class(**kwargs)