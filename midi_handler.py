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
        self.mode = None

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

        self.knob_map = {
            1: "knob_browse",
            2: "knob_1",
            3: "knob_2",
            4: "knob_3",
        }

        self.cc_to_pad_map = {
            10: "pad_5_1",
            11: "pad_5_2",
            12: "pad_5_3",
            13: "pad_5_4",
            14: "pad_4_1",
            15: "pad_4_2",
            16: "pad_4_3",
            17: "pad_4_4",
            18: "pad_3_1",
            19: "pad_3_2",
            20: "pad_3_3",
            21: "pad_3_4",
            22: "pad_2_1",
            23: "pad_2_2",
            24: "pad_2_3",
            25: "pad_2_4",
            37: "pad_1_1",
            38: "pad_1_2",
            39: "pad_1_3",
            40: "pad_1_4",
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
        mode_detected = False
        for message in self.port:
            if not self.running:
                break
            if not mode_detected and message.type in ("note_on", "control_change"):
                self.mode = "traktor" if message.type == "note_on" else "midi"
                log.info(f"Detected F1 mode: {self.mode.upper()} mode")
                mode_detected = True
            self._process_message(message)

    def _process_message(self, message):
        if message.type == "note_on":
            if self.mode is None:
                self.mode = "traktor"
            note = message.note
            value = message.velocity
            channel = message.channel

            if note in self.note_map:
                self.callback("pad", self.note_map[note], value, channel)

        elif message.type == "control_change":
            if self.mode is None:
                self.mode = "midi"
            controller = message.control
            value = message.value
            channel = message.channel

            if controller in self.fader_map:
                self.callback("fader", self.fader_map[controller], value, channel)
            elif controller in self.knob_map:
                self.callback("knob", self.knob_map[controller], value, channel)
            elif controller in self.cc_to_pad_map:
                self.callback("pad", self.cc_to_pad_map[controller], value, channel)
            else:
                self.callback("cc", controller, value, channel)

        elif message.type == "pitch":
            pass

        elif message.type == "sysex":
            if self.led_controller:
                self.led_controller.handle_sysex(message.data)
