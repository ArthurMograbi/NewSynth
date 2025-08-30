from pynput import mouse
from typing import Dict
from .Patch import Patch

class MouseData(Patch):
    """Outputs mouse X, Y positions and scroll delta as properties."""

    _metadata = {
        "io": {
            "mouseX": "out",
            "mouseY": "out",
            "mouseScroll": "out"  # Added scroll output
        }
    }

    def __init__(self, scaleX: float = 0.25, scaleY: float = 0.0005, scaleScroll: float = 0.25,scrollFalloff:float=0.00005,scrollLimit:float=1.0):
        super().__init__()
        self.mouseX = 0.0
        self.mouseY = 0.0
        self.mouseScroll = 0.0  # New scroll property
        self.scaleX = scaleX
        self.scaleY = scaleY
        self.scaleScroll = scaleScroll
        self.scrollFalloff = scrollFalloff
        self.scrollLimit = scrollLimit
        # Thread-safe value storage
        self._current_pos = (0, 0)
        self._scroll_delta = 0.0
        
        # Setup mouse listener
        self.listener = mouse.Listener(
            on_move=self._on_move,
            on_scroll=self._on_scroll
        )
        self.listener.start()

    def _on_move(self, x, y):
        self._current_pos = (x, y)

    def _on_scroll(self, x, y, dx, dy):
        #print(dy)
        self._scroll_delta += dy
        

    def step(self):
        # Get current values
        x, y = self._current_pos
        
        
        
        # Apply scaling and update outputs
        self.mouseX = float(x) * self.scaleX
        self.mouseY = float(y) * self.scaleY
        self.mouseScroll += abs(self._scroll_delta) * self.scaleScroll-self.scrollFalloff
        self.mouseScroll=min(max(self.mouseScroll,0.0),self.scrollLimit)
        #print(self.mouseScroll)
        self._scroll_delta=0.0
        self.time += 1


    def __del__(self):
        """Clean up listener when patch is destroyed."""
        if hasattr(self, 'listener'):
            self.listener.stop()