"""Spell-checking support via system Hunspell dictionaries."""

from __future__ import annotations

import locale
import re
from pathlib import Path

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction, QSyntaxHighlighter, QTextCharFormat, QTextCursor
from PyQt6.QtWidgets import QTextEdit

try:
    import hunspell

    _HUNSPELL_AVAILABLE = True
except ImportError:
    _HUNSPELL_AVAILABLE = False


# ---------------------------------------------------------------------------
# Core spell checker  (thin wrapper around system hunspell)
# ---------------------------------------------------------------------------

class SpellChecker:
    """Check words and get suggestions via the system Hunspell library.

    The constructor tries to load a dictionary for the given *lang* code
    (e.g. ``"en_US"``, ``"es_ES"``).  When *lang* is ``None`` the system
    locale is used.
    """

    def __init__(self, lang: str | None = None):
        self._hs: hunspell.HunSpell | None = None
        self._lang = lang or _default_lang()
        self._load()

    # --- public API -------------------------------------------------------

    @property
    def available(self) -> bool:
        """``True`` when the hunspell library and dictionary were loaded."""
        return self._hs is not None

    @property
    def language(self) -> str:
        return self._lang

    def check(self, word: str) -> bool:
        """Return ``True`` when *word* is spelled correctly."""
        if self._hs is None:
            return True
        return self._hs.spell(word)

    def suggest(self, word: str) -> list[str]:
        """Return a list of spelling suggestions for *word*."""
        if self._hs is None:
            return []
        return self._hs.suggest(word)

    # --- internal ---------------------------------------------------------

    def _load(self) -> None:
        if not _HUNSPELL_AVAILABLE:
            return
        lang = self._lang.replace("-", "_")
        for aff, dic in _dictionary_paths(lang):
            if not aff.exists() or not dic.exists():
                continue
            try:
                self._hs = hunspell.HunSpell(str(aff), str(dic))
                # pyhunspell 0.5.x requires an explicit add_dic call,
                # otherwise the dictionary is not actually loaded.
                self._hs.add_dic(str(dic))
                # Verify the dictionary works.
                self._hs.spell("test")
                return
            except Exception:
                self._hs = None
                continue


# ---------------------------------------------------------------------------
# Qt spell highlighter  (red underline on misspelled words)
# ---------------------------------------------------------------------------

class SpellHighlighter(QSyntaxHighlighter):
    """Underline misspelled words in red."""

    def __init__(self, document, checker: SpellChecker):
        super().__init__(document)
        self._checker = checker
        self._fmt = QTextCharFormat()
        self._fmt.setUnderlineStyle(
            QTextCharFormat.UnderlineStyle.SpellCheckUnderline
        )
        self._fmt.setUnderlineColor(Qt.GlobalColor.red)
        self._word_re = re.compile(r"\b\w+\b")

    def highlightBlock(self, text: str) -> None:
        if not self._checker.available:
            return
        for m in self._word_re.finditer(text):
            word = m.group()
            # Skip numbers and very short tokens
            if len(word) <= 1 or word.isdigit():
                continue
            if not self._checker.check(word):
                self.setFormat(m.start(), m.end() - m.start(), self._fmt)


# ---------------------------------------------------------------------------
# Context-menu integration
# ---------------------------------------------------------------------------

def install_spell_checker(
    editor: QTextEdit, lang: str | None = None
) -> SpellChecker:
    """Attach a spell checker + highlighter to *editor*.

    Returns the :class:`SpellChecker` instance so callers can inspect
    ``.available`` and ``.language``.
    """
    checker = SpellChecker(lang)
    if not checker.available:
        return checker

    # Install highlighter on the document.
    highlighter = SpellHighlighter(editor.document(), checker)
    # Keep a reference so it isn't garbage-collected.
    editor._spell_highlighter = highlighter  # type: ignore[attr-defined]

    # Monkey-patch the context menu.
    _orig = editor.contextMenuEvent

    def _context_menu(event):
        menu = editor.createStandardContextMenu()
        cursor = editor.cursorForPosition(event.pos())
        cursor.select(QTextCursor.SelectionType.WordUnderCursor)
        word = cursor.selectedText()

        if word and not checker.check(word):
            suggestions = checker.suggest(word)
            if suggestions:
                first = True
                for s in suggestions[:10]:
                    if first:
                        first = False
                    action = QAction(s, editor)
                    action.triggered.connect(
                        lambda checked, sug=s: _replace_word(editor, sug)
                    )
                    menu.insertAction(menu.actions()[0] if menu.actions() else None, action)
                menu.insertSeparator(menu.actions()[0] if menu.actions() else None)

        menu.exec(event.globalPos())

    editor.contextMenuEvent = _context_menu  # type: ignore[method-assign]
    return checker


def _replace_word(editor: QTextEdit, replacement: str) -> None:
    cursor = editor.textCursor()
    cursor.select(QTextCursor.SelectionType.WordUnderCursor)
    cursor.insertText(replacement)
    editor.setTextCursor(cursor)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _default_lang() -> str:
    """Return a language code from the system locale (e.g. ``"en_US"``)."""
    try:
        code, _ = locale.getlocale(locale.LC_MESSAGES)
        if code:
            return code.replace("-", "_")
    except Exception:
        pass
    return "en_US"


def _dictionary_paths(lang: str) -> list[tuple[Path, Path]]:
    """Return possible ``(aff_path, dic_path)`` pairs for *lang*."""
    bases = [
        Path(f"/usr/share/hunspell/{lang}"),
        Path(f"/usr/share/myspell/dicts/{lang}"),
        Path(f"/usr/share/hunspell/{lang.replace('_', '-')}"),
    ]
    return [(b.with_suffix(".aff"), b.with_suffix(".dic")) for b in bases]


__all__ = [
    "SpellChecker",
    "SpellHighlighter",
    "install_spell_checker",
]