"""Chord transposition logic for ChordFlow."""

from __future__ import annotations

import re


CHORD_BASE = [
    ["C"],
    ["C#", "Db"],
    ["D"],
    ["D#", "Eb"],
    ["E"],
    ["F"],
    ["F#", "Gb"],
    ["G"],
    ["G#", "Ab"],
    ["A"],
    ["A#", "Bb"],
    ["B"],
]

CHORD_PATTERN = re.compile(r"\b[A-G](#|b)?(m|maj|min|dim|aug|sus|add)?[0-9]?(?!\w)")

# Single source of truth for *chord-symbol recognition*. ``CHORD_PATTERN`` above
# stays deliberately narrow because transposition splits a chord into root,
# accidental and suffix; recognition needs the complete chord vocabulary
# (qualities, extensions, alterations and slash basses) so that spell checking
# never receives a chord fragment.
#
# Matches: root note (A-G) + optional accidental (#/b)
# + optional quality (m, maj, min, dim, aug, sus, add, M, M7, dom)
# + optional extension number (2-13)
# + optional alterations (sus4, b5, #5, add9, ...)
# + optional slash-chord bass note (/A, /F#, ...)
CHORD_SYMBOL_PATTERN = re.compile(
    r"\b[A-G](#|b)?"
    r"(?:maj|min|dim|aug|sus|add|m|M|M7|dom)?"
    r"(?:[0-9]|1[0-3])?"
    r"(?:sus[0-9]|b[0-9]|#[0-9]|add[0-9])*"
    r"(?:/[A-G](#|b)?)?"
    r"(?!\w)"
)


def is_chord_symbol(text: str) -> bool:
    """Return True when *text* is exactly one chord symbol.

    Recognizes the same symbols as :data:`CHORD_SYMBOL_PATTERN`, for example
    ``A``, ``Am``, ``A#m``, ``Bb``, ``C#m7``, ``Fmaj7``, ``Gsus4``, ``D/F#`` and
    ``Cadd9``. This is the shared recognizer used by the spell-check token
    filter in :mod:`chordflow.chord_token_filter`.
    """
    if not text:
        return False
    return CHORD_SYMBOL_PATTERN.fullmatch(text) is not None


def is_chord_line(line: str) -> bool:
    """Return True if more than half of the words in *line* look like chords."""
    words = line.split()
    if not words:
        return False
    matches = [bool(re.fullmatch(CHORD_PATTERN.pattern, word)) for word in words]
    return sum(matches) > len(words) / 2


def transpose_chord(chord: str, semitones: int, use_sharps: bool) -> str:
    """Transpose a single chord name by *semitones* steps."""
    root = chord[0]
    accidental = "#" if "#" in chord else "b" if "b" in chord else ""
    suffix = chord[len(root + accidental) :]
    current_index = next(
        i for i, group in enumerate(CHORD_BASE) if root + accidental in group
    )
    new_index = (current_index + semitones) % len(CHORD_BASE)
    new_root = (
        CHORD_BASE[new_index][0] if use_sharps else CHORD_BASE[new_index][-1]
    )
    return new_root + suffix


def transpose_text(text: str, semitones: int, use_sharps: bool) -> str:
    """Transpose every chord line in *text* by *semitones* steps.

    A line is considered a chord line when more than half of its words
    match the chord pattern (preserves alignment via spaces).
    """
    lines = text.split("\n")
    transposed: list[str] = []

    for line in lines:
        if not is_chord_line(line):
            transposed.append(line)
            continue

        positions = list(re.finditer(CHORD_PATTERN, line))
        if not positions:
            transposed.append(line)
            continue

        parts: list[str] = []
        last_end = 0

        for i, match in enumerate(positions):
            parts.append(line[last_end : match.start()])
            next_pos = positions[i + 1].start() if i + 1 < len(positions) else len(line)
            spaces = next_pos - match.end()
            new_chord = transpose_chord(match.group(), semitones, use_sharps)
            parts.append(new_chord + " " * spaces)
            last_end = next_pos

        parts.append(line[last_end:])
        transposed.append("".join(parts))

    return "\n".join(transposed)


__all__ = [
    "CHORD_BASE",
    "CHORD_PATTERN",
    "CHORD_SYMBOL_PATTERN",
    "is_chord_line",
    "is_chord_symbol",
    "transpose_chord",
    "transpose_text",
]
