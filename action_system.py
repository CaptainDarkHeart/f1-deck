"""
Action system for executing mapped commands
"""

import logging
import subprocess
import webbrowser
from pathlib import Path

try:
    from pynput.keyboard import Key, Controller as KeyboardController
    from pynput.keyboard import HotKey
except ImportError:
    KeyboardController = None

try:
    import pyautogui
except ImportError:
    pyautogui = None

log = logging.getLogger("f1-deck.actions")


class ActionSystem:
    def __init__(self):
        self.keyboard = KeyboardController() if KeyboardController else None
        self.registered_hotkeys = {}

    def execute(self, action: dict, value: float = None):
        action_type = action.get("type")

        try:
            if action_type == "keyboard":
                self._execute_keyboard(action)
            elif action_type == "hotkey":
                self._execute_hotkey(action)
            elif action_type == "launch":
                self._execute_launch(action)
            elif action_type == "url":
                self._execute_url(action)
            elif action_type == "script":
                self._execute_script(action)
            elif action_type == "system":
                self._execute_system(action)
            elif action_type == "text":
                self._execute_text(action)
            elif action_type == "fader_callback":
                self._execute_fader_callback(action, value)
            else:
                log.warning(f"Unknown action type: {action_type}")
        except Exception as e:
            log.error(f"Failed to execute action {action_type}: {e}")

    def _execute_keyboard(self, action: dict):
        if not self.keyboard:
            log.error("pynput not installed")
            return

        keys = action.get("keys", [])
        log.info(f"Pressing keys: {keys}")

        with self.keyboard.pressed(Key.ctrl):
            for key in keys:
                self.keyboard.press(key)
                self.keyboard.release(key)

    def _execute_hotkey(self, action: dict):
        if not self.keyboard:
            log.error("pynput not installed")
            return

        combo = action.get("combo", [])
        log.info(f"Hotkey: {'+'.join(combo)}")

        with self.keyboard.pressed(Key[combo[0]]):
            for key in combo[1:]:
                self.keyboard.press(key)
                self.keyboard.release(key)

    def _execute_launch(self, action: dict):
        app = action.get("app", "")
        args = action.get("args", [])

        log.info(f"Launching: {app}")

        try:
            if Path(app).exists():
                subprocess.Popen([app] + args)
            else:
                subprocess.Popen(["open", "-a", app] + args)
        except Exception as e:
            log.error(f"Failed to launch {app}: {e}")

    def _execute_url(self, action: dict):
        url = action.get("url", "")
        log.info(f"Opening URL: {url}")
        webbrowser.open(url)

    def _execute_script(self, action: dict):
        script = action.get("script", "")
        shell = action.get("shell", "/bin/bash")

        log.info(f"Running script: {script[:50]}...")

        try:
            subprocess.run(script, shell=True, executable=shell, check=True)
        except subprocess.CalledProcessError as e:
            log.error(f"Script failed: {e}")

    def _execute_system(self, action: dict):
        command = action.get("command", "")
        log.info(f"System command: {command}")

        if command == "volume_up":
            self._volume_up()
        elif command == "volume_down":
            self._volume_down()
        elif command == "mute":
            self._mute()
        elif command == "brightness_up":
            self._brightness_up()
        elif command == "brightness_down":
            self._brightness_down()
        elif command == "screenshot":
            self._screenshot()
        else:
            log.warning(f"Unknown system command: {command}")

    def _execute_text(self, action: dict):
        if not pyautogui:
            log.error("pyautogui not installed")
            return

        text = action.get("text", "")
        log.info(f"Typing text: {text[:20]}...")
        pyautogui.typewrite(text, interval=0.01)

    def _execute_fader_callback(self, action: dict, value: float):
        if value is None:
            return

        callback_type = action.get("callback_type", "")

        if callback_type == "keyboard_slider":
            self._keyboard_slider(action, value)
        elif callback_type == "brightness":
            self._set_brightness(value)
        elif callback_type == "volume":
            self._set_volume(value)

    def _volume_up(self):
        if pyautogui:
            for _ in range(5):
                pyautogui.press("volumeup")

    def _volume_down(self):
        if pyautogui:
            for _ in range(5):
                pyautogui.press("volumedown")

    def _mute(self):
        if pyautogui:
            pyautogui.press("volumemute")

    def _brightness_up(self):
        log.info("Brightness up")

    def _brightness_down(self):
        log.info("Brightness down")

    def _screenshot(self):
        if pyautogui:
            pyautogui.screenshot()

    def _keyboard_slider(self, action: dict, value: float):
        keys = action.get("keys", [])
        key_count = len(keys)

        if key_count == 0:
            return

        index = min(int(value * key_count), key_count - 1)

        if self.keyboard:
            with self.keyboard.pressed(Key.ctrl):
                self.keyboard.press(keys[index])
                self.keyboard.release(keys[index])

    def _set_brightness(self, value: float):
        log.info(f"Set brightness to {value * 100:.0f}%")

    def _set_volume(self, value: float):
        log.info(f"Set volume to {value * 100:.0f}%")
