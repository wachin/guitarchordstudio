"""Tests for the GuitarChordStudio chord and marker token filter."""

from __future__ import annotations

import pytest

from pyqt6_linguistic_tools import UnicodeTokenizer, WordToken

from chordflow.chord_token_filter import is_chord_token
from chordflow.chord_transposer import is_chord_symbol
from chordflow.tests.documents import ROADMAP_DOCUMENT, SPANISH_LYRIC_WORDS


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

# The realistic lyrics-and-chords document required by roadmap Phase 38 lives in
# ``chordflow.tests.documents`` so the acceptance test uses the same source.


def _token(word: str) -> WordToken:
    return WordToken(
        text=word,
        start=0,
        end=len(word),
        utf16_start=0,
        utf16_end=len(word),
    )


def _kept_words(text: str) -> list[str]:
    tokenizer = UnicodeTokenizer(token_filters=(is_chord_token,))
    return [token.text for token in tokenizer.iter_tokens(text)]


class TestChordGrammar:
    @pytest.mark.parametrize("chord", CHORD_SYMBOLS)
    def test_recognizes_known_chords(self, chord: str) -> None:
        assert is_chord_symbol(chord) is True, f"{chord!r} should match"

    @pytest.mark.parametrize("word", REGULAR_WORDS)
    def test_rejects_regular_words(self, word: str) -> None:
        assert is_chord_symbol(word) is False, f"{word!r} should not match"

    def test_rejects_empty_string(self) -> None:
        assert is_chord_symbol("") is False


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


class TestTokenizerPipeline:
    """The filter must survive the tokenizer splitting chords on '#'."""

    def test_no_chord_fragments_reach_spellcheck(self) -> None:
        kept = _kept_words(ROADMAP_DOCUMENT)
        # ``A#m`` tokenizes as ``A`` + ``m``: the fragment must be excluded too.
        assert "m" not in kept
        for chord in ("A", "A#m", "G#", "F#", "C#", "B", "G"):
            assert chord not in kept, f"{chord!r} leaked to spell checking"

    def test_section_markers_are_excluded(self) -> None:
        kept = _kept_words(ROADMAP_DOCUMENT)
        for marker in ("INTRO", "VERSE"):
            assert marker not in kept
        # ``X3`` is a repeat count, not a word.
        assert "X3" not in kept

    def test_lyric_words_are_kept(self) -> None:
        kept = _kept_words(ROADMAP_DOCUMENT)
        for word in SPANISH_LYRIC_WORDS:
            assert word in kept, f"{word!r} should be kept"

    def test_only_lyric_and_marker_free_tokens_survive(self) -> None:
        kept = _kept_words(ROADMAP_DOCUMENT)
        assert kept == SPANISH_LYRIC_WORDS


class TestStructuralMarkers:
    @pytest.mark.parametrize(
        "marker",
        ["INTRO", "VERSE", "CHORUS", "BRIDGE", "OUTRO", "PUENTE", "CORO", "X3", "x2"],
    )
    def test_uppercase_markers_are_excluded(self, marker: str) -> None:
        assert is_chord_token(_token(marker), "") is False

    def test_lowercase_marker_on_structural_line_is_excluded(self) -> None:
        text = "Intro: A#m  G#  F#"
        token = WordToken("Intro", 0, 5, 0, 5)
        assert is_chord_token(token, text) is False

    def test_lowercase_marker_inside_lyric_is_kept(self) -> None:
        text = "Solo tú y yo"
        token = WordToken("Solo", 0, 4, 0, 4)
        assert is_chord_token(token, text) is True

    def test_spanish_word_coro_inside_lyric_is_kept(self) -> None:
        text = "Coro de ángeles"
        token = WordToken("Coro", 0, 4, 0, 4)
        assert is_chord_token(token, text) is True

    def test_marker_with_trailing_colon_is_excluded(self) -> None:
        text = "Chorus:"
        token = WordToken("Chorus", 0, 6, 0, 6)
        assert is_chord_token(token, text) is False
