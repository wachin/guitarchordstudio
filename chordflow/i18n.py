"""Qt translation loading for ChordFlow."""

from __future__ import annotations

import sys
from pathlib import Path

from PyQt6.QtCore import QTranslator
from PyQt6.QtWidgets import QApplication


TRANSLATION_BASENAME = "chordflow"
SOURCE_TRANSLATIONS_PATH = Path(__file__).resolve().parent.parent / "translations"
INSTALLED_TRANSLATIONS_PATH = (
    Path(sys.prefix) / "share" / "chordflow" / "translations"
)


def install_translations(app: QApplication, language: str = "es") -> QTranslator | None:
    """Install the optional ChordFlow application translator."""
    previous = getattr(app, "_chordflow_translator", None)
    if isinstance(previous, QTranslator):
        app.removeTranslator(previous)

    candidate = language.strip().replace("-", "_") or "es"
    files = [
        SOURCE_TRANSLATIONS_PATH / f"{TRANSLATION_BASENAME}_{candidate}.qm",
        INSTALLED_TRANSLATIONS_PATH / f"{TRANSLATION_BASENAME}_{candidate}.qm",
    ]
    for translation_file in files:
        if not translation_file.is_file():
            continue
        translator = QTranslator(app)
        if translator.load(str(translation_file)):
            app.installTranslator(translator)
            app._chordflow_translator = translator
            return translator
    return None


__all__ = [
    "INSTALLED_TRANSLATIONS_PATH",
    "SOURCE_TRANSLATIONS_PATH",
    "install_translations",
]
