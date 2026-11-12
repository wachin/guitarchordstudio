"""About dialog for ChordFlow."""

from __future__ import annotations

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QHBoxLayout,
    QLabel,
    QVBoxLayout,
    QWidget,
)

from chordflow import __version__
from chordflow.resources import app_icon


EMAIL = "linuxfrontier@proton.me"
WEBSITE = "https://github.com/wachin/guitarchordstudio"
COPYRIGHT = "© 2026 Washington Indacochea Delgado"
LICENSE = "GPL3"
LINK_COLOR_DARK = "#8ab4f8"
LINK_COLOR_LIGHT = "#0969da"


class AboutDialog(QDialog):
    """Show ChordFlow identity, credits, links and technologies."""

    def __init__(self, parent: QWidget | None = None, *, dark_mode: bool = False):
        super().__init__(parent)
        self.setWindowTitle(
            self.tr("About {application_name}").format(application_name="ChordFlow")
        )
        self.resize(720, 330)
        self.setMinimumSize(600, 310)

        icon_label = QLabel(self)
        icon_label.setObjectName("aboutIcon")
        icon_label.setFixedSize(224, 224)
        icon_label.setAlignment(
            Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter
        )
        icon_label.setPixmap(app_icon().pixmap(224, 224))

        text_panel = QWidget(self)
        text_layout = QVBoxLayout(text_panel)
        text_layout.setContentsMargins(0, 0, 0, 0)
        text_layout.setSpacing(8)

        title = QLabel("ChordFlow", text_panel)
        title_font = QFont(title.font())
        title_font.setPointSize(title_font.pointSize() + 9)
        title_font.setBold(True)
        title.setFont(title_font)

        version = QLabel(
            self.tr("Version {version}").format(version=__version__),
            text_panel,
        )

        description = QLabel(
            self.tr(
                "ChordFlow is a lightweight reader and editor for lyrics with "
                "chords. It supports transposition, automatic scrolling during "
                "rehearsals, spell checking, and synonyms."
            ),
            text_panel,
        )
        description.setObjectName("aboutDescription")
        description.setWordWrap(True)
        description.setTextInteractionFlags(
            Qt.TextInteractionFlag.TextSelectableByMouse
        )

        link_color = LINK_COLOR_DARK if dark_mode else LINK_COLOR_LIGHT
        email_link = f'<a href="mailto:{EMAIL}" style="color:{link_color};">{EMAIL}</a>'
        website_link = f'<a href="{WEBSITE}" style="color:{link_color};">{WEBSITE}</a>'
        details = QLabel(
            "<br>".join(
                (
                    self.tr("Copyright: {copyright}").format(copyright=COPYRIGHT),
                    self.tr("Email: {email}").format(email=email_link),
                    self.tr("License: {license}").format(license=LICENSE),
                    self.tr("Website: {website}").format(website=website_link),
                )
            ),
            text_panel,
        )
        details.setObjectName("aboutDetails")
        details.setTextFormat(Qt.TextFormat.RichText)
        details.setTextInteractionFlags(Qt.TextInteractionFlag.TextBrowserInteraction)
        details.setOpenExternalLinks(True)
        details.setWordWrap(True)

        technologies = QLabel(
            self.tr(
                "Technologies used: Python 3, PyQt6, Qt 6, and "
                "pyqt6-linguistic-tools (Spylls and PyThes)."
            ),
            text_panel,
        )
        technologies.setWordWrap(True)
        technologies.setTextInteractionFlags(
            Qt.TextInteractionFlag.TextSelectableByMouse
        )

        text_layout.addWidget(title)
        text_layout.addWidget(version)
        text_layout.addWidget(description)
        text_layout.addSpacing(6)
        text_layout.addWidget(details)
        text_layout.addSpacing(6)
        text_layout.addWidget(technologies)
        text_layout.addStretch(1)

        body = QHBoxLayout()
        body.setSpacing(18)
        body.setContentsMargins(4, 4, 4, 0)
        body.addWidget(icon_label, 0, Qt.AlignmentFlag.AlignVCenter)
        body.addWidget(text_panel, 1)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Close,
            parent=self,
        )
        buttons.rejected.connect(self.reject)

        layout = QVBoxLayout(self)
        layout.addLayout(body, 1)
        layout.addWidget(buttons)


__all__ = ["AboutDialog"]
