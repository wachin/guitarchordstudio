"""Regression test for the thesaurus replacement signal contract."""

from __future__ import annotations

import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest


pytest.importorskip("PyQt6", reason="PyQt6 is an optional dependency")

from PyQt6.QtCore import QObject, pyqtSignal
from PyQt6.QtGui import QTextCursor
from PyQt6.QtWidgets import QApplication

from chordflow import main_window as main_window_module
from chordflow.config_manager import DEFAULT_CONFIG


class _FakeThesaurusDialog(QObject):
    """Emit the same two-argument signal as the real toolkit dialog."""

    replacement_requested = pyqtSignal(str, str)

    def __init__(self, _service, word: str, parent=None) -> None:
        super().__init__(parent)
        self.word = word

    def exec(self) -> int:
        self.replacement_requested.emit(self.word, "asistencia")
        return 1


def test_thesaurus_replacement_uses_the_replacement_argument(monkeypatch):
    application = QApplication.instance() or QApplication([])

    class _MemoryConfig:
        def __init__(self, *_args, **_kwargs) -> None:
            self.values: dict = {}

        def load(self) -> dict:
            values = dict(DEFAULT_CONFIG)
            values["last_slider_position"] = 15
            values.update(self.values)
            return values

        def save(self, *_args, **_kwargs) -> None:
            return None

    monkeypatch.setattr(main_window_module, "ConfigManager", _MemoryConfig)
    monkeypatch.setattr(
        main_window_module,
        "ThesaurusDialog",
        _FakeThesaurusDialog,
    )
    window = main_window_module.TextScrollerApp()
    editor = window.get_current_text_widget()
    assert editor is not None
    assert not editor._linguistic_decorator.context_menu.action_enabled("language")

    editor.setPlainText("Presencia")
    cursor = editor.textCursor()
    cursor.setPosition(0)
    cursor.setPosition(
        len("Presencia"),
        QTextCursor.MoveMode.KeepAnchor,
    )
    editor.setTextCursor(cursor)

    window.show_synonyms_dialog()

    assert editor.toPlainText() == "asistencia"
    editor.document().setModified(False)
    window.close()
    application.processEvents()
