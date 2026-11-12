"""ChordFlow About dialog content and links."""

from __future__ import annotations

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication, QLabel

from chordflow.ui.about_dialog import AboutDialog


def test_about_dialog_has_credits_and_clickable_links(qtbot):
    app = QApplication.instance() or QApplication([])
    dialog = AboutDialog(dark_mode=True)
    qtbot.addWidget(dialog)
    try:
        assert dialog.windowTitle() == "About ChordFlow"
        details = dialog.findChild(QLabel, "aboutDetails")
        assert details is not None
        text = details.text()
        assert "© 2026 Washington Indacochea Delgado" in text
        assert "mailto:linuxfrontier@proton.me" in text
        assert "https://github.com/wachin/guitarchordstudio" in text
        assert "GPL3" in text
        assert "#8ab4f8" in text
        assert details.openExternalLinks()
        assert (
            details.textInteractionFlags()
            & Qt.TextInteractionFlag.LinksAccessibleByMouse
        )
    finally:
        dialog.close()
        app.processEvents()


def test_about_dialog_has_icon_description_and_technologies(qtbot):
    app = QApplication.instance() or QApplication([])
    dialog = AboutDialog(dark_mode=False)
    qtbot.addWidget(dialog)
    try:
        icon = dialog.findChild(QLabel, "aboutIcon")
        assert icon is not None
        assert not icon.pixmap().isNull()
        description = dialog.findChild(QLabel, "aboutDescription")
        assert description is not None
        assert "chords" in description.text()
        labels = [label.text() for label in dialog.findChildren(QLabel)]
        assert any("Technologies used" in text for text in labels)
        assert any("#0969da" in text for text in labels)
    finally:
        dialog.close()
        app.processEvents()
