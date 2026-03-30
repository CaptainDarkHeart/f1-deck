#!/usr/bin/env python3
"""
F1-Deck - Traktor Kontrol F1 as a Stream Deck replacement
"""

import sys
import signal
import logging
from pathlib import Path

from midi_handler import F1MidiHandler
from action_system import ActionSystem
from config import ConfigManager
from led_control import LEDController

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
log = logging.getLogger("f1-deck")


class F1Deck:
    def __init__(self, config_path: str = None):
        self.config_path_arg = config_path
        self.config_manager = ConfigManager(config_path)
        self.action_system = ActionSystem()
        self.led_controller = LEDController()
        self.midi_handler = None
        self.running = False

    def start(self):
        log.info("Starting F1-Deck...")

        if self.config_path_arg is None:
            profile_dir = Path(__file__).parent / "profiles"
            default_profile = profile_dir / "default.json"
            if default_profile.exists():
                self.config_manager.config_path = default_profile
                self.config_manager.config = self.config_manager._load_config()

        profile = self.config_manager.get_active_profile()
        log.info(f"Loaded profile: {profile['name']}")

        self.midi_handler = F1MidiHandler(
            callback=self.on_midi_event, led_controller=self.led_controller
        )

        if not self.midi_handler.connect():
            log.error("Failed to connect to F1. Is it connected?")
            sys.exit(1)

        self.led_controller.set_profile(profile)
        self.midi_handler.start()
        self.running = True

        log.info("F1-Deck running. Press Ctrl+C to stop.")

    def on_midi_event(self, event_type, note, value, channel=None):
        profile = self.config_manager.get_active_profile()

        for mapping in profile.get("mappings", []):
            if mapping["trigger"] == "pad_press" and mapping["note"] == note:
                self.action_system.execute(mapping["action"])
                return

            if mapping["trigger"] == "fader" and mapping["note"] == note:
                normalized = value / 127.0
                self.action_system.execute(mapping["action"], value=normalized)
                return

    def stop(self):
        log.info("Stopping F1-Deck...")
        self.running = False
        if self.midi_handler:
            self.midi_handler.stop()
        log.info("F1-Deck stopped.")

    def run(self):
        signal.signal(signal.SIGINT, lambda s, f: self.stop())
        signal.signal(signal.SIGTERM, lambda s, f: self.stop())
        self.start()

        try:
            while self.running:
                signal.pause()
        except AttributeError:
            import time

            while self.running:
                time.sleep(0.1)


def main():
    import argparse

    parser = argparse.ArgumentParser(description="F1-Deck - F1 as Stream Deck")
    parser.add_argument("--config", "-c", help="Path to config file")
    parser.add_argument(
        "--list-ports", action="store_true", help="List available MIDI ports"
    )
    args = parser.parse_args()

    if args.list_ports:
        from midi_handler import F1MidiHandler

        F1MidiHandler.list_ports()
        return

    app = F1Deck(config_path=args.config)
    app.run()


if __name__ == "__main__":
    main()
