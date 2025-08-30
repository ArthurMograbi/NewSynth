import pyautogui
from .Patch import Patch

class MouseData(Patch):
    """Outputs mouse X and Y positions as properties."""

    _metadata = {
        "io": {
            "mouseX":"out",
            "mouseY":"out"
        }
    }

    def __init__(self,scaleX:float=0.25,scaleY:float=0.0005):
        super().__init__()
        self.mouseX = 0.0
        self.mouseY = 0.0
        self.scaleX = scaleX
        self.scaleY = scaleY

    def step(self):
        x, y = pyautogui.position()
        self.mouseX = float(x)*self.scaleX
        self.mouseY = float(y)*self.scaleY
        #print(self.mouseX,self.mouseY)
        self.time+=1