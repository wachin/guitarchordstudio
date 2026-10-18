"""Toolbar icons, tooltips and ordering for ChordPages."""

from __future__ import annotations

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QToolBar

from chordpages.main_window import TOOLBAR_ICON_ACTIONS, MainWindow
from chordpages.settings import THEME_DARK, THEME_LIGHT, SettingsManager


def _window(tmp_path) -> MainWindow:
    settings = SettingsManager.from_file(tmp_path / "chordpages-settings.ini")
    return MainWindow(settings=settings)


def _stroke_color(icon: QIcon) -> str | None:
    """Return the first opaque pixel colour of a rendered icon."""
    image = icon.pixmap(24, 24).toImage()
    for y in range(image.height()):
        for x in range(image.width()):
            color = image.pixelColor(x, y)
            if color.alpha() > 200:
                return color.name()
    return None


def _toolbar_labels(toolbar: QToolBar) -> list[str]:
    return [
        action.text()
        for action in toolbar.actions()
        if not action.isSeparator() and action.text()
    ]


def test_toolbar_is_icon_only(qtbot, tmp_path) -> None:
    window = _window(tmp_path)
    qtbot.addWidget(window)

    assert window.toolbar.toolButtonStyle() == Qt.ToolButtonStyle.ToolButtonIconOnly
    assert window.toolbar.iconSize().width() == 24


def test_each_toolbar_action_has_an_icon_and_tooltip(qtbot, tmp_path) -> None:
    window = _window(tmp_path)
    qtbot.addWidget(window)

    for attribute, _icon_name in TOOLBAR_ICON_ACTIONS:
        action = getattr(window, attribute)
        assert not action.icon().isNull(), f"{attribute} has no icon"
        assert action.toolTip() == action.text()
        assert action.toolTip()


def test_toolbar_order_includes_save_as_after_save(qtbot, tmp_path) -> None:
    window = _window(tmp_path)
    qtbot.addWidget(window)

    expected = [
        getattr(window, attribute).text() for attribute, _icon in TOOLBAR_ICON_ACTIONS
    ]
    labels = _toolbar_labels(window.toolbar)
    assert labels[: len(expected)] == expected

    save_index = expected.index(window.save_action.text())
    assert expected[save_index + 1] == window.save_as_action.text()


def test_icons_follow_the_theme(qtbot, tmp_path) -> None:
    window = _window(tmp_path)
    qtbot.addWidget(window)
    try:
        window.set_theme(THEME_LIGHT)
        assert _stroke_color(window.save_action.icon()) == "#3c4043"

        window.set_theme(THEME_DARK)
        assert _stroke_color(window.save_action.icon()) == "#e8eaed"
    finally:
        window.set_theme(THEME_LIGHT)
