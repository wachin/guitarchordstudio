"""Application resources for ChordFlow."""

from __future__ import annotations

from pathlib import Path

from PyQt6.QtGui import QIcon


ASSETS_PATH = Path(__file__).with_name("assets")
APP_ICON_PATH = ASSETS_PATH / "chordflow.svg"


def app_icon() -> QIcon:
    """Return the ChordFlow application icon."""
    return QIcon(str(APP_ICON_PATH))


__all__ = ["APP_ICON_PATH", "app_icon"]
