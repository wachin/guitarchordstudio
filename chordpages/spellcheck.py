"""Spell-checking support for ChordPages.

Re-exports from the shared :mod:`chordflow.spellcheck` module. When the
pyqt6-linguistic-tools toolkit is available, uses the toolkit's
``LinguisticService`` and ``LinguisticTextEditDecorator`` instead.
"""

from __future__ import annotations

from chordflow.spellcheck import (
    SpellChecker,
    SpellHighlighter,
    build_language_menu,
    install_spell_checker,
)

# Attempt to import the toolkit's enhanced integration
try:
    from pyqt6_linguistic_tools.qt import (
        LinguisticTextEditDecorator,
        ThesaurusDialog,
    )
    from chordflow.linguistic_service import create_linguistic_service

    _HAS_TOOLKIT = True
except ImportError:
    _HAS_TOOLKIT = False


__all__ = [
    "SpellChecker",
    "SpellHighlighter",
    "LinguisticTextEditDecorator",
    "ThesaurusDialog",
    "build_language_menu",
    "create_linguistic_service",
    "install_spell_checker",
]