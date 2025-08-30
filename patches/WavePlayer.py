#patches/WavePlayer.py
from .Patch import Patch
from .waveforms import Waveform

class WavePlayer(Patch):

    _metadata = {
        "io": {
            "input":"in",
            "play_progress":"in",
            "output":"out"
        },
        "waveio":{
            "wave":"in"
        }
    }

    def __init__(self,wave:Waveform|None=None):
        super().__init__()
        self.wave = wave
        self.play_progress = 0
        self.input =0.0
        self.output = 0.0
        self.playing = False


    def step(self):
        self.getInputs()
        if self.input > 0.0:
            self.playing=True
        if self.playing:
            self.output = self.wave[abs(self.play_progress)]
            #print(self.play_progress,self.output,len(self.wave))
            self.play_progress+=1
            if self.play_progress > len(self.wave):
                self.output=0.0
                self.playing=False
                self.play_progress = 0
        self.time+=1