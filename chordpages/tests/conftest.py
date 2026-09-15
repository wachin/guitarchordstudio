"""Shared pytest configuration."""

from __future__ import annotations

import os

import pytest


os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")


@pytest.fixture(autouse=True)
def deterministic_ui_language(qapp):
    """Force the source-language UI so tests do not depend on the host locale.

    ``build_application`` honors the saved (or system) language, so a machine
    configured for Spanish otherwise translates the menus and breaks tests that
    assert the English labels. Tests that exercise translations install the
    language they need themselves.
    """
    from chordpages.i18n import install_translations

    install_translations(qapp, "en")
    yield
