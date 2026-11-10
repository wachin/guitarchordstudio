"""Tests for the toolkit-only ChordPages spell-checking integration."""

from __future__ import annotations

from types import SimpleNamespace

from PyQt6.QtWidgets import QTextEdit

from chordpages import spellcheck


def _capabilities() -> SimpleNamespace:
    return SimpleNamespace(
        spell_check=True,
        thesaurus=True,
        spelling_source="system",
        thesaurus_source="system",
    )


def test_language_menu_reports_dictionary_sources(qapp, monkeypatch):
    service = SimpleNamespace(
        available_languages=lambda: ("es_EC",),
        language="es_EC",
        capabilities=lambda _locale: _capabilities(),
        set_language=lambda _locale: None,
    )
    monkeypatch.setattr(
        spellcheck,
        "get_linguistic_service",
        lambda: service,
    )

    menu = spellcheck.build_language_menu(None, lambda: None)
    text = menu.actions()[0].text()

    assert "es_EC" in text
    assert "Spelling (system)" in text
    assert "Thesaurus (system)" in text


def test_unavailable_toolkit_shows_a_disabled_message(qapp, monkeypatch):
    monkeypatch.setattr(spellcheck, "_HAS_TOOLKIT", False)
    menu = spellcheck.build_language_menu(None, lambda: None)

    assert len(menu.actions()) == 1
    assert not menu.actions()[0].isEnabled()
    assert "unavailable" in menu.actions()[0].text().lower()
    assert spellcheck.install_spell_checker(QTextEdit()) is None
