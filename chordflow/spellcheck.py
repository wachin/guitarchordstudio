"""Spell-checking support via system Hunspell library (ctypes)."""

from __future__ import annotations

import ctypes
import ctypes.util
import locale
import re
from pathlib import Path

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction, QSyntaxHighlighter, QTextCharFormat, QTextCursor
from PyQt6.QtWidgets import QMenu, QTextEdit

# ---------------------------------------------------------------------------
# Load libhunspell via ctypes
# ---------------------------------------------------------------------------

_LIB: ctypes.CDLL | None = None
_lib_path = ctypes.util.find_library("hunspell-1.7")
if _lib_path is None:
    _lib_path = ctypes.util.find_library("hunspell")
if _lib_path is not None:
    try:
        _LIB = ctypes.cdll.LoadLibrary(_lib_path)
    except Exception:
        _LIB = None


def _hs_create(aff: bytes, dic: bytes) -> ctypes.c_void_p | None:
    """Create a Hunspell handle via ctypes."""
    if _LIB is None:
        return None
    try:
        _LIB.Hunspell_create.restype = ctypes.c_void_p
        _LIB.Hunspell_create.argtypes = [ctypes.c_char_p, ctypes.c_char_p]
        return _LIB.Hunspell_create(aff, dic)
    except Exception:
        return None


def _hs_destroy(handle: ctypes.c_void_p) -> None:
    if _LIB is not None and handle is not None:
        try:
            _LIB.Hunspell_destroy(handle)
        except Exception:
            pass


def _hs_spell(handle: ctypes.c_void_p, word: bytes) -> bool:
    if _LIB is None or handle is None:
        return True
    try:
        _LIB.Hunspell_spell.restype = ctypes.c_int
        _LIB.Hunspell_spell.argtypes = [ctypes.c_void_p, ctypes.c_char_p]
        return bool(_LIB.Hunspell_spell(handle, word))
    except Exception:
        return True


def _hs_suggest(handle: ctypes.c_void_p, word: bytes) -> list[str]:
    if _LIB is None or handle is None:
        return []
    try:
        _LIB.Hunspell_suggest.restype = ctypes.c_int
        _LIB.Hunspell_suggest.argtypes = [
            ctypes.c_void_p,
            ctypes.POINTER(ctypes.c_char_p),
            ctypes.c_char_p,
        ]
        arr = ctypes.c_char_p()
        n = _LIB.Hunspell_suggest(handle, ctypes.byref(arr), word)
        result: list[str] = []
        if n > 0:
            ptr = ctypes.cast(arr, ctypes.c_void_p).value
            for i in range(n):
                str_ptr = ctypes.c_char_p.from_address(
                    ptr + i * ctypes.sizeof(ctypes.c_char_p)
                )
                if str_ptr.value:
                    result.append(str_ptr.value.decode("utf-8"))
        _LIB.Hunspell_free_list(handle, ctypes.byref(arr), n)
        return result
    except Exception:
        return []


def _hs_add(handle: ctypes.c_void_p, word: bytes) -> None:
    if _LIB is None or handle is None:
        return
    try:
        _LIB.Hunspell_add.restype = ctypes.c_int
        _LIB.Hunspell_add.argtypes = [ctypes.c_void_p, ctypes.c_char_p]
        _LIB.Hunspell_add(handle, word)
    except Exception:
        pass


# ---------------------------------------------------------------------------
# Core spell checker
# ---------------------------------------------------------------------------

class SpellChecker:
    """Check words and get suggestions via the system Hunspell library."""

    def __init__(self, lang: str | None = None):
        self._handle: ctypes.c_void_p | None = None
        self._lang = lang or _default_lang()
        self._load()

    # --- public API -------------------------------------------------------

    @property
    def available(self) -> bool:
        return self._handle is not None

    @property
    def language(self) -> str:
        return self._lang

    def set_language(self, lang: str) -> bool:
        self._destroy()
        self._lang = lang
        self._load()
        return self.available

    def check(self, word: str) -> bool:
        if self._handle is None:
            return True
        return _hs_spell(self._handle, word.encode("utf-8"))

    def suggest(self, word: str) -> list[str]:
        if self._handle is None:
            return []
        return _hs_suggest(self._handle, word.encode("utf-8"))

    def add_word(self, word: str) -> None:
        if self._handle is not None:
            _hs_add(self._handle, word.encode("utf-8"))

    def _destroy(self) -> None:
        if self._handle is not None:
            _hs_destroy(self._handle)
            self._handle = None

    # --- internal ---------------------------------------------------------

    def _load(self) -> None:
        if _LIB is None:
            return
        lang = self._lang.replace("-", "_")
        for aff, dic in _dictionary_paths(lang):
            if not aff.exists() or not dic.exists():
                continue
            try:
                handle = _hs_create(str(aff).encode("utf-8"), str(dic).encode("utf-8"))
                if handle is not None:
                    self._handle = handle
                    _hs_spell(handle, b"test")  # verify
                    return
            except Exception:
                self._handle = None
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

    def highlightBlock(self, text: str) -> None:
        if not self._checker.available:
            return
        for m in self._word_re.finditer(text):
            word = m.group()
            if len(word) <= 1 or word.isdigit():
                continue
            if re.match(r"^[A-G](#|b)?(m|maj|min|dim|aug|sus|add)?[0-9]?$", word):
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

    highlighter = SpellHighlighter(editor.document(), checker)
    editor._spell_highlighter = highlighter  # type: ignore[attr-defined]
    editor._spell_checker = checker  # type: ignore[attr-defined]

    def _context_menu(event):
        menu = editor.createStandardContextMenu()
        cursor = editor.cursorForPosition(event.pos())
        cursor.select(QTextCursor.SelectionType.WordUnderCursor)
        word = cursor.selectedText()

        if word and not checker.check(word):
            suggestions = checker.suggest(word)
            if suggestions:
                insert_pos = menu.actions()[0] if menu.actions() else None
                for s in suggestions[:10]:
                    action = QAction(s, editor)
                    action.triggered.connect(
                        lambda checked, sug=s: _replace_word(editor, sug)
                    )
                    menu.insertAction(insert_pos, action)
                menu.insertSeparator(insert_pos)

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
    editor._spell_highlighter.rehighlight()  # type: ignore[attr-defined]


# ---------------------------------------------------------------------------
# Language menu builder
# ---------------------------------------------------------------------------

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
    return labels.get(lang, lang.replace("_", " ").title())


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
    "build_language_menu",
]