"""Tests for the ChordFlow application resources."""

from __future__ import annotations

from PyQt6.QtWidgets import QApplication

from chordflow.app import build_application
from chordflow.resources import APP_ICON_PATH, app_icon


def test_icon_file_exists() -> None:
    assert APP_ICON_PATH.is_file()


def test_app_icon_renders(qapp) -> None:
    icon = app_icon()

    assert not icon.isNull()
    assert not icon.pixmap(64, 64).isNull()


def test_build_application_installs_the_window_icon(qapp) -> None:
    app = build_application([])

    assert app is QApplication.instance()
    assert not app.windowIcon().isNull()
