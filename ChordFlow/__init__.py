"""ChordFlow application package."""

from .app import main
from .main_window import TextScrollerApp
from .search_dialog import FindInFilesDialog, SynonymsDialog
from .thesaurus import MythesThesaurus

__all__ = [
    "FindInFilesDialog",
    "MythesThesaurus",
    "SynonymsDialog",
    "TextScrollerApp",
    "main",
]
