"""About dialog content, links and theme contrast."""

from __future__ import annotations

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QLabel

from chordpages.ui.about_dialog import AboutDialog


def test_about_dialog_shows_credits_and_clickable_links(qtbot):
    dialog = AboutDialog(dark_mode=True)
    qtbot.addWidget(dialog)

    assert dialog.windowTitle() == "About ChordPages"
    details = dialog.findChild(QLabel, "aboutDetails")
    assert details is not None
    text = details.text()
    assert "© 2026 Washington Indacochea Delgado" in text
    assert "linuxfrontier@proton.me" in text
    assert "mailto:linuxfrontier@proton.me" in text
    assert "GPL3" in text
    assert "https://github.com/wachin/guitarchordstudio" in text
    assert "#8ab4f8" in text
    assert details.openExternalLinks()
    assert details.textInteractionFlags() & Qt.TextInteractionFlag.LinksAccessibleByMouse


def test_about_dialog_has_icon_description_and_technologies(qtbot):
    dialog = AboutDialog(dark_mode=False)
    qtbot.addWidget(dialog)

    icon = dialog.findChild(QLabel, "aboutIcon")
    assert icon is not None
    assert not icon.pixmap().isNull()
    description = dialog.findChild(QLabel, "aboutDescription")
    assert description is not None
    assert "ChordPro" in description.text()
    labels = [label.text() for label in dialog.findChildren(QLabel)]
    assert any("Technologies used" in text for text in labels)
    assert any("#0969da" in text for text in labels)
