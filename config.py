"""
Configuration management for F1-Deck
"""

import json
import logging
from pathlib import Path
import yaml

log = logging.getLogger("f1-deck.config")

DEFAULT_CONFIG = {
    "profiles": [{"name": "default", "mappings": []}],
    "active_profile": 0,
    "midi": {"port_name": "Traktor Kontrol F1", "channel": 0},
}


class ConfigManager:
    def __init__(self, config_path: str = None):
        if config_path:
            self.config_path = Path(config_path)
        else:
            self.config_path = Path.home() / ".config" / "f1-deck" / "config.json"

        self.config_dir = self.config_path.parent
        self.config = self._load_config()

    def _load_config(self) -> dict:
        if self.config_path.exists():
            try:
                with open(self.config_path, "r") as f:
                    if self.config_path.suffix in [".yaml", ".yml"]:
                        config = yaml.safe_load(f)
                    else:
                        config = json.load(f)
                log.info(f"Loaded config from {self.config_path}")
                return config
            except Exception as e:
                log.error(f"Failed to load config: {e}")

        log.info("Using default config")
        return DEFAULT_CONFIG.copy()

    def save_config(self):
        self.config_dir.mkdir(parents=True, exist_ok=True)

        try:
            with open(self.config_path, "w") as f:
                if self.config_path.suffix in [".yaml", ".yml"]:
                    yaml.dump(self.config, f, default_flow_style=False)
                else:
                    json.dump(self.config, f, indent=2)
            log.info(f"Saved config to {self.config_path}")
        except Exception as e:
            log.error(f"Failed to save config: {e}")

    def get_active_profile(self) -> dict:
        idx = self.config.get("active_profile", 0)
        profiles = self.config.get("profiles", [])

        if 0 <= idx < len(profiles):
            return profiles[idx]
        return profiles[0] if profiles else DEFAULT_CONFIG["profiles"][0]

    def set_active_profile(self, index: int):
        if 0 <= index < len(self.config.get("profiles", [])):
            self.config["active_profile"] = index
            self.save_config()

    def add_mapping(self, mapping: dict):
        profile = self.get_active_profile()
        profile.setdefault("mappings", []).append(mapping)
        self.save_config()

    def remove_mapping(self, index: int):
        profile = self.get_active_profile()
        if 0 <= index < len(profile.get("mappings", [])):
            profile["mappings"].pop(index)
            self.save_config()

    def get_mappings(self) -> list:
        return self.get_active_profile().get("mappings", [])
