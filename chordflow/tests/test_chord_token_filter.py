"""Tests for the GuitarChordStudio chord token filter."""

from __future__ import annotations

import pytest

from pyqt6_linguistic_tools import WordToken

from chordflow.chord_token_filter import _CHORD_RE, is_chord_token


# Known chord symbols that should be excluded from spell checking
CHORD_SYMBOLS = [
    "A",
    "Am",
    "A#m",
    "Bb",
    "C#m7",
    "Fmaj7",
    "Gsus4",
    "D/F#",
    "Cadd9",
    "Dm",
    "Em",
    "E7",
    "G7",
    "Am7",
    "Bdim",
    "Caug",
    "Dmaj7",
    "Ebm",
    "F#m",
    "G#",
    "A7sus4",
    "Dm7b5",
    "Cmaj9",
    "F13",
    "Gdim7",
    "Aaug",
    "Bb/D",
    "C/E",
    "F/A",
    "G/B",
    "Am/G",
    "Dm/F",
    "E/G#",
    "F#m/A",
    "Bm7b5",
    "Cm7",
    "Dbmaj7",
    "Ebm7",
    "Fmaj9",
    "Abmaj7",
    "Bbm7",
    "D#m",
    "G#m",
    "A#dim",
    "C#",
    "F#",
    "G#m7",
    "A#m7",
    "D#dim",
]

# Regular words that should be kept for spell checking
REGULAR_WORDS = [
    "hello",
    "world",
    "am",  # lowercase "am" is not a chord
    "bed",  # "bed" is not a chord (though it starts with B, e, d)
    "add",  # "add" is a word, not a chord
    "dim",  # "dim" is a word
    "maj",  # "maj" is a word
    "sus",  # "sus" is a word
    "guitar",
    "casa",
    "música",
    "canción",
    "Señor",
    "Straße",
    "français",
    "d'Artagnan",
    "O'Connor",
    "rock-n-roll",
]


def _token(word: str) -> WordToken:
    return WordToken(
        text=word,
        start=0,
        end=len(word),
        utf16_start=0,
        utf16_end=len(word),
    )


class TestChordPattern:
    @pytest.mark.parametrize("chord", CHORD_SYMBOLS)
    def test_chord_pattern_matches_known_chords(self, chord: str) -> None:
        assert _CHORD_RE.fullmatch(chord) is not None, f"{chord!r} should match"

    @pytest.mark.parametrize("word", REGULAR_WORDS)
    def test_chord_pattern_rejects_regular_words(self, word: str) -> None:
        assert _CHORD_RE.fullmatch(word) is None, f"{word!r} should not match"


class TestIsChordToken:
    @pytest.mark.parametrize("chord", CHORD_SYMBOLS)
    def test_excludes_chords(self, chord: str) -> None:
        token = _token(chord)
        assert is_chord_token(token, "") is False, f"{chord!r} should be excluded"

    @pytest.mark.parametrize("word", REGULAR_WORDS)
    def test_keeps_regular_words(self, word: str) -> None:
        token = _token(word)
        assert is_chord_token(token, "") is True, f"{word!r} should be kept"

    def test_keeps_numbers(self) -> None:
        assert is_chord_token(_token("123"), "") is True

    def test_chord_a_is_excluded(self) -> None:
        """Single letter 'A' is a chord symbol and should be excluded."""
        assert is_chord_token(_token("A"), "") is False


class TestIntegrationAcceptance:
    """Integration acceptance test with a realistic lyrics-and-chords document."""

    SAMPLE_DOCUMENT = """\
INTRO X3
A#m   G#   F#

VERSE
C#       G#       A#m      G#    F#
Siento   un       vacío    en    mí

CHORUS
A#m      G#       F#       G#
Nunca    pensé    llegar   hasta  aquí
"""

    def test_chord_lines_are_not_sent_to_spellcheck(self) -> None:
        """Verify that tokens in chord lines are excluded by the filter."""
        for line in self.SAMPLE_DOCUMENT.split("\n"):
            if not line.strip():
                continue
            tokens = line.split()
            for token_text in tokens:
                token = _token(token_text)
                # Chord lines contain mostly chord symbols
                chord_count = sum(
                    1 for t in tokens if _CHORD_RE.fullmatch(t)
                )
                is_chord_line = chord_count > len(tokens) / 2
                if is_chord_line and _CHORD_RE.fullmatch(token_text):
                    # This token is a chord symbol in a chord line
                    assert is_chord_token(token, "") is False, (
                        f"{token_text!r} should be excluded"
                    )

    def test_lyric_words_are_sent_to_spellcheck(self) -> None:
        """Verify that tokens in lyric lines are kept by the filter."""
        for line in self.SAMPLE_DOCUMENT.split("\n"):
            if not line.strip():
                continue
            tokens = line.split()
            chord_count = sum(1 for t in tokens if _CHORD_RE.fullmatch(t))
            is_chord_line = chord_count > len(tokens) / 2
            if not is_chord_line:
                for token_text in tokens:
                    if token_text.isupper() and len(token_text) > 1:
                        continue  # Skip section markers like INTRO, VERSE, CHORUS
                    token = _token(token_text)
                    if token_text not in ("un", "en", "mi", "a"):
                        assert is_chord_token(token, "") is True, (
                            f"{token_text!r} should be kept"
                        )