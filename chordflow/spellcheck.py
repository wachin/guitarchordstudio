"""Spell-checking support.

Linux / macOS: Hunspell via system ctypes (when the shared library is found).
Windows: lightweight pure-Python spell checker that reads ``.dic`` files directly
and applies basic affix rules.  No external DLL needed.
"""

from __future__ import annotations

import ctypes
import ctypes.util
import locale
import os
import re
import sys
from pathlib import Path

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction, QSyntaxHighlighter, QTextCharFormat, QTextCursor
from PyQt6.QtWidgets import QMenu, QTextEdit

# ---------------------------------------------------------------------------
# Backend detection
# ---------------------------------------------------------------------------

def _find_hunspell_dll() -> str | None:
    """Find the Hunspell shared library on Linux / macOS only."""
    if sys.platform == "win32":
        return None
    for name in ["hunspell-1.7", "hunspell"]:
        lib = ctypes.util.find_library(name)
        if lib:
            return lib
    return None


_LIB: ctypes.CDLL | None = None
_dll_path = _find_hunspell_dll()
if _dll_path is not None:
    try:
        _LIB = ctypes.cdll.LoadLibrary(_dll_path)
    except Exception:
        _LIB = None

_USE_HUNSPELL_CTYPES = _LIB is not None


# ---------------------------------------------------------------------------
# Pure-Python .dic reader with affix rule support (Windows fallback)
# ---------------------------------------------------------------------------

class _DicFileWordSet:
    """Load words from a Hunspell .dic file + apply .aff suffix rules.

    Hunspell .dic format:
        Line 1: word_count [optional flags]
        Lines 2..N: word[/flags]  — flags reference rules in the .aff file

    SFX rules in .aff:
        SFX flag N count          — header
        SFX flag strip add cond   — rule lines (N of them)

    We expand derived words by applying SFX rules to base words that carry
    the matching flag character.
    """

    def __init__(self, dic_path: Path):
        self.words: set[str] = set()
        self._load(dic_path)

    def _load(self, dic_path: Path) -> None:
        if not dic_path.exists():
            return
        try:
            encoding = self._detect_encoding(dic_path)
            with open(dic_path, "r", encoding=encoding, errors="replace") as f:
                raw_lines = f.readlines()

            # Parse base words with their flags
            base_words: list[tuple[str, str]] = []
            for line in raw_lines[1:]:
                parts = line.strip().split("/", 1)
                word = parts[0].strip()
                flags = parts[1].strip() if len(parts) > 1 else ""
                if word:
                    base_words.append((word, flags))
                    self.words.add(word.lower())

            # Parse affix rules and expand derived words
            aff_path = dic_path.with_suffix(".aff")
            if aff_path.exists():
                self._expand_with_affix_rules(base_words, aff_path, encoding)

        except Exception:
            pass

    def _expand_with_affix_rules(
        self, base_words: list[tuple[str, str]], aff_path: Path, encoding: str
    ) -> None:
        """Parse SFX rules from .aff and generate derived word forms."""
        try:
            with open(aff_path, "r", encoding=encoding, errors="replace") as f:
                aff_lines = f.readlines()
        except Exception:
            return

        suffix_rules: dict[str, list[tuple[str, str, str]]] = {}
        current_flag: str | None = None
        current_rules: list[tuple[str, str, str]] = []

        for line in aff_lines:
            stripped = line.strip()
            if stripped.startswith("SFX ") and not stripped.startswith("SFX Y"):
                parts = stripped.split()
                if len(parts) >= 2 and len(parts[1]) == 1 and parts[1] not in ("Y", "N"):
                    # Header line: SFX flag Y count  or  SFX flag N count
                    if current_flag:
                        suffix_rules[current_flag] = current_rules
                    current_flag = parts[1]
                    current_rules = []
                elif len(parts) == 5 and current_flag:
                    # Rule line: SFX flag strip add condition
                    flag = parts[1]
                    strip = parts[2] if parts[2] != "0" else ""
                    add = parts[3]
                    condition = parts[4]
                    current_rules.append((strip, add, condition))

        if current_flag:
            suffix_rules[current_flag] = current_rules

        # Apply rules to base words
        for word, flags in base_words:
            if not flags:
                continue
            for flag_char in flags:
                for strip, add, condition in suffix_rules.get(flag_char, []):
                    derived = self._apply_suffix_rule(word, strip, add, condition)
                    if derived:
                        self.words.add(derived.lower())

    @staticmethod
    def _apply_suffix_rule(word: str, strip: str, add: str, condition: str) -> str | None:
        """Apply one suffix rule.  Returns derived word or None."""
        # Hunspell conditions use dot as wildcard, [^...] for negation
        if condition and condition != ".":
            cond_re = "^" + condition.replace(".", "[a-zA-ZáéíóúñÁÉÍÓÚÑ]") + "$"
            try:
                if not re.match(cond_re, word):
                    return None
            except re.error:
                pass

        # Strip characters from end
        base = word
        if strip:
            if strip == "0":
                pass
            elif word.endswith(strip):
                base = word[: -len(strip)]
            else:
                return None

        # Add suffix
        return base + add

    @staticmethod
    def _detect_encoding(dic_path: Path) -> str:
        """Try to detect encoding from the sibling .aff file."""
        aff = dic_path.with_suffix(".aff")
        if aff.exists():
            try:
                with open(aff, "r", encoding="utf-8", errors="replace") as f:
                    for line in f:
                        if line.startswith("SET "):
                            return line.split()[1].strip()
            except Exception:
                pass
        return "utf-8"

    def contains(self, word: str) -> bool:
        return word.lower() in self.words


# ---------------------------------------------------------------------------
# Hunspell ctypes wrapper (Linux / macOS)
# ---------------------------------------------------------------------------

def _hs_create(aff: bytes, dic: bytes) -> ctypes.c_void_p | None:
    if not _USE_HUNSPELL_CTYPES:
        return None
    try:
        _LIB.Hunspell_create.restype = ctypes.c_void_p
        _LIB.Hunspell_create.argtypes = [ctypes.c_char_p, ctypes.c_char_p]
        return _LIB.Hunspell_create(aff, dic)
    except Exception:
        return None


def _hs_destroy(handle: ctypes.c_void_p) -> None:
    if _USE_HUNSPELL_CTYPES and handle is not None:
        try:
            _LIB.Hunspell_destroy(handle)
        except Exception:
            pass


def _hs_spell(handle: ctypes.c_void_p, word: bytes) -> bool:
    if not _USE_HUNSPELL_CTYPES or handle is None:
        return True
    try:
        _LIB.Hunspell_spell.restype = ctypes.c_int
        _LIB.Hunspell_spell.argtypes = [ctypes.c_void_p, ctypes.c_char_p]
        return bool(_LIB.Hunspell_spell(handle, word))
    except Exception:
        return True


def _hs_suggest(handle: ctypes.c_void_p, word: bytes) -> list[str]:
    if not _USE_HUNSPELL_CTYPES or handle is None:
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
    if _USE_HUNSPELL_CTYPES and handle is not None:
        try:
            _LIB.Hunspell_add.restype = ctypes.c_int
            _LIB.Hunspell_add.argtypes = [ctypes.c_void_p, ctypes.c_char_p]
            _LIB.Hunspell_add(handle, word)
        except Exception:
            pass


# ---------------------------------------------------------------------------
# Core spell checker (auto-selects backend)
# ---------------------------------------------------------------------------

class SpellChecker:
    """Check words and get suggestions.

    Uses Hunspell via ctypes on Linux / macOS, or a pure-Python .dic word
    list with affix expansion on Windows.
    """

    def __init__(self, lang: str | None = None):
        self._handle: ctypes.c_void_p | None = None
        self._dic_set: _DicFileWordSet | None = None
        self._lang = lang or _default_lang()
        self._load()

    @property
    def available(self) -> bool:
        if _USE_HUNSPELL_CTYPES:
            return self._handle is not None
        return self._dic_set is not None

    @property
    def language(self) -> str:
        return self._lang

    @property
    def backend(self) -> str:
        return "hunspell" if _USE_HUNSPELL_CTYPES else "dic"

    def set_language(self, lang: str) -> bool:
        self._destroy()
        self._lang = lang
        self._load()
        return self.available

    def check(self, word: str) -> bool:
        if _USE_HUNSPELL_CTYPES:
            if self._handle is None:
                return True
            return _hs_spell(self._handle, word.encode("utf-8"))
        else:
            if self._dic_set is None:
                return True
            return self._dic_set.contains(word)

    def suggest(self, word: str) -> list[str]:
        if _USE_HUNSPELL_CTYPES:
            if self._handle is None:
                return []
            return _hs_suggest(self._handle, word.encode("utf-8"))
        else:
            return []

    def add_word(self, word: str) -> None:
        if _USE_HUNSPELL_CTYPES:
            if self._handle is not None:
                _hs_add(self._handle, word.encode("utf-8"))
        else:
            if self._dic_set is not None:
                self._dic_set.words.add(word.lower())

    def _destroy(self) -> None:
        if _USE_HUNSPELL_CTYPES and self._handle is not None:
            _hs_destroy(self._handle)
            self._handle = None
        self._dic_set = None

    def _load(self) -> None:
        lang = self._lang.replace("-", "_")
        paths = _dictionary_paths(lang)

        if _USE_HUNSPELL_CTYPES:
            for aff, dic in paths:
                if not aff.exists() or not dic.exists():
                    continue
                try:
                    handle = _hs_create(str(aff).encode("utf-8"), str(dic).encode("utf-8"))
                    if handle is not None:
                        self._handle = handle
                        _hs_spell(handle, b"test")
                        return
                except Exception:
                    self._handle = None
                    continue
        else:
            for aff, dic in paths:
                if dic.exists():
                    try:
                        self._dic_set = _DicFileWordSet(dic)
                        if self._dic_set.words:
                            return
                    except Exception:
                        self._dic_set = None
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
            # Skip chord symbols
            if re.match(r"^[A-G](#|b)?(m|maj|min|dim|aug|sus|add)?[0-9]?$", word):
                continue
            # Skip lines that look like chord lines (mostly uppercase + symbols)
            if re.match(r"^[A-G0-9#/b\s\-]+$", word):
                continue
            if not self._checker.check(word):
                self.setFormat(m.start(), m.end() - m.start(), self._fmt)


# ---------------------------------------------------------------------------
# Context-menu integration
# ---------------------------------------------------------------------------

def install_spell_checker(
    editor: QTextEdit, lang: str | None = None
) -> SpellChecker:
    """Attach a spell checker + highlighter to *editor*."""
    checker = SpellChecker(lang)
    if not checker.available:
        return checker

    highlighter = SpellHighlighter(editor.document(), checker)
    editor._spell_highlighter = highlighter
    editor._spell_checker = checker

    def _context_menu(event):
        menu = editor.createStandardContextMenu()
        cursor = editor.cursorForPosition(event.pos())
        cursor.select(QTextCursor.SelectionType.WordUnderCursor)
        word = cursor.selectedText()
        editor.setTextCursor(cursor)

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

    editor.contextMenuEvent = _context_menu
    return checker


def _replace_word(editor: QTextEdit, replacement: str) -> None:
    cursor = editor.textCursor()
    cursor.select(QTextCursor.SelectionType.WordUnderCursor)
    cursor.insertText(replacement)
    editor.setTextCursor(cursor)


def _add_word(editor: QTextEdit, checker: SpellChecker, word: str) -> None:
    checker.add_word(word)
    editor._spell_highlighter.rehighlight()


# ---------------------------------------------------------------------------
# Language menu builder
# ---------------------------------------------------------------------------

def build_language_menu(parent, editor_getter) -> QMenu:
    """Build a ``QMenu`` of available Hunspell dictionaries."""
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

def _scan_languages() -> dict[str, str]:
    """Scan for available Hunspell dictionaries and return ``{lang: label}``."""
    langs: dict[str, str] = {}

    bundled = _bundled_resources()
    if bundled and bundled.is_dir():
        for path in bundled.glob("dict-*/**/*.dic"):
            lang = path.stem
            label = _language_label(lang)
            langs[lang] = label

    if sys.platform != "win32":
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


def _default_lang() -> str:
    """Return a language code from the system locale.

    On Windows, defaults to ``es_ES`` since this app is primarily used
    by Spanish-speaking guitarists.
    """
    try:
        code, _ = locale.getlocale(locale.LC_MESSAGES)
        if code:
            code = code.replace("-", "_")
            if code.lower().startswith("es"):
                return "es_ES"
            return code
    except Exception:
        pass
    if sys.platform == "win32":
        return "es_ES"
    return "en_US"


def _bundled_resources() -> Path:
    """Return the path to the bundled resources directory."""
    module = Path(__file__).resolve().parent
    for parent in (module.parent, module.parent.parent):
        resources = parent / "resources" / "dicts"
        if resources.is_dir():
            return resources
        third_party = (
            parent
            / "third-party"
            / "libreoffice-dictionaries-collection"
            / "dicts"
        )
        if third_party.is_dir():
            return third_party
    return Path()


def _dictionary_paths(lang: str) -> list[tuple[Path, Path]]:
    """Return possible ``(aff_path, dic_path)`` pairs for *lang*."""
    bases: list[Path] = []

    if sys.platform == "win32":
        appdata = Path(os.environ.get("APPDATA", ""))
        if appdata.exists():
            bases.append(appdata / "guitarchs" / "dicts" / f"dict-{lang.split('_')[0].lower()}" / lang)
    else:
        bases.extend([
            Path(f"/usr/share/hunspell/{lang}"),
            Path(f"/usr/share/myspell/dicts/{lang}"),
            Path(f"/usr/share/hunspell/{lang.replace('_', '-')}"),
        ])

    bundled = _bundled_resources()
    if bundled:
        prefix = f"dict-{lang.split('_')[0].lower()}"
        bases.append(bundled / prefix / lang)

    return [(b.with_suffix(".aff"), b.with_suffix(".dic")) for b in bases]


__all__ = [
    "SpellChecker",
    "SpellHighlighter",
    "install_spell_checker",
    "build_language_menu",
]
