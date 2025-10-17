from .VisualPatch import VisualPatch
import numpy as np
import math
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.patches import Circle

class BouncingBall(VisualPatch):

    _metadata = {
        "io": {
            "v0":"in",
            "acc":"in",
            "r0":"in",
            "racc":"in",
            "x":"out",
            "y":"out"
        }
    }

    def __init__(self, v0:float=0.0001, acc:float=0.0, r0:float=1.0, racc:float=0.0, radius:float=0.03):
        super().__init__()
        # motion parameters (can be connected as inputs)
        self.v0 = v0        # speed magnitude (normalized units per step)
        self.acc = acc      # change in speed per step
        self.r0 = r0        # angle in radians
        self.racc = racc    # change in angle per step (rotational velocity)
        # position outputs (normalized 0..1)
        self.x = 0.5
        self.y = 0.5

        # visual parameters
        self.radius = radius
        self.fig = Figure(figsize=(3, 3))
        self.canvas = FigureCanvas(self.fig)
        self.ax = self.fig.add_subplot(111)
        self.ax.set_xlim(0, 1)
        self.ax.set_ylim(0, 1)
        self.ax.set_aspect('equal')
        self.ax.axis('off')

        # create the ball patch
        self.ball = Circle((self.x, self.y), radius=self.radius, color='C0')
        self.ax.add_patch(self.ball)

        self.visual_element = self.canvas

    def step(self):
        # If inputs not connected, allow defaults; otherwise get values from connected patches
        self.getInputs()

        # update speed and angle from inputs
        self.v0 += self.acc
        self.r0 += self.racc

        # compute displacement
        dx = self.v0 * math.cos(self.r0)
        dy = self.v0 * math.sin(self.r0)

        self.x += dx
        self.y += dy

        # handle bouncing on vertical walls
        if self.x - self.radius <= 0:
            self.x = self.radius
            self.r0 = math.pi - self.r0
        elif self.x + self.radius >= 1:
            self.x = 1 - self.radius
            self.r0 = math.pi - self.r0

        # handle bouncing on horizontal walls
        if self.y - self.radius <= 0:
            self.y = self.radius
            self.r0 = -self.r0
        elif self.y + self.radius >= 1:
            self.y = 1 - self.radius
            self.r0 = -self.r0

        # normalize angle to avoid overflow
        self.r0 = (self.r0 + math.pi*2) % (math.pi*2)

        # update visual periodically for performance
        if self.time % 4 == 0:
            self.ball.center = (self.x, self.y)
            self.canvas.draw_idle()

        self.time += 1