"""Spell-checking support for ChordPages.

Uses the shared :mod:`pyqt6_linguistic_tools` ``LinguisticService`` and
``LinguisticTextEditDecorator`` when the toolkit is available, with the legacy
:mod:`chordflow.spellcheck` implementation as a fallback.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import TYPE_CHECKING

# Support a libs/pyqt6-linguistic-tools git submodule without pip.
_TOOLKIT_ROOT = (
    Path(__file__).resolve().parent.parent
    / "libs"
    / "pyqt6-linguistic-tools"
)
if _TOOLKIT_ROOT.is_dir():
    _toolkit_text = str(_TOOLKIT_ROOT)
    if _toolkit_text not in sys.path:
        sys.path.insert(0, _toolkit_text)
    import pyqt6_linguistic_tools_bootstrap  # noqa: F401

from PyQt6.QtGui import QActionGroup
from PyQt6.QtWidgets import QMenu

from chordflow.spellcheck import (
    SpellChecker,
    SpellHighlighter,
    build_language_menu as _build_legacy_language_menu,
    install_spell_checker as _install_legacy_spell_checker,
)

if TYPE_CHECKING:
    from pyqt6_linguistic_tools import LinguisticService

# Attempt to import the toolkit's enhanced integration.
try:
    from pyqt6_linguistic_tools import create_service
    from pyqt6_linguistic_tools.qt import (
        LinguisticTextEditDecorator,
        ThesaurusDialog,
    )

    _HAS_TOOLKIT = True
except ImportError:
    _HAS_TOOLKIT = False
    LinguisticTextEditDecorator = None  # type: ignore[assignment,misc]
    ThesaurusDialog = None  # type: ignore[assignment,misc]
    create_service = None  # type: ignore[assignment]


_SERVICE: "LinguisticService | None" = None


def _corpus_root() -> Path | None:
    """Return an optional local LibreOffice corpus for development builds."""
    repo_root = Path(__file__).resolve().parent.parent
    for candidate in (
        repo_root
        / "third-party"
        / "libreoffice-dictionaries-collection"
        / "dicts",
        repo_root / "resources" / "dicts",
    ):
        if candidate.is_dir():
            return candidate
    environment = os.environ.get("LIBREOFFICE_DICTIONARIES_PATH")
    if environment:
        candidate = Path(environment).expanduser().resolve()
        if candidate.is_dir():
            return candidate
    return None


def create_linguistic_service(
    *,
    language: str | None = None,
) -> "LinguisticService":
    """Create the shared GuitarChordStudio service without ChordFlow imports."""
    if not _HAS_TOOLKIT or create_service is None:
        raise RuntimeError("pyqt6-linguistic-tools is not available")
    return create_service(
        language=language,
        namespace="guitarchordstudio",
        corpus_path=_corpus_root(),
    )


def get_linguistic_service() -> "LinguisticService":
    """Return the process-wide toolkit service used by every page editor."""
    global _SERVICE
    if _SERVICE is None:
        _SERVICE = create_linguistic_service()
    return _SERVICE


def install_spell_checker(editor, lang: str | None = None):
    """Attach the toolkit decorator, or the legacy checker as a fallback."""
    if _HAS_TOOLKIT and LinguisticTextEditDecorator is not None:
        try:
            service = get_linguistic_service()
        except Exception:
            return _install_legacy_spell_checker(editor, lang)
        decorator = LinguisticTextEditDecorator(editor, service)
        editor._linguistic_decorator = decorator
        return decorator
    return _install_legacy_spell_checker(editor, lang)


def build_language_menu(parent, editor_getter):
    """Build the language menu from the shared toolkit service."""
    if not _HAS_TOOLKIT:
        return _build_legacy_language_menu(parent, editor_getter)

    try:
        service = get_linguistic_service()
    except Exception:
        return _build_legacy_language_menu(parent, editor_getter)

    translate = getattr(parent, "tr", None)

    def label(text: str) -> str:
        return translate(text) if callable(translate) else text

    menu = QMenu(label("Language"), parent)
    available = service.available_languages()
    if not available:
        action = menu.addAction(label("(no dictionaries)"))
        action.setEnabled(False)
        return menu

    group = QActionGroup(menu)
    group.setExclusive(True)
    current = service.language
    for locale in available:
        capabilities = service.capabilities(locale)
        capability_text = ""
        if capabilities.spell_check:
            capability_text = label("Spelling")
        if capabilities.thesaurus:
            capability_text += (
                (" + " if capability_text else "") + label("Thesaurus")
            )
        text = f"{locale} — {capability_text}" if capability_text else locale
        action = menu.addAction(text)
        action.setData(locale)
        action.setCheckable(True)
        action.setChecked(locale == current)
        action.triggered.connect(
            lambda _checked=False, value=locale: service.set_language(value)
        )
        group.addAction(action)
    return menu


__all__ = [
    "SpellChecker",
    "SpellHighlighter",
    "LinguisticTextEditDecorator",
    "ThesaurusDialog",
    "build_language_menu",
    "create_linguistic_service",
    "get_linguistic_service",
    "install_spell_checker",
]
