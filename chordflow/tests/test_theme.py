"""ChordFlow theme palette and persistence tests."""

from __future__ import annotations

from PyQt6.QtGui import QPalette
from PyQt6.QtWidgets import QApplication

from chordflow.config_manager import DEFAULT_CONFIG
from chordflow.theme import (
    THEME_DARK,
    THEME_LIGHT,
    THEME_SYSTEM,
    apply_theme,
    effective_theme,
)


def test_theme_can_be_applied_and_restored(qtbot):
    app = QApplication.instance() or QApplication([])
    try:
        apply_theme(app, THEME_DARK)
        assert effective_theme(app) == THEME_DARK
        assert app.palette().color(QPalette.ColorRole.Window).lightness() < 128
        assert "QTextEdit" in app.styleSheet()
        assert app.palette().color(QPalette.ColorRole.Link).name() == "#8ab4f8"

        apply_theme(app, THEME_LIGHT)
        assert effective_theme(app) == THEME_LIGHT
        assert app.palette().color(QPalette.ColorRole.Window).lightness() >= 128
        assert app.palette().color(QPalette.ColorRole.Link).name() == "#0969da"
    finally:
        apply_theme(app, THEME_SYSTEM)


def test_theme_is_saved_in_default_configuration():
    assert DEFAULT_CONFIG["theme"] == THEME_SYSTEM


def test_window_exposes_theme_menu_and_saves_selection(qtbot, monkeypatch):
    from chordflow import main_window as main_window_module
    from chordflow.config_manager import DEFAULT_CONFIG

    saved: dict = {}

    class MemoryConfig:
        def __init__(self, *_args, **_kwargs):
            pass

        def load(self):
            return dict(DEFAULT_CONFIG)

        def save(self, config):
            saved.update(config)

    monkeypatch.setattr(main_window_module, "ConfigManager", MemoryConfig)
    window = main_window_module.TextScrollerApp()
    qtbot.addWidget(window)
    try:
        assert window.view_menu.title() == "Ver"
        assert [action.text() for action in window.theme_menu.actions()] == [
            "Sistema",
            "Claro",
            "Oscuro",
        ]
        assert window.theme == THEME_SYSTEM
        window.set_theme(THEME_DARK)
        assert window.theme == THEME_DARK
        assert window._theme_actions[THEME_DARK].isChecked()
        assert saved["theme"] == THEME_DARK
    finally:
        window.set_theme(THEME_SYSTEM)
        window.close()
