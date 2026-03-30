# F1-Deck

Turn your **Traktor Kontrol F1** into a Stream Deck replacement for macOS/Linux.

```
F1 → USB → f1-deck → keyboard shortcuts, app launch, URLs, scripts...
```

## Features

- **20 RGB pads** with color feedback
- **4 faders** for smooth analog control
- **Profile switching** — create custom layouts for streaming, working, gaming
- **Action types:**
  - Keyboard shortcuts & hotkeys
  - App launching
  - URL opening
  - Shell scripts
  - Text expansion
  - System controls (volume, brightness, screenshot)
  - Fader → continuous actions

## Requirements

- Python 3.8+
- Traktor Kontrol F1
- macOS or Linux

## Quick Start

```bash
cd f1-deck
pip install -r requirements.txt

# List available MIDI ports
python main.py --list-ports

# Run
python main.py

# Edit configuration
python ui.py
```

## Configuration

Profiles are stored in `profiles/` as JSON files. Example:

```json
{
  "name": "default",
  "mappings": [
    {
      "trigger": "pad",
      "note": "pad_4_1",
      "action": {
        "type": "keyboard",
        "keys": ["1"]
      },
      "color": [255, 0, 0]
    },
    {
      "trigger": "fader",
      "note": "fader_1",
      "action": {
        "type": "fader_callback",
        "callback_type": "volume"
      }
    }
  ]
}
```

### Action Types

| Type | Config |
|------|--------|
| `keyboard` | `{"keys": ["a", "b"]}` |
| `hotkey` | `{"combo": ["ctrl", "shift", "m"]}` |
| `launch` | `{"app": "/Applications/OBS.app"}` |
| `url` | `{"url": "https://github.com"}` |
| `script` | `{"script": "echo hello"}` |
| `system` | `{"command": "volume_up"}` |
| `text` | `{"text": "your email@domain.com"}` |
| `fader_callback` | `{"callback_type": "volume"}` |

## Pad Names

Rows from bottom to top: `pad_4_1` through `pad_5_4`

```
pad_5_1  pad_5_2  pad_5_3  pad_5_4   (top row)
pad_4_1  pad_4_2  pad_4_3  pad_4_4
pad_3_1  pad_3_2  pad_3_3  pad_3_4
pad_2_1  pad_2_2  pad_2_3  pad_2_4
pad_1_1  pad_1_2  pad_1_3  pad_1_4   (bottom row)
```

## Auto-Start (macOS)

### Install LaunchAgent

```bash
./install-launchagent.sh
```

This installs `com.f1deck.app.plist` which starts f1-deck automatically on login and restarts it if it crashes.

**Commands:**
```bash
launchctl list | grep f1deck     # Check status
launchctl stop com.f1deck.app    # Stop
launchctl start com.f1deck.app    # Start
tail -f /tmp/f1-deck.log         # View logs
```

**Uninstall:**
```bash
launchctl unload ~/Library/LaunchAgents/com.f1deck.app.plist
rm ~/Library/LaunchAgents/com.f1deck.app.plist
rm ~/Library/LaunchAgents/com.f1deck.ui.plist
```

### macOS MIDI Mode

On macOS, you need to enable MIDI mode on the F1:

1. Hold **Shift** and press **Browse**
2. The F1 will beep and enter MIDI mode
3. The port name changes to `Traktor Kontrol F1 - 1 Input`

## Architecture

```
main.py          - Entry point, orchestrates components
midi_handler.py  - Raw MIDI input from F1
action_system.py - Executes mapped actions
config.py        - Profile & mapping management
led_control.py   - RGB LED feedback
ui.py            - Tkinter config editor
```

## License

MIT
