"""
LED control for Traktor Kontrol F1 pads

The F1 supports RGB LED control via SysEx messages.
This allows setting pad colors based on profile state.
"""

import logging
import struct
import mido

log = logging.getLogger("f1-deck.led")

F1_SYSEX_MANUFACTURER = [0x00, 0x20, 0xFF]
F1_SYSEX_DEVICE = 0x47
F1_SYSEX_LED_COMMAND = 0x14

RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
ORANGE = (255, 128, 0)
PURPLE = (128, 0, 255)
WHITE = (255, 255, 255)
OFF = (0, 0, 0)


class LEDController:
    def __init__(self):
        self.port = None
        self.profile = None
        self.current_colors = {}

    def set_port(self, port):
        self.port = port

    def set_profile(self, profile: dict):
        self.profile = profile

    def set_pad_color(self, pad_id: str, color: tuple):
        if not self.port:
            return

        self.current_colors[pad_id] = color

        pad_index = self._get_pad_index(pad_id)
        if pad_index is None:
            return

        msg = self._build_led_message(pad_index, color)

        try:
            self.port.send(msg)
        except Exception as e:
            log.error(f"Failed to set pad color: {e}")

    def _get_pad_index(self, pad_id: str) -> int:
        parts = pad_id.split("_")
        if len(parts) != 3 or parts[0] != "pad":
            return None

        row = int(parts[1]) - 1
        col = int(parts[2]) - 1

        return row * 4 + col

    def _build_led_message(self, pad_index: int, color: tuple) -> mido.Message:
        r, g, b = color

        sysex_data = F1_SYSEX_MANUFACTURER + [
            F1_SYSEX_DEVICE,
            F1_SYSEX_LED_COMMAND,
            pad_index,
            r,
            g,
            b,
            0x00,
        ]

        return mido.Message("sysex", data=sysex_data)

    def flash(self, pad_id: str, times: int = 1, color: tuple = None):
        if not color:
            color = self.current_colors.get(pad_id, OFF)

        for _ in range(times):
            self.set_pad_color(pad_id, color)
            import time

            time.sleep(0.1)
            self.set_pad_color(pad_id, OFF)
            time.sleep(0.1)

    def pulse(self, pad_id: str, duration: float = 1.0):
        import math
        import time

        steps = 20
        interval = duration / steps

        for i in range(steps):
            intensity = int((math.sin(i * math.pi / steps) * 0.5 + 0.5) * 255)
            color = tuple(c // 2 for c in self.current_colors.get(pad_id, RED))
            self.set_pad_color(pad_id, color)
            time.sleep(interval)

    def handle_sysex(self, data: bytes):
        pass

    def clear_all(self):
        for pad_id in self.current_colors:
            self.set_pad_color(pad_id, OFF)
        self.current_colors = {}

    def set_all(self, color: tuple):
        for row in range(1, 6):
            for col in range(1, 5):
                self.set_pad_color(f"pad_{row}_{col}", color)
