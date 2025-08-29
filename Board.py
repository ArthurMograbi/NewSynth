from Patch import Patch
from typing import List

class Board:

    def __init__(self,patches:List=[]):
        self.patches=patches

    def play(self):
        for patch in self.patches:
            if hasattr(patch,"play") and callable(getattr(patch,"play")):
                patch.play()

    def stop(self):
        for patch in self.patches:
            if hasattr(patch,"stop") and callable(getattr(patch,"stop")):
                patch.stop()
        
