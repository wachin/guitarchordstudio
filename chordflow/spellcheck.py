"""Spell-checking support via system Hunspell dictionaries."""

from __future__ import annotations

import locale
import re
from pathlib import Path

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction, QSyntaxHighlighter, QTextCharFormat, QTextCursor
from PyQt6.QtWidgets import QMenu, QTextEdit

try:
    import hunspell

    _HUNSPELL_AVAILABLE = True
except ImportError:
    _HUNSPELL_AVAILABLE = False


# ---------------------------------------------------------------------------
# Core spell checker
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

    def set_language(self, lang: str) -> bool:
        """Switch to a different dictionary.  Returns ``True`` on success."""
        self._lang = lang
        self._hs = None
        self._load()
        return self.available

    def check(self, word: str) -> bool:
        """Return ``True`` when *word* is spelled correctly."""
        if self._hs is None:
            return True
        # pyhunspell 0.5.x handles UTF-8 bytes correctly for accented chars.
        return self._hs.spell(word.encode("utf-8"))

    def suggest(self, word: str) -> list[str]:
        """Return a list of spelling suggestions for *word*."""
        if self._hs is None:
            return []
        return self._hs.suggest(word.encode("utf-8"))

    def add_word(self, word: str) -> None:
        """Add *word* to the current session dictionary."""
        if self._hs is not None:
            self._hs.add(word.encode("utf-8"))

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
                self._hs.add_dic(str(dic))
                self._hs.spell(b"test")  # verify
                return
            except Exception:
                self._hs = None
                continue


# ---------------------------------------------------------------------------
# Qt spell highlighter
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
        self._accent_re = re.compile(
            r"[áéíóúàèìòùâêîôûäëïöüñçÁÉÍÓÚÀÈÌÒÙÂÊÎÔÛÄËÏÖÜÑÇ]"
        )

    def highlightBlock(self, text: str) -> None:
        if not self._checker.available:
            return
        for m in self._word_re.finditer(text):
            word = m.group()
            if len(word) <= 1 or word.isdigit():
                continue
            # Skip lines that look like chord-only lines (uppercase + optional
            # sharps/flats, no vowels beyond the first letter).
            if re.match(r"^[A-G](#|b)?(m|maj|min|dim|aug|sus|add)?[0-9]?$", word):
                continue
            if not self._checker.check(word):
                self.setFormat(m.start(), m.end() - m.start(), self._fmt)


# ---------------------------------------------------------------------------
# Context-menu integration
# ---------------------------------------------------------------------------

AVAILABLE_LANGUAGES: dict[str, str] = {}


def _scan_languages() -> dict[str, str]:
    """Scan for available Hunspell dictionaries and return ``{lang: label}``."""
    langs: dict[str, str] = {}
    for path in Path("/usr/share/hunspell").glob("*.dic"):
        lang = path.stem
        label = _language_label(lang)
        langs[lang] = label
    return dict(sorted(langs.items()))


def _language_label(lang: str) -> str:
    """Return a human-readable label for a language code."""
    labels = {
        "en_US": "English (US)",
        "en_GB": "English (UK)",
        "es_ES": "Spanish (Spain)",
        "es_EC": "Spanish (Ecuador)",
        "es_MX": "Spanish (Mexico)",
        "es_AR": "Spanish (Argentina)",
        "fr_FR": "French",
        "de_DE": "German",
        "pt_BR": "Portuguese (Brazil)",
        "pt_PT": "Portuguese (Portugal)",
        "it_IT": "Italian",
        "ca_ES": "Catalan",
    }
    return labels.get(lang, lang.replace("_", " "))


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

    # Install highlighter.
    highlighter = SpellHighlighter(editor.document(), checker)
    editor._spell_highlighter = highlighter  # type: ignore[attr-defined]
    editor._spell_checker = checker  # type: ignore[attr-defined]

    # Monkey-patch the context menu.
    def _context_menu(event):
        menu = editor.createStandardContextMenu()
        cursor = editor.cursorForPosition(event.pos())
        cursor.select(QTextCursor.SelectionType.WordUnderCursor)
        word = cursor.selectedText()

        if word and not checker.check(word):
            suggestions = checker.suggest(word)
            if suggestions:
                insert_pos = menu.actions()[0] if menu.actions() else None
                first = True
                for s in suggestions[:10]:
                    if first:
                        first = False
                    action = QAction(s, editor)
                    action.triggered.connect(
                        lambda checked, sug=s: _replace_word(editor, sug)
                    )
                    menu.insertAction(insert_pos, action)
                menu.insertSeparator(insert_pos)

            # "Add to dictionary"
            add_action = QAction(f'Add "{word}" to dictionary', editor)
            add_action.triggered.connect(
                lambda checked: _add_word(editor, checker, word)
            )
            menu.insertAction(
                menu.actions()[0] if menu.actions() else None,
                add_action,
            )
            menu.insertSeparator(
                menu.actions()[0] if menu.actions() else None,
            )

        menu.exec(event.globalPos())

    editor.contextMenuEvent = _context_menu  # type: ignore[method-assign]
    return checker


def _replace_word(editor: QTextEdit, replacement: str) -> None:
    cursor = editor.textCursor()
    cursor.select(QTextCursor.SelectionType.WordUnderCursor)
    cursor.insertText(replacement)
    editor.setTextCursor(cursor)


def _add_word(editor: QTextEdit, checker: SpellChecker, word: str) -> None:
    checker.add_word(word)
    # Force re-highlight of the current document.
    editor._spell_highlighter.rehighlight()  # type: ignore[attr-defined]


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


def build_language_menu(parent, editor_getter) -> QMenu:
    """Build a ``QMenu`` of available Hunspell dictionaries.

    When an item is selected, the spell checker attached to the editor
    returned by *editor_getter* is switched to that language.
    """
    menu = QMenu("Spell-check language", parent)
    langs = _scan_languages()
    if not langs:
        action = menu.addAction("(no dictionaries found)")
        action.setEnabled(False)
        return menu

    for code, label in langs.items():
        action = menu.addAction(label)
        action.setData(code)
        action.triggered.connect(
            lambda checked, c=code: _switch_language(editor_getter(), c)
        )
    return menu


def _switch_language(editor: QTextEdit, lang: str) -> None:
    """Switch the spell checker on *editor* to *lang*."""
    checker: SpellChecker | None = getattr(editor, "_spell_checker", None)
    if checker is None:
        return
    if checker.set_language(lang):
        highlighter: SpellHighlighter | None = getattr(
            editor, "_spell_highlighter", None
        )
        if highlighter is not None:
            highlighter.rehighlight()


__all__ = [
    "SpellChecker",
    "SpellHighlighter",
    "install_spell_checker",
    "build_language_menu",
    "AVAILABLE_LANGUAGES",
]