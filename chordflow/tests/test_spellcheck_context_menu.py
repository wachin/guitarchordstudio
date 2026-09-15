"""Regression tests for the spell-check context menu.

Right-clicking used to replace the user's selection with the word under the
pointer, so Copy and Cut stopped acting on the selected text. These tests pin
the corrected behaviour: an existing selection is never modified, and the word
under the pointer is only selected when nothing is selected.
"""

from __future__ import annotations

from types import SimpleNamespace

from PyQt6.QtCore import QPoint
from PyQt6.QtGui import QTextCursor
from PyQt6.QtWidgets import QApplication, QTextEdit, QMenu

from chordflow.spellcheck import build_spell_context_menu


MISSPELLED = "marabillas"
SUGGESTION = "maravillas"
CORRECT_WORD = "Cristo"
TEXT = f"Mi {CORRECT_WORD}, mi {MISSPELLED}, nadie es como tu"


class _FakeChecker:
    """Duck-typed ``SpellChecker`` for deterministic menu tests."""

    def __init__(self) -> None:
        self.added: list[str] = []

    def check(self, word: str) -> bool:
        return word.casefold() in {CORRECT_WORD.casefold(), "mi", "nadie", "es", "como"}

    def suggest(self, word: str) -> list[str]:
        return [SUGGESTION, "camarillas"]

    def add_word(self, word: str) -> None:
        self.added.append(word)


def _editor(qtbot) -> QTextEdit:
    editor = QTextEdit()
    editor.resize(600, 200)
    editor.setPlainText(TEXT)
    # The pointer-to-text mapping needs real geometry; offscreen is enough.
    editor.show()
    QApplication.processEvents()
    # ``_add_word`` expects the highlighter that ``install_spell_checker`` sets.
    editor._spell_highlighter = SimpleNamespace(rehighlight=lambda: None)
    qtbot.addWidget(editor)
    return editor


def _select(editor: QTextEdit, start: int, end: int) -> None:
    cursor = editor.textCursor()
    cursor.setPosition(start)
    cursor.setPosition(end, QTextCursor.MoveMode.KeepAnchor)
    editor.setTextCursor(cursor)


def _point_over(editor: QTextEdit, position: int) -> QPoint:
    cursor = QTextCursor(editor.document())
    cursor.setPosition(position)
    return editor.cursorRect(cursor).center()


def _labels(menu: QMenu) -> list[str]:
    return [
        action.text().replace("&", "").split("\t")[0].strip()
        for action in menu.actions()
    ]


def _find_copy_action(menu: QMenu):
    for action in menu.actions():
        label = action.text().replace("&", "").split("\t")[0].strip().casefold()
        if label in {"copy", "copiar"}:
            return action
    raise AssertionError(f"no Copy action in {_labels(menu)!r}")


class TestSelectionIsPreserved:
    def test_word_selection_survives_right_click(self, qtbot) -> None:
        editor = _editor(qtbot)
        start = TEXT.index(CORRECT_WORD)
        _select(editor, start, start + len(CORRECT_WORD))

        build_spell_context_menu(editor, _FakeChecker(), QPoint(60, 8))

        assert editor.textCursor().selectedText() == CORRECT_WORD

    def test_sentence_selection_survives_right_click(self, qtbot) -> None:
        editor = _editor(qtbot)
        _select(editor, 0, len(TEXT))
        selected = editor.textCursor().selectedText()

        build_spell_context_menu(editor, _FakeChecker(), QPoint(60, 8))

        assert editor.textCursor().selectedText() == selected

    def test_copy_action_copies_the_selection(self, qtbot) -> None:
        editor = _editor(qtbot)
        start = TEXT.index(CORRECT_WORD)
        _select(editor, start, start + len(CORRECT_WORD))
        menu = build_spell_context_menu(editor, _FakeChecker(), QPoint(60, 8))

        copy_action = _find_copy_action(menu)
        assert copy_action.isEnabled()
        copy_action.trigger()

        assert QApplication.clipboard().text() == CORRECT_WORD


class TestWordUnderPointer:
    def test_word_is_selected_when_nothing_is_selected(self, qtbot) -> None:
        editor = _editor(qtbot)
        start = TEXT.index(MISSPELLED)

        menu = build_spell_context_menu(
            editor, _FakeChecker(), _point_over(editor, start + 1)
        )

        assert editor.textCursor().selectedText() == MISSPELLED
        assert SUGGESTION in _labels(menu)

    def test_suggestion_replaces_the_selected_word(self, qtbot) -> None:
        editor = _editor(qtbot)
        start = TEXT.index(MISSPELLED)
        _select(editor, start, start + len(MISSPELLED))
        menu = build_spell_context_menu(editor, _FakeChecker(), QPoint(60, 8))

        action = next(
            item for item in menu.actions() if item.text() == SUGGESTION
        )
        action.trigger()

        assert editor.toPlainText() == TEXT.replace(MISSPELLED, SUGGESTION)
        assert editor.textCursor().selectedText() != MISSPELLED

    def test_add_to_dictionary_action_uses_the_word(self, qtbot) -> None:
        editor = _editor(qtbot)
        start = TEXT.index(MISSPELLED)
        _select(editor, start, start + len(MISSPELLED))
        checker = _FakeChecker()
        menu = build_spell_context_menu(editor, checker, QPoint(60, 8))

        add_action = next(
            item for item in menu.actions() if item.text().startswith("Add ")
        )
        add_action.trigger()

        assert checker.added == [MISSPELLED]

    def test_correct_word_has_no_suggestion_actions(self, qtbot) -> None:
        editor = _editor(qtbot)
        start = TEXT.index(CORRECT_WORD)
        _select(editor, start, start + len(CORRECT_WORD))
        menu = build_spell_context_menu(editor, _FakeChecker(), QPoint(60, 8))

        labels = _labels(menu)
        assert SUGGESTION not in labels
        assert not any(label.startswith("Add ") for label in labels)
