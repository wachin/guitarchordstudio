"""Chord token filter for the page editor's spelling highlighter.

Chord symbols are markup, not lyrics. The toolkit tokenizer splits ``F#m`` into
``F`` and ``m``, so this filter inspects the surrounding chunk rather than only
the individual token.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from chordpages.document.chordpro import CHORD_SYMBOL_RE, TOKEN_EDGE_PUNCTUATION

if TYPE_CHECKING:
    from pyqt6_linguistic_tools import WordToken


_CHUNK_EDGE_PUNCTUATION = TOKEN_EDGE_PUNCTUATION + ".,;:!?¡¿<>\"'`|*_–—…"


def _source_chunk(text: str, token: "WordToken") -> str:
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


def is_chord_token(token: "WordToken", text: str) -> bool:
    """Return False for chord symbols and True for ordinary lyric words."""
    word = token.text
    if word.isdigit():
        return True
    chunk = _source_chunk(text, token) or word
    candidate = chunk.strip(_CHUNK_EDGE_PUNCTUATION)
    if candidate and CHORD_SYMBOL_RE.fullmatch(candidate):
        return False
    return True


__all__ = ["is_chord_token"]
