"""Spell-checking support for ChordPages.

Uses the shared :mod:`pyqt6_linguistic_tools` ``LinguisticService`` and
``LinguisticTextEditDecorator``. The toolkit is the only implementation path;
there is no silent fallback to ChordFlow's legacy spell checker.
"""

from __future__ import annotations

import logging
import os
import sys
from pathlib import Path
from typing import TYPE_CHECKING

# Support a libs/pyqt6-linguistic-tools git submodule without pip.
_TOOLKIT_ROOT = (
    Path(__file__).resolve().parent.parent / "libs" / "pyqt6-linguistic-tools"
)
if _TOOLKIT_ROOT.is_dir():
    _toolkit_text = str(_TOOLKIT_ROOT)
    if _toolkit_text not in sys.path:
        sys.path.insert(0, _toolkit_text)
    import pyqt6_linguistic_tools_bootstrap  # noqa: F401

from PyQt6.QtGui import QActionGroup
from PyQt6.QtWidgets import QMenu

if TYPE_CHECKING:
    from pyqt6_linguistic_tools import LinguisticService


logger = logging.getLogger(__name__)

# Attempt to import the toolkit's enhanced integration.
try:
    from pyqt6_linguistic_tools import create_service
    from pyqt6_linguistic_tools.qt import (
        LinguisticAction,
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
        repo_root / "third-party" / "libreoffice-dictionaries-collection" / "dicts",
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
    """Attach the toolkit decorator or report that the toolkit is unavailable."""
    del lang  # The shared service owns the active language.
    if not _HAS_TOOLKIT or LinguisticTextEditDecorator is None:
        logger.error("pyqt6-linguistic-tools is not available")
        return None
    try:
        service = get_linguistic_service()
    except Exception:
        logger.exception("Could not create the linguistic service")
        return None
    decorator = LinguisticTextEditDecorator(editor, service)
    decorator.context_menu.set_action_enabled(LinguisticAction.LANGUAGE, False)
    editor._linguistic_decorator = decorator
    return decorator


def _unavailable_menu(parent, label) -> QMenu:
    menu = QMenu(label("Language"), parent)
    action = menu.addAction(label("Dictionaries are unavailable."))
    action.setEnabled(False)
    return menu


def _source_label(source: str | None, label) -> str:
    names = {
        "system": label("system"),
        "corpus": label("bundled"),
        "managed": label("managed"),
        "user": label("user"),
    }
    if source in names:
        return names[source]
    return source or label("unknown")


def build_language_menu(parent, editor_getter):
    """Build the language menu from the shared toolkit service.

    Each capability reports where its dictionary came from (system, bundled
    corpus, managed download or user import), which makes Linux discovery and
    packaging problems visible instead of silently falling back.
    """
    translate = getattr(parent, "tr", None)

    def label(text: str) -> str:
        return translate(text) if callable(translate) else text

    if not _HAS_TOOLKIT:
        logger.error("pyqt6-linguistic-tools is not available")
        return _unavailable_menu(parent, label)

    try:
        service = get_linguistic_service()
    except Exception:
        logger.exception("Could not create the linguistic service")
        return _unavailable_menu(parent, label)

    menu = QMenu(label("Language"), parent)
    try:
        available = service.available_languages()
    except Exception:
        logger.exception("Could not list available languages")
        return _unavailable_menu(parent, label)
    if not available:
        action = menu.addAction(label("(no dictionaries)"))
        action.setEnabled(False)
        return menu

    group = QActionGroup(menu)
    group.setExclusive(True)
    current = service.language
    for locale in available:
        try:
            capabilities = service.capabilities(locale)
        except Exception:
            logger.exception("Could not read capabilities for %s", locale)
            continue
        parts: list[str] = []
        if capabilities.spell_check:
            parts.append(
                f"{label('Spelling')} "
                f"({_source_label(capabilities.spelling_source, label)})"
            )
        if capabilities.thesaurus:
            parts.append(
                f"{label('Thesaurus')} "
                f"({_source_label(capabilities.thesaurus_source, label)})"
            )
        text = f"{locale} — {' + '.join(parts)}" if parts else locale
        action = menu.addAction(text)
        action.setData(locale)
        action.setCheckable(True)
        action.setChecked(locale == current)
        action.triggered.connect(
            lambda _checked=False, value=locale: service.set_language(value)
        )
        group.addAction(action)
    if not menu.actions():
        return _unavailable_menu(parent, label)
    return menu


__all__ = [
    "LinguisticTextEditDecorator",
    "ThesaurusDialog",
    "build_language_menu",
    "create_linguistic_service",
    "get_linguistic_service",
    "install_spell_checker",
]
