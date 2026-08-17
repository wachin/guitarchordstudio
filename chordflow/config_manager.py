"""Configuration persistence for ChordFlow."""

from __future__ import annotations

import json
from pathlib import Path

from PyQt6.QtCore import QStandardPaths


CONFIG_DIR_NAME = "guitarchs"
APP_NAME = "chordflow"

DEFAULT_CONFIG: dict = {
    "max_speed": 100,
    "font_family": "Noto Mono",
    "font_size": 10,
    "last_opened_path": "",
    "use_sharps": True,
}


def config_path() -> Path:
    """Return the platform-appropriate config directory for the app.

    Linux:   ~/.config/guitarchs/chordflow/config.json
    Windows: %APPDATA%/guitarchs/chordflow/config.json
    macOS:   ~/Library/Application Support/guitarchs/chordflow/config.json
    """
    base = Path(
        QStandardPaths.writableLocation(
            QStandardPaths.StandardLocation.GenericConfigLocation
        )
    )
    path = base / CONFIG_DIR_NAME / APP_NAME
    path.mkdir(parents=True, exist_ok=True)
    return path / "config.json"


class ConfigManager:
    """Load and save application configuration as JSON."""

    def __init__(self, file_path: str | None = None):
        self.file_path = file_path or str(config_path())

    def load(self) -> dict:
        """Load config from disk, falling back to defaults."""
        if not Path(self.file_path).exists():
            return dict(DEFAULT_CONFIG)
        with open(self.file_path, "r") as f:
            return json.load(f)

    def save(self, config: dict) -> None:
        """Persist *config* to disk as JSON."""
        Path(self.file_path).parent.mkdir(parents=True, exist_ok=True)
        with open(self.file_path, "w") as f:
            json.dump(config, f, indent=4)


__all__ = ["ConfigManager", "DEFAULT_CONFIG", "config_path"]