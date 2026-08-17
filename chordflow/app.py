"""Application entry point for ChordFlow."""

from __future__ import annotations

import sys

from PyQt6.QtWidgets import QApplication

from .main_window import TextScrollerApp


def main(argv=None):
    app = QApplication(list(argv) if argv is not None else sys.argv)
    window = TextScrollerApp()
    window.show()
    return app.exec()


__all__ = ["main"]
