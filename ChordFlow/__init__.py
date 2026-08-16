"""ChordFlow application package."""

from .app import main
from .chord_transposer import is_chord_line, transpose_chord, transpose_text
from .config_manager import ConfigManager
from .file_operations import detect_encoding, read_file, write_file
from .main_window import TextScrollerApp
from .search_dialog import FindInFilesDialog, SynonymsDialog
from .thesaurus import MythesThesaurus

__all__ = [
    "ConfigManager",
    "FindInFilesDialog",
    "MythesThesaurus",
    "SynonymsDialog",
    "TextScrollerApp",
    "detect_encoding",
    "is_chord_line",
    "main",
    "read_file",
    "transpose_chord",
    "transpose_text",
    "write_file",
]
