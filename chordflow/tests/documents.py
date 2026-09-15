"""Shared realistic documents for the GuitarChordStudio integration tests."""

from __future__ import annotations

# Realistic lyrics-and-chords document required by roadmap Phase 38. It mixes
# section markers, repeat counts, chord lines (with sharps and slash basses) and
# ordinary Spanish lyrics.
ROADMAP_DOCUMENT = """\
INTRO X3
A#m   G#   F#

VERSE
C#       G#       A#m      G#    F#
Mi Cristo, mi Rey, nadie es como tú
C#       F#       G#
Toda mi vida, quiero exaltar,
A#m      B        G#
las maravillas de tu amor
"""

# Ordinary Spanish words in the document that must reach the dictionary, in
# source order (``mi`` intentionally appears twice, once per lyric line).
SPANISH_LYRIC_WORDS = [
    "Mi",
    "Cristo",
    "mi",
    "Rey",
    "nadie",
    "es",
    "como",
    "tú",
    "Toda",
    "mi",
    "vida",
    "quiero",
    "exaltar",
    "las",
    "maravillas",
    "de",
    "tu",
    "amor",
]

__all__ = ["ROADMAP_DOCUMENT", "SPANISH_LYRIC_WORDS"]
