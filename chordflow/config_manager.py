"""Configuration persistence for ChordFlow."""

from __future__ import annotations

import json
from pathlib import Path

from guitarchordstudio_paths import app_config_dir


CONFIG_DIR_NAME = "guitarchordstudio"
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

    Linux:   ~/.config/guitarchordstudio/chordflow/settings.json
    Windows: %APPDATA%/GuitarChordStudio/ChordFlow/settings.json
    macOS:   ~/Library/Application Support/GuitarChordStudio/ChordFlow/settings.json
    """
    path = app_config_dir("chordflow")
    path.mkdir(parents=True, exist_ok=True)
    return path / "settings.json"


class ConfigManager:
    """Load and save application configuration as JSON."""

    def __init__(self, file_path: str | None = None):
        self.file_path = file_path or str(config_path())
        if file_path is None:
            legacy_path = Path(self.file_path).with_name("config.json")
            if not Path(self.file_path).exists() and legacy_path.exists():
                try:
                    with legacy_path.open("r", encoding="utf-8") as legacy_file:
                        legacy_config = json.load(legacy_file)
                    if isinstance(legacy_config, dict):
                        self.save(legacy_config)
                except (OSError, json.JSONDecodeError):
                    pass

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