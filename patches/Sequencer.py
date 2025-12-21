#patches/Sequencer.py
from typing import List
from .VisualPatch import VisualPatch
from PyQt5.QtWidgets import QWidget, QGridLayout, QDoubleSpinBox, QLabel, QScrollArea, QSizePolicy
from PyQt5.QtCore import Qt


class Sequencer(VisualPatch):
    """4-track, 8-step sequencer VisualPatch.

    Inputs:
      - clock: stepping input (rising edge when > 0.1)

    Outputs:
      - out1, out2, out3, out4: numeric values for each track at current step
    """

    _metadata = {
        "io": {
            "clock": "in",
            "out1": "out",
            "out2": "out",
            "out3": "out",
            "out4": "out"
        }
    }

    TRACKS = 4
    STEPS_PER_TRACK = 8

    def __init__(self, steps: List[List[float]] | None = None, current_step: int = 0):
        super().__init__()

        # Normalize steps shape to TRACKS x STEPS_PER_TRACK
        if steps is None:
            self.steps = [[0.0 for _ in range(self.STEPS_PER_TRACK)] for _ in range(self.TRACKS)]
        else:
            # ensure proper dimensions (pad/truncate as needed)
            self.steps = []
            for t in range(self.TRACKS):
                if t < len(steps) and isinstance(steps[t], list):
                    row = list(steps[t])[: self.STEPS_PER_TRACK]
                    # pad
                    while len(row) < self.STEPS_PER_TRACK:
                        row.append(0.0)
                    self.steps.append([float(x) for x in row])
                else:
                    self.steps.append([0.0 for _ in range(self.STEPS_PER_TRACK)])

        # Runtime state
        self.current_step = int(current_step) % self.STEPS_PER_TRACK
        self.prev_clock = 0.0

        # Initialize outputs from current step
        for i in range(self.TRACKS):
            setattr(self, f"out{i+1}", float(self.steps[i][self.current_step]))

        # Build the visual widget: inner grid of spinboxes wrapped in a scroll area
        inner = QWidget()
        inner_layout = QGridLayout()
        inner_layout.setSpacing(4)
        inner_layout.setContentsMargins(4, 4, 4, 4)
        inner.setLayout(inner_layout)

        # Header: step numbers
        inner_layout.addWidget(QLabel(""), 0, 0)
        for s in range(self.STEPS_PER_TRACK):
            lbl = QLabel(str(s + 1))
            lbl.setAlignment(Qt.AlignCenter)
            inner_layout.addWidget(lbl, 0, s + 1)

        for t in range(self.TRACKS):
            inner_layout.addWidget(QLabel(f"T{t+1}"), t + 1, 0)
            for s in range(self.STEPS_PER_TRACK):
                sb = QDoubleSpinBox()
                sb.setRange(-9999.0, 9999.0)
                sb.setDecimals(4)
                sb.setSingleStep(0.01)
                sb.setValue(self.steps[t][s])
                sb.setMaximumWidth(72)
                sb.setMinimumWidth(48)
                sb.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

                # capture loop variables with defaults
                def make_handler(track, step_index):
                    def handler(value):
                        self.steps[track][step_index] = float(value)
                    return handler

                sb.valueChanged.connect(make_handler(t, s))
                inner_layout.addWidget(sb, t + 1, s + 1)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(inner)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll.setMaximumHeight(180)

        self.visual_element = scroll

    def step(self):
        # Pull connected inputs into attributes
        self.getInputs()

        clk = getattr(self, "clock", 0.0)

        # Rising-edge detection: threshold 0.1
        if clk > 0.1 and self.prev_clock <= 0.1:
            self.current_step = (self.current_step + 1) % self.STEPS_PER_TRACK
            for i in range(self.TRACKS):
                setattr(self, f"out{i+1}", float(self.steps[i][self.current_step]))

        self.prev_clock = clk
        self.time += 1

    def jsonify(self, patch_ids=None, position=None):
        # Use base jsonify then add sequencer-specific params
        result = super().jsonify(patch_ids, position)
        # Ensure params dict exists
        params = result.get("params", {})
        params["steps"] = self.steps
        params["current_step"] = int(self.current_step)
        result["params"] = params
        return result
