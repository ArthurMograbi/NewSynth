#patches/KeyboardInput.py
from .Patch import Patch
from pynput import keyboard
from collections import deque

class KeyboardInput(Patch):
    """Captures keyboard input and outputs note values based on keyboard layout."""

    _metadata = {
        "io": {
            "chromatic_layout": "out",
            "keyboard_layout": "out",
            "caps": "out",
            "shift": "out",
            "control": "out",
            "alt": "out"
        }
    }

    chromatic_order = "\\zxcvbnm,.;/asdfghjklç~]qwertyuiop´[1234567890"
    keyboard_order = "\\azsxcfvgbhnmk,l.;~/]q2we4r5ty7u8i9op"

    def __init__(self):
        super().__init__()
        self.chromatic_layout = 0.0
        self.keyboard_layout = 0.0
        self.caps = 0.0
        self.shift = 0.0
        self.control = 0.0
        self.alt = 0.0
        
        # Store pressed keys and caps lock state
        self.pressed_keys = set()
        self.key_queue = deque(maxlen=10)  # Keep last 10 keys
        self.caps_lock_active = False  # Track caps lock state
        
        # Setup keyboard listener
        self.listener = keyboard.Listener(
            on_press=self._on_press,
            on_release=self._on_release
        )
        self.listener.start()

    def _on_press(self, key):
        try:
            # Get character representation of the key
            if hasattr(key, 'char') and key.char:
                char = key.char
                self.pressed_keys.add(char)
                self.key_queue.append(char)
            else:
                # Handle special keys
                if key == keyboard.Key.caps_lock:
                    # Toggle caps lock state
                    self.caps_lock_active = not self.caps_lock_active
                    self.caps = 1.0 if self.caps_lock_active else 0.0
                elif key == keyboard.Key.shift or key == keyboard.Key.shift_r:
                    self.shift = 1.0
                elif key == keyboard.Key.ctrl or key == keyboard.Key.ctrl_r:
                    self.control = 1.0
                elif key == keyboard.Key.alt or key == keyboard.Key.alt_gr:
                    self.alt = 1.0
        except:
            pass

    def _on_release(self, key):
        try:
            if hasattr(key, 'char') and key.char:
                char = key.char
                if char in self.pressed_keys:
                    self.pressed_keys.remove(char)
            else:
                # Handle special keys (except caps lock which is a toggle)
                if key == keyboard.Key.shift or key == keyboard.Key.shift_r:
                    self.shift = 0.0
                elif key == keyboard.Key.ctrl_l or key == keyboard.Key.ctrl_r:
                    self.control = 0.0
                elif key == keyboard.Key.alt_l or key == keyboard.Key.alt_gr:
                    self.alt = 0.0
        except:
            pass

    def step(self):
        self.getInputs()
        
        # Reset outputs if no keys are currently pressed
        if not self.pressed_keys:
            self.chromatic_layout = 0.0
            self.keyboard_layout = 0.0
        else:
            # Get the most recent key press that is still pressed
            current_key = None
            for key in reversed(self.key_queue):
                if key in self.pressed_keys:
                    current_key = key
                    break
            
            # Handle chromatic layout
            if current_key and current_key in self.chromatic_order:
                self.chromatic_layout = self.chromatic_order.index(current_key) + 1
            else:
                self.chromatic_layout = 0.0
            
            # Handle keyboard layout
            if current_key and current_key in self.keyboard_order:
                self.keyboard_layout = self.keyboard_order.index(current_key) + 1
            else:
                self.keyboard_layout = 0.0

        self.time += 1

    def __del__(self):
        """Clean up listener when patch is destroyed."""
        if hasattr(self, 'listener'):
            self.listener.stop()