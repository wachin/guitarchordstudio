"""Configuration persistence for ChordFlow."""

from __future__ import annotations

import json
import os


DEFAULT_CONFIG: dict = {
    "max_speed": 100,
    "font_family": "Noto Mono",
    "font_size": 10,
    "last_opened_path": "",
    "use_sharps": True,
}


class ConfigManager:
    """Load and save application configuration as JSON."""

    def __init__(self, file_path: str = "config12.json"):
        self.file_path = file_path

    def load(self) -> dict:
        """Load config from disk, falling back to defaults."""
        if not os.path.exists(self.file_path):
            return dict(DEFAULT_CONFIG)
        with open(self.file_path, "r") as f:
            return json.load(f)

    def save(self, config: dict) -> None:
        """Persist *config* to disk as JSON."""
        with open(self.file_path, "w") as f:
            json.dump(config, f, indent=4)


__all__ = ["ConfigManager", "DEFAULT_CONFIG"]