#patches/Scope.py
import numpy as np
from .VisualPatch import VisualPatch
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

class Scope(VisualPatch):
    """A scope that visualizes input signals"""
    
    _metadata = {
        "io": {
            "x": "in",
            "y": "in",
            "buffer_size":"in"
        }
    }

    def __init__(self, x:float=0.0, y:float=0.0, buffer_size:int=1024):
        super().__init__()
        self.x = x
        self.y = y
        self.buffer_size = buffer_size
        self.buffer_x = np.zeros(buffer_size)
        self.buffer_y = np.zeros(buffer_size)
        self.buffer_index = 0
        self.filled = False
        
        # Create the visual element (matplotlib figure)
        self.fig = Figure(figsize=(5, 3))
        self.canvas = FigureCanvas(self.fig)
        self.ax = self.fig.add_subplot(111)
        self.line, = self.ax.plot(self.buffer_x, self.buffer_y)
        self.ax.set_ylim(-1, 1)
        self.ax.set_xlim(0, buffer_size)
        self.fig.tight_layout()
        
        self.visual_element = self.canvas
    
    def step(self):
        # Set x to time if not connected
        if 'x' not in self.inputs:
            self.x = self.time
            
        self.getInputs()
        
        # Add new data to buffer
        self.buffer_x[self.buffer_index] = self.x
        self.buffer_y[self.buffer_index] = self.y
        
        # Update buffer index
        self.buffer_index = (self.buffer_index + 1) % self.buffer_size
        if self.buffer_index == 0:
            self.filled = True
            
        # Update the plot periodically for performance
        if self.time % 64 == 0:  # Update every 64 samples
            self.update_plot()
            
        self.time += 1
    
    def update_plot(self):
        """Update the scope display"""
        if self.filled:
            x_data = np.concatenate((self.buffer_x[self.buffer_index:], 
                                    self.buffer_x[:self.buffer_index]))
            y_data = np.concatenate((self.buffer_y[self.buffer_index:], 
                                    self.buffer_y[:self.buffer_index]))
        else:
            x_data = self.buffer_x[:self.buffer_index]
            y_data = self.buffer_y[:self.buffer_index]
            
        self.line.set_data(np.arange(len(y_data)), y_data)
        
        # Auto-scale y axis
        if len(y_data) > 0:
            y_min, y_max = np.min(y_data), np.max(y_data)
            margin = (y_max - y_min) * 0.1 if y_max != y_min else 0.1
            self.ax.set_ylim(y_min - margin, y_max + margin)
            
        self.canvas.draw_idle()  # Efficient update