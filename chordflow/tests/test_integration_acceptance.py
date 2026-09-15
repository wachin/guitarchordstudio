"""End-to-end acceptance test for the GuitarChordStudio integration (Phase 38).

This test runs the roadmap's realistic lyrics-and-chords document through the
same pipeline the Qt decorator uses: the toolkit tokenizer with the
GuitarChordStudio token filter, followed by ``LinguisticService.check_word``
against a real pinned Spanish dictionary read by Spylls.

It verifies the still-open Phase 38 acceptance criteria that can be checked on
Linux:

- chords and non-word markers are ignored while ordinary Spanish words are
  checked against the active dictionary;
- a misspelling such as ``marabillas`` exposes the suggestions of the active
  dictionary, including ``maravillas`` when that dictionary provides it.

Windows and macOS verification stays unchecked in the roadmap because those
platforms cannot be exercised from this checkout.
"""

from __future__ import annotations

import os
from pathlib import Path

import pytest

from pyqt6_linguistic_tools import (
    DictionaryRegistry,
    DictionarySourcePriority,
    DirectoryDictionaryProvider,
    LinguisticService,
    UnicodeTokenizer,
)

from chordflow.chord_token_filter import is_chord_token
from chordflow.chord_transposer import is_chord_symbol
from chordflow.tests.documents import ROADMAP_DOCUMENT, SPANISH_LYRIC_WORDS


def _dictionary_directory() -> Path | None:
    """Return a directory holding ``es_ES.aff``/``es_ES.dic``, or ``None``.

    Search order mirrors the toolkit's configurable corpus policy: an explicit
    environment override first, then the bundled LibreOffice collection, then
    the Linux system dictionary directory.
    """
    candidates: list[Path] = []
    override = os.environ.get("LIBREOFFICE_DICTIONARIES_PATH")
    if override:
        candidates.append(Path(override).expanduser())
    repository = Path(__file__).resolve().parents[2]
    collection = (
        repository / "third-party" / "libreoffice-dictionaries-collection" / "dicts"
    )
    candidates.extend([collection / "dict-es", collection])
    candidates.append(Path("/usr/share/hunspell"))

    for candidate in candidates:
        if not candidate.is_dir():
            continue
        if (candidate / "es_ES.aff").is_file() and (candidate / "es_ES.dic").is_file():
            return candidate
    return None


@pytest.fixture(scope="module")
def spanish_service() -> LinguisticService:
    """A ``LinguisticService`` pinned to one real Spanish dictionary."""
    directory = _dictionary_directory()
    if directory is None:
        pytest.skip(
            "no es_ES dictionary available; set LIBREOFFICE_DICTIONARIES_PATH to "
            "the LibreOffice collection dicts directory to run this acceptance test"
        )
    provider = DirectoryDictionaryProvider(
        directory,
        source="guitarchordstudio-acceptance",
        priority=DictionarySourcePriority.MANAGED,
    )
    service = LinguisticService(
        "es_ES",
        registry=DictionaryRegistry((provider,)),
        namespace="guitarchordstudio-acceptance",
    )
    info = service.dictionary_info("es_ES")
    if info is None or not info.has_spelling:
        service.close()
        pytest.skip(f"es_ES spelling dictionary did not load from {directory}")
    try:
        yield service
    finally:
        service.close()


def _pipeline_words(text: str) -> list[str]:
    """Mirror the decorator pipeline: tokenize with the host filter."""
    tokenizer = UnicodeTokenizer(token_filters=(is_chord_token,))
    return [token.text for token in tokenizer.iter_tokens(text)]


class TestAcceptanceDocument:
    def test_only_lyric_words_reach_the_dictionary(
        self, spanish_service: LinguisticService
    ) -> None:
        words = _pipeline_words(ROADMAP_DOCUMENT)
        assert words == SPANISH_LYRIC_WORDS

    def test_chords_and_markers_are_ignored(
        self, spanish_service: LinguisticService
    ) -> None:
        words = _pipeline_words(ROADMAP_DOCUMENT)
        assert all(not is_chord_symbol(word) for word in words)
        # ``A#m`` tokenizes as ``A`` + ``m``; the fragment must not survive.
        for excluded in ("m", "A", "A#m", "C#", "G#", "F#", "INTRO", "VERSE", "X3"):
            assert excluded not in words, f"{excluded!r} leaked to spell checking"

    def test_spanish_words_are_accepted_by_the_active_dictionary(
        self, spanish_service: LinguisticService
    ) -> None:
        flagged = [
            word
            for word in _pipeline_words(ROADMAP_DOCUMENT)
            if not spanish_service.check_word(word, locale="es_ES")
        ]
        assert flagged == []

    def test_chord_symbols_are_not_valid_words(
        self, spanish_service: LinguisticService
    ) -> None:
        """Without the filter these would be flagged as misspellings."""
        for chord in ("A#m", "C#m7", "Fmaj7", "Gsus4", "D/F#", "Cadd9"):
            assert spanish_service.check_word(chord, locale="es_ES") is False

    def test_unfiltered_tokenization_would_flag_chord_fragments(
        self, spanish_service: LinguisticService
    ) -> None:
        """Document why the filter inspects the source text, not just the token."""
        raw_words = [
            token.text for token in UnicodeTokenizer().iter_tokens(ROADMAP_DOCUMENT)
        ]
        assert "m" in raw_words
        assert spanish_service.check_word("m", locale="es_ES") is False


class TestSuggestions:
    def test_misspelling_exposes_dictionary_suggestions(
        self, spanish_service: LinguisticService
    ) -> None:
        if not spanish_service.check_word("maravillas", locale="es_ES"):
            pytest.skip("active dictionary does not provide maravillas")
        assert spanish_service.check_word("marabillas", locale="es_ES") is False
        suggestions = spanish_service.suggestions(
            "marabillas", locale="es_ES", limit=8
        )
        assert "maravillas" in suggestions
