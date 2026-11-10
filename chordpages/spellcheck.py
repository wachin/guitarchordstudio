"""Spell-checking support for ChordPages.

Uses the shared :mod:`pyqt6_linguistic_tools` ``LinguisticService`` and
``LinguisticTextEditDecorator`` when the toolkit is available, with the legacy
:mod:`chordflow.spellcheck` implementation as a fallback.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

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
    from pyqt6_linguistic_tools.qt import (
        LinguisticTextEditDecorator,
        ThesaurusDialog,
    )
    from chordflow.linguistic_service import create_linguistic_service

    _HAS_TOOLKIT = True
except ImportError:
    _HAS_TOOLKIT = False
    LinguisticTextEditDecorator = None  # type: ignore[assignment,misc]
    ThesaurusDialog = None  # type: ignore[assignment,misc]
    create_linguistic_service = None  # type: ignore[assignment]


_SERVICE: "LinguisticService | None" = None


def get_linguistic_service() -> "LinguisticService":
    """Return the process-wide toolkit service used by every page editor."""
    global _SERVICE
    if _SERVICE is None:
        if not _HAS_TOOLKIT or create_linguistic_service is None:
            raise RuntimeError("pyqt6-linguistic-tools is not available")
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
