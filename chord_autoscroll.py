"""Compatibility launcher for ChordFlow."""

from __future__ import annotations

import sys

from ChordFlow.app import main
from ChordFlow.main_window import CustomTextEdit, TextScrollerApp
from ChordFlow.search_dialog import FindInFilesDialog, SynonymsDialog
from ChordFlow.thesaurus import MythesThesaurus

__all__ = [
    "CustomTextEdit",
    "FindInFilesDialog",
    "MythesThesaurus",
    "SynonymsDialog",
    "TextScrollerApp",
    "main",
]


if __name__ == "__main__":
    sys.exit(main())
