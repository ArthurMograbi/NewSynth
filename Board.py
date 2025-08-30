#Board.py
from patches import Patch
from typing import List

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
        
    def handle_key(self, key: str):
        if key == 's':
            self.play()
        elif key == 'e':
            self.stop()