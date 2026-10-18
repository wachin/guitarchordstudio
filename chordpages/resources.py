"""Shared application resources."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from PyQt6.QtCore import QByteArray, Qt
from PyQt6.QtGui import QIcon, QPainter, QPixmap

try:  # QtSvg ships with PyQt6; keep the fallback for minimal installs.
    from PyQt6.QtSvg import QSvgRenderer
except ImportError:  # pragma: no cover - depends on the Qt installation
    QSvgRenderer = None  # type: ignore[assignment,misc]


ASSETS_PATH = Path(__file__).with_name("assets")
APP_ICON_PATH = ASSETS_PATH / "chordflow.svg"
TOOLBAR_ICON_PATH = ASSETS_PATH / "toolbar"

# Monochrome toolbar icons are tinted when rendered so the same SVGs work on
# the light and dark palettes.
TOOLBAR_ICON_COLORS = {
    False: "#3c4043",
    True: "#e8eaed",
}
TOOLBAR_ICON_SIZES = (24, 48, 72)


def app_icon() -> QIcon:
    """Return the ChordPages application icon."""
    return QIcon(str(APP_ICON_PATH))


@lru_cache(maxsize=None)
def toolbar_icon(name: str, dark: bool = False) -> QIcon:
    """Return the toolbar icon *name*, tinted for the current theme.

    The SVG sources use ``currentColor``; it is replaced with a light or dark
    foreground colour before rendering. A missing file or an installation
    without QtSvg returns a null icon, so the toolbar falls back to text.
    """
    if QSvgRenderer is None:
        return QIcon()

    path = TOOLBAR_ICON_PATH / f"{name}.svg"
    if not path.is_file():
        return QIcon()

    color = TOOLBAR_ICON_COLORS[bool(dark)]
    svg = path.read_text(encoding="utf-8").replace("currentColor", color)
    renderer = QSvgRenderer(QByteArray(svg.encode("utf-8")))
    if not renderer.isValid():
        return QIcon()

    icon = QIcon()
    for size in TOOLBAR_ICON_SIZES:
        pixmap = QPixmap(size, size)
        pixmap.fill(Qt.GlobalColor.transparent)
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        try:
            renderer.render(painter)
        finally:
            painter.end()
        icon.addPixmap(pixmap)
    return icon


__all__ = [
    "APP_ICON_PATH",
    "TOOLBAR_ICON_PATH",
    "app_icon",
    "toolbar_icon",
]
