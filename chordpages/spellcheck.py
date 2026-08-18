"""Spell-checking support for ChordPages via system Hunspell dictionaries.

Re-exports from the shared :mod:`chordflow.spellcheck` module.
"""

from __future__ import annotations

from chordflow.spellcheck import (
    SpellChecker,
    SpellHighlighter,
    build_language_menu,
    install_spell_checker,
)

__all__ = [
    "SpellChecker",
    "SpellHighlighter",
    "build_language_menu",
    "install_spell_checker",
]