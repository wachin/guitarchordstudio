"""Chord and structural-marker token filter for the toolkit tokenizer.

Provides a ``TokenFilter``-compatible function that excludes GuitarChordStudio
chord symbols and non-word structural markers (section labels and repeat
counts) from spell checking. Chord recognition reuses the shared grammar in
:mod:`chordflow.chord_transposer`; this module does not define a second chord
pattern.

The toolkit tokenizer splits ``A#m`` into the tokens ``A`` and ``m`` because
``#`` is not a word character. A per-token regular expression alone would
therefore let the ``m`` fragment reach Spylls, so the filter inspects the
surrounding whitespace-delimited chunk through the token's source offsets from
the full document text passed by the tokenizer.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path


# Ensure the pyqt6-linguistic-tools toolkit is on the Python path.
_repo_root = Path(__file__).resolve().parent.parent
_toolkit_root = _repo_root / "libs" / "pyqt6-linguistic-tools"
for _path in [
    str(_toolkit_root / "src"),
    str(_toolkit_root / "libs" / "spylls"),
    str(_toolkit_root / "libs" / "pythes"),
]:
    if _path not in sys.path:
        sys.path.insert(0, _path)


from pyqt6_linguistic_tools import WordToken  # noqa: E402

from .chord_transposer import is_chord_symbol  # noqa: E402


# Punctuation that may surround a chunk in a chord chart (``Intro:``, ``(x4)``,
# ``A#m,``). It is stripped only for recognition; the source text is untouched.
_CHUNK_EDGE_PUNCTUATION = ".,;:!?¡¿()[]{}<>\"'`|*_–—…"

# Section labels used by GuitarChordStudio chord charts. They are structure, not
# words, and must never be spell checked.
_MARKER_KEYWORDS = frozenset(
    {
        # English
        "intro",
        "outro",
        "verse",
        "chorus",
        "bridge",
        "pre-chorus",
        "prechorus",
        "refrain",
        "hook",
        "solo",
        "interlude",
        "instrumental",
        "coda",
        "tag",
        "vamp",
        "turnaround",
        "ending",
        "repeat",
        # Spanish
        "estrofa",
        "coro",
        "estribillo",
        "puente",
        "precoro",
        "pre-coro",
        "introduccion",
        "introducción",
        "interludio",
        "final",
        "repeticion",
        "repetición",
    }
)

# Repeat/play counts such as ``X3``, ``x2`` or ``(x4)``.
_REPEAT_MARKER_PATTERN = re.compile(r"\(?[xX]\d+\)?")


def _clean(value: str) -> str:
    """Strip chart punctuation from both ends of *value*."""
    return value.strip(_CHUNK_EDGE_PUNCTUATION)


def _source_chunk(text: str, token: WordToken) -> str:
    """Return the whitespace-delimited chunk of *text* containing *token*."""
    if not isinstance(text, str) or not text:
        return ""
    start, end = token.start, token.end
    if not 0 <= start <= end <= len(text):
        return ""
    left = start
    while left > 0 and not text[left - 1].isspace():
        left -= 1
    right = end
    while right < len(text) and not text[right].isspace():
        right += 1
    return text[left:right]


def _source_line(text: str, token: WordToken) -> str | None:
    """Return the source line containing *token*, or ``None`` without context."""
    if not isinstance(text, str) or not text:
        return None
    start, end = token.start, token.end
    if not 0 <= start <= end <= len(text):
        return None
    line_start = text.rfind("\n", 0, start) + 1
    line_end = text.find("\n", end)
    if line_end == -1:
        line_end = len(text)
    return text[line_start:line_end]


def _is_structural_line(line: str) -> bool:
    """Return True when *line* contains only markers, repeats or chord symbols."""
    words = line.split()
    if not words:
        return False
    for word in words:
        candidate = _clean(word)
        if not candidate or _REPEAT_MARKER_PATTERN.fullmatch(candidate):
            continue
        if candidate.casefold() in _MARKER_KEYWORDS:
            continue
        if is_chord_symbol(candidate):
            continue
        return False
    return True


def _is_marker(chunk: str, line: str | None) -> bool:
    """Return True when *chunk* is a structural marker rather than a word.

    Uppercase labels (``INTRO``, ``VERSE``) are recognized directly. Lowercase
    or mixed-case labels are only ignored when their whole line contains nothing
    but markers, repeats and chords, so an ordinary lyric such as ``Solo tú``
    keeps ``Solo`` as a real word.
    """
    candidate = _clean(chunk)
    if not candidate:
        return False
    if _REPEAT_MARKER_PATTERN.fullmatch(candidate):
        return True
    if candidate.casefold() not in _MARKER_KEYWORDS:
        return False
    if candidate.isupper():
        return True
    return line is not None and _is_structural_line(line)


def is_chord_token(token: WordToken, text: str) -> bool:
    """Return ``True`` to keep *token* (a real word) or ``False`` to exclude it.

    This function is a ``TokenFilter`` — it can be passed to
    :meth:`LinguisticTextEditDecorator.add_token_filter` or included in
    the ``token_filters`` constructor parameter.

    A token is excluded when it belongs to a chord symbol, a section marker or
    a repeat count. Numbers are kept so a host dictionary or the toolkit decides
    what to do with them.

    Args:
        token: The word token being evaluated.
        text: The full document (or block) text the token came from.

    Returns:
        ``True`` if the token is a regular word (keep it),
        ``False`` if it is chord or structural markup (exclude from spell
        checking).
    """
    word = token.text

    # Skip pure numbers
    if word.isdigit():
        return True

    chunk = _source_chunk(text, token) or word
    if is_chord_symbol(_clean(chunk)):
        return False
    if _is_marker(chunk, _source_line(text, token)):
        return False

    return True


__all__ = ["is_chord_token"]
