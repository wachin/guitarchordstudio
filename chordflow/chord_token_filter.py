"""Chord token filter for the pyqt6-linguistic-tools tokenizer.

Provides a ``TokenFilter``-compatible function that excludes chord symbols
from spell checking. Uses the existing chord grammar from
:mod:`chordflow.chord_transposer` to recognize chord symbols such as
``A``, ``Am``, ``C#m7``, ``D/F#``, ``Fmaj7``, ``Gsus4``, and ``Cadd9``.
"""

from __future__ import annotations

import re
import sys
import unicodedata
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


from pyqt6_linguistic_tools import TokenFilter, WordToken  # noqa: E402

# Reuse the chord grammar from chord_transposer.
# Matches chord symbols: root note (A-G) + optional accidental (#/b)
# + optional quality (m, maj, min, dim, aug, sus, add, M, M7, dom)
# + optional extension number (2-13)
# + optional alterations (sus4, b5, #5, add9, etc.)
# + optional slash chord bass note (/A, /F#, etc.)
_CHORD_RE = re.compile(
    r"\b[A-G](#|b)?"
    r"(?:maj|min|dim|aug|sus|add|m|M|M7|dom)?"
    r"(?:[0-9]|1[0-3])?"
    r"(?:sus[0-9]|b[0-9]|#[0-9]|add[0-9])*"
    r"(?:/[A-G](#|b)?)?"
    r"(?!\w)"
)


def is_chord_token(token: WordToken, _text: str) -> bool:
    """Return ``True`` to keep *token* (not a chord) or ``False`` to exclude it.

    This function is a ``TokenFilter`` — it can be passed to
    :meth:`LinguisticTextEditDecorator.add_token_filter` or included in
    the ``token_filters`` constructor parameter.

    Args:
        token: The word token being evaluated.
        _text: The full document text (unused by this filter).

    Returns:
        ``True`` if the token is a regular word (keep it),
        ``False`` if it matches a chord symbol (exclude from spell checking).
    """
    word = token.text

    # Skip pure numbers
    if word.isdigit():
        return True

    # Check against the chord pattern
    if _CHORD_RE.fullmatch(word):
        return False

    return True


__all__ = [
    "_CHORD_RE",
    "is_chord_token",
]