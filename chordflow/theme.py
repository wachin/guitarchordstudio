"""Application-wide light and dark theme support for ChordFlow."""

from __future__ import annotations

from dataclasses import dataclass

from PyQt6.QtGui import QColor, QPalette
from PyQt6.QtWidgets import QApplication


THEME_SYSTEM = "system"
THEME_LIGHT = "light"
THEME_DARK = "dark"
DEFAULT_THEME = THEME_SYSTEM
SUPPORTED_THEMES = (THEME_SYSTEM, THEME_LIGHT, THEME_DARK)

BASE_PALETTE_PROPERTY = "_chordflow_base_palette"
CURRENT_THEME_PROPERTY = "_chordflow_theme"
EFFECTIVE_THEME_PROPERTY = "_chordflow_effective_theme"


@dataclass(frozen=True, slots=True)
class AppliedTheme:
    """Result of applying a theme preference."""

    requested: str
    effective: str


def normalize_theme(theme: str | None) -> str:
    """Return a supported theme code."""
    normalized = (theme or DEFAULT_THEME).strip().lower()
    return normalized if normalized in SUPPORTED_THEMES else DEFAULT_THEME


def apply_theme(app: QApplication, theme: str = DEFAULT_THEME) -> AppliedTheme:
    """Apply a system, light or dark palette and stylesheet."""
    requested = normalize_theme(theme)
    base_palette = _base_palette(app)

    if requested == THEME_SYSTEM:
        app.setPalette(base_palette)
        app.setStyleSheet("")
        effective = _palette_theme(base_palette)
    else:
        app.setPalette(_theme_palette(requested))
        app.setStyleSheet(_theme_stylesheet(requested))
        effective = requested

    app.setProperty(CURRENT_THEME_PROPERTY, requested)
    app.setProperty(EFFECTIVE_THEME_PROPERTY, effective)
    return AppliedTheme(requested=requested, effective=effective)


def effective_theme(app: QApplication | None = None) -> str:
    """Return the currently effective light/dark theme."""
    application = app or QApplication.instance()
    if not isinstance(application, QApplication):
        return THEME_LIGHT
    value = application.property(EFFECTIVE_THEME_PROPERTY)
    if value in (THEME_LIGHT, THEME_DARK):
        return str(value)
    return _palette_theme(application.palette())


def _base_palette(app: QApplication) -> QPalette:
    stored_palette = app.property(BASE_PALETTE_PROPERTY)
    if isinstance(stored_palette, QPalette):
        return QPalette(stored_palette)
    palette = QPalette(app.palette())
    app.setProperty(BASE_PALETTE_PROPERTY, palette)
    return QPalette(palette)


def _palette_theme(palette: QPalette) -> str:
    window_color = palette.color(QPalette.ColorRole.Window)
    return THEME_DARK if window_color.lightness() < 128 else THEME_LIGHT


def _theme_palette(theme: str) -> QPalette:
    if theme == THEME_DARK:
        return _build_palette(
            window="#202124",
            window_text="#f1f3f4",
            base="#181a1b",
            alternate_base="#242629",
            text="#f1f3f4",
            button="#2b2d31",
            button_text="#f1f3f4",
            highlight="#3d8bfd",
            highlighted_text="#ffffff",
            link="#8ab4f8",
            disabled_text="#9aa0a6",
        )
    return _build_palette(
        window="#f5f6f8",
        window_text="#1f2328",
        base="#ffffff",
        alternate_base="#eef1f4",
        text="#1f2328",
        button="#ffffff",
        button_text="#1f2328",
        highlight="#1769d1",
        highlighted_text="#ffffff",
        link="#0969da",
        disabled_text="#6e7781",
    )


def _build_palette(
    *,
    window: str,
    window_text: str,
    base: str,
    alternate_base: str,
    text: str,
    button: str,
    button_text: str,
    highlight: str,
    highlighted_text: str,
    link: str,
    disabled_text: str,
) -> QPalette:
    palette = QPalette()
    palette.setColor(QPalette.ColorRole.Window, QColor(window))
    palette.setColor(QPalette.ColorRole.WindowText, QColor(window_text))
    palette.setColor(QPalette.ColorRole.Base, QColor(base))
    palette.setColor(QPalette.ColorRole.AlternateBase, QColor(alternate_base))
    palette.setColor(QPalette.ColorRole.Text, QColor(text))
    palette.setColor(QPalette.ColorRole.Button, QColor(button))
    palette.setColor(QPalette.ColorRole.ButtonText, QColor(button_text))
    palette.setColor(QPalette.ColorRole.BrightText, QColor("#ffffff"))
    palette.setColor(QPalette.ColorRole.Highlight, QColor(highlight))
    palette.setColor(QPalette.ColorRole.HighlightedText, QColor(highlighted_text))
    palette.setColor(QPalette.ColorRole.Link, QColor(link))
    palette.setColor(QPalette.ColorRole.PlaceholderText, QColor(disabled_text))

    for role in (
        QPalette.ColorRole.WindowText,
        QPalette.ColorRole.Text,
        QPalette.ColorRole.ButtonText,
    ):
        palette.setColor(QPalette.ColorGroup.Disabled, role, QColor(disabled_text))

    return palette


def _theme_stylesheet(theme: str) -> str:
    if theme == THEME_DARK:
        return _stylesheet(
            window="#202124",
            text="#f1f3f4",
            panel="#2b2d31",
            border="#3c4043",
            selected="#3d8bfd",
            selected_text="#ffffff",
        )
    return _stylesheet(
        window="#f5f6f8",
        text="#1f2328",
        panel="#ffffff",
        border="#d0d7de",
        selected="#1769d1",
        selected_text="#ffffff",
    )


def _stylesheet(
    *,
    window: str,
    text: str,
    panel: str,
    border: str,
    selected: str,
    selected_text: str,
) -> str:
    return f"""
        QToolTip {{
            background-color: {panel};
            border: 1px solid {border};
            color: {text};
        }}

        QMenuBar, QMenu, QStatusBar, QDialog {{
            background-color: {window};
            color: {text};
        }}

        QMenuBar::item:selected, QMenu::item:selected {{
            background-color: {selected};
            color: {selected_text};
        }}

        QTabWidget::pane {{
            border: 1px solid {border};
        }}

        QTabBar::tab {{
            background-color: {panel};
            color: {text};
            padding: 3px 9px;
            border: 1px solid {border};
        }}

        QTabBar::tab:selected {{
            background-color: {selected};
            color: {selected_text};
        }}

        QTextEdit, QPlainTextEdit, QLineEdit, QComboBox {{
            background-color: {panel};
            color: {text};
            border: 1px solid {border};
            selection-background-color: {selected};
            selection-color: {selected_text};
        }}

        QPushButton {{
            background-color: {panel};
            color: {text};
            border: 1px solid {border};
            padding: 4px 10px;
        }}

        QPushButton:hover {{
            border-color: {selected};
        }}

        QSlider::groove:horizontal {{
            background: {border};
            height: 4px;
        }}

        QSlider::handle:horizontal {{
            background: {selected};
            width: 14px;
            margin: -5px 0;
            border-radius: 7px;
        }}
    """


__all__ = [
    "AppliedTheme",
    "DEFAULT_THEME",
    "EFFECTIVE_THEME_PROPERTY",
    "SUPPORTED_THEMES",
    "THEME_DARK",
    "THEME_LIGHT",
    "THEME_SYSTEM",
    "apply_theme",
    "effective_theme",
    "normalize_theme",
]
