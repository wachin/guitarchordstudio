"""Encoding detection for legacy and modern text files."""

from __future__ import annotations

from chordpages.document.text_file import decode_text


def test_utf8_is_detected_without_chardet_guesswork():
    text, encoding = decode_text("canción".encode("utf-8"))
    assert text == "canción"
    assert encoding == "utf-8"


def test_windows_1252_legacy_file_decodes():
    text, encoding = decode_text("canción".encode("cp1252"))
    assert text == "canción"
    assert encoding


def test_utf16_bom_is_detected():
    text, encoding = decode_text("canción".encode("utf-16"))
    assert text == "canción"
    assert encoding == "utf-16"
