"""Shared per-user paths for the GuitarChordStudio applications.

Linux follows the XDG base-directory specification:

    ~/.config/guitarchordstudio/          configuration
    ~/.local/share/guitarchordstudio/     dictionaries and document data

Windows and macOS use the conventional visible folder name
``GuitarChordStudio`` under the platform application-data directory.  The
subdirectories are lowercase on Linux and PascalCase elsewhere.
"""

from __future__ import annotations

import os
from pathlib import Path
import sys


WINDOWS_APP_DIR = "GuitarChordStudio"
MACOS_APP_DIR = "GuitarChordStudio"
LINUX_APP_DIR = "guitarchordstudio"

_APP_NAMES = {
    "chordflow": "ChordFlow",
    "chordpages": "ChordPages",
}


def _platform_app_dir() -> str:
    if sys.platform == "win32":
        return WINDOWS_APP_DIR
    if sys.platform == "darwin":
        return MACOS_APP_DIR
    return LINUX_APP_DIR


def _linux_config_home() -> Path:
    return Path(
        os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config")
    ).expanduser()


def _linux_data_home() -> Path:
    return Path(
        os.environ.get("XDG_DATA_HOME", Path.home() / ".local" / "share")
    ).expanduser()


def _windows_appdata() -> Path:
    return Path(
        os.environ.get("APPDATA", Path.home() / "AppData" / "Roaming")
    ).expanduser()


def config_root() -> Path:
    """Return the shared configuration root for this platform."""
    if sys.platform == "win32":
        return _windows_appdata() / _platform_app_dir()
    if sys.platform == "darwin":
        return Path.home() / "Library" / "Application Support" / _platform_app_dir()
    return _linux_config_home() / _platform_app_dir()


def data_root() -> Path:
    """Return the shared data root for dictionaries and document data."""
    if sys.platform == "win32":
        return _windows_appdata() / _platform_app_dir()
    if sys.platform == "darwin":
        return Path.home() / "Library" / "Application Support" / _platform_app_dir()
    return _linux_data_home() / _platform_app_dir()


def app_directory_name(application: str) -> str:
    """Return the platform-appropriate component name for an application."""
    key = application.strip().lower()
    if sys.platform in {"win32", "darwin"}:
        return _APP_NAMES.get(key, application)
    return key


def app_config_dir(application: str) -> Path:
    """Return the application's configuration directory."""
    return config_root() / app_directory_name(application)


def app_data_dir(application: str) -> Path:
    """Return the application's document-data directory."""
    return data_root() / app_directory_name(application)


def dictionaries_dir() -> Path:
    """Return the shared managed/user dictionary directory."""
    return data_root() / "dictionaries"


__all__ = [
    "app_config_dir",
    "app_data_dir",
    "app_directory_name",
    "config_root",
    "data_root",
    "dictionaries_dir",
]
