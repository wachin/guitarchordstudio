"""Application entry point for ChordFlow."""

from __future__ import annotations

import sys

from PyQt6.QtWidgets import QApplication

from .i18n import install_translations
from .main_window import TextScrollerApp
from .resources import app_icon


def build_application(argv=None) -> QApplication:
    """Create or reuse the ``QApplication`` and install the ChordFlow icon."""
    app = QApplication.instance()
    if app is None:
        app = QApplication(list(argv) if argv is not None else sys.argv)
    app.setWindowIcon(app_icon())
    install_translations(app, "es")
    try:
        from pyqt6_linguistic_tools.qt import install_toolkit_translations

        install_toolkit_translations(app, "es")
    except ImportError:
        pass
    return app


def main(argv=None):
    app = build_application(argv)
    window = TextScrollerApp()
    window.show()
    return app.exec()


__all__ = ["build_application", "main"]
