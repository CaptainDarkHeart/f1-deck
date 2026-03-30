"""
MIDI input handling for Traktor Kontrol F1
"""

import logging
import threading
import mido

log = logging.getLogger("f1-deck.midi")

NOTE_ON = 144
NOTE_OFF = 128
CC = 176


class F1MidiHandler:
    F1_PORT_NAME = "Traktor Kontrol F1"

    def __init__(self, callback, led_controller=None):
        self.callback = callback
        self.led_controller = led_controller
        self.port = None
        self.running = False
        self.thread = None

        self.note_map = {
            36: "pad_1_1",
            37: "pad_1_2",
            38: "pad_1_3",
            39: "pad_1_4",
            40: "pad_2_1",
            41: "pad_2_2",
            42: "pad_2_3",
            43: "pad_2_4",
            44: "pad_3_1",
            45: "pad_3_2",
            46: "pad_3_3",
            47: "pad_3_4",
            48: "pad_4_1",
            49: "pad_4_2",
            50: "pad_4_3",
            51: "pad_4_4",
            52: "pad_5_1",
            53: "pad_5_2",
            54: "pad_5_3",
            55: "pad_5_4",
        }

        self.fader_map = {
            12: "fader_1",
            13: "fader_2",
            14: "fader_3",
            15: "fader_4",
        }

    @staticmethod
    def list_ports():
        log.info("Available MIDI input ports:")
        for port in mido.get_input_names():
            log.info(f"  - {port}")
        if not mido.get_input_names():
            log.info("  (none found)")

    def connect(self) -> bool:
        ports = mido.get_input_names()

        for port_name in ports:
            if self.F1_PORT_NAME in port_name:
                try:
                    self.port = mido.open_input(port_name)
                    log.info(f"Connected to F1 on port: {port_name}")

                    if self.led_controller:
                        self.led_controller.set_port(self.port)

                    return True
                except Exception as e:
                    log.error(f"Failed to open port {port_name}: {e}")

        log.warning(f"F1 not found. Looking for: {self.F1_PORT_NAME}")
        log.info("Available ports:")
        for p in ports:
            log.info(f"  - {p}")
        return False

    def start(self):
        self.running = True
        self.thread = threading.Thread(target=self._read_loop, daemon=True)
        self.thread.start()

    def stop(self):
        self.running = False
        if self.port:
            self.port.close()

    def _read_loop(self):
        log.info("MIDI listener started")
        for message in self.port:
            if not self.running:
                break
            self._process_message(message)

    def _process_message(self, message):
        if message.type == "note_on":
            note = message.note
            value = message.velocity
            channel = message.channel

            if note in self.note_map:
                self.callback("pad", self.note_map[note], value, channel)

        elif message.type == "control_change":
            controller = message.control
            value = message.value
            channel = message.channel

            if controller in self.fader_map:
                self.callback("fader", self.fader_map[controller], value, channel)
            elif controller >= 10 and controller <= 55:
                row = (controller - 10) // 4
                col = (controller - 10) % 4
                pad_name = f"pad_{4 - row}_{col + 1}"
                self.callback("pad", pad_name, value, channel)

        elif message.type == "sysex":
            if self.led_controller:
                self.led_controller.handle_sysex(message.data)
