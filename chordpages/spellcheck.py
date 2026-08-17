"""Spell-checking support for ChordPages via system Hunspell dictionaries.

Re-exports ``SpellChecker``, ``SpellHighlighter`` and ``install_spell_checker``
from the shared :mod:`chordflow.spellcheck` module.
"""

from __future__ import annotations

from chordflow.spellcheck import SpellChecker, SpellHighlighter, install_spell_checker

__all__ = [
    "SpellChecker",
    "SpellHighlighter",
    "install_spell_checker",
]