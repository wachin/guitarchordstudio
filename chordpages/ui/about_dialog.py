"""About dialog for ChordPages."""

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

from chordpages import __version__
from chordpages.resources import app_icon
from chordpages.settings import WINDOW_TITLE_NAME


EMAIL = "linuxfrontier@proton.me"
WEBSITE = "https://github.com/wachin/guitarchordstudio"
COPYRIGHT = "© 2026 Washington Indacochea Delgado"
LICENSE = "GPL3"
LINK_COLOR_DARK = "#8ab4f8"
LINK_COLOR_LIGHT = "#0969da"


class AboutDialog(QDialog):
    """Show application identity, credits, links and technologies."""

    def __init__(
        self,
        parent: QWidget | None = None,
        *,
        dark_mode: bool = False,
    ):
        super().__init__(parent)
        self.setWindowTitle(
            self.tr("About {application_name}").format(
                application_name=WINDOW_TITLE_NAME
            )
        )
        self.resize(660, 470)
        self.setMinimumSize(560, 400)

        icon_label = QLabel(self)
        icon_label.setObjectName("aboutIcon")
        icon_label.setFixedSize(128, 128)
        icon_label.setAlignment(
            Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter
        )
        icon_label.setPixmap(app_icon().pixmap(112, 112))

        text_panel = QWidget(self)
        text_layout = QVBoxLayout(text_panel)
        text_layout.setContentsMargins(0, 0, 0, 0)
        text_layout.setSpacing(8)

        title = QLabel(WINDOW_TITLE_NAME, text_panel)
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
                "A lightweight WYSIWYG ChordPro-oriented word processor for "
                "page layout, worship songs, and Git-friendly music documents."
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
            self.tr(
                "Copyright: {copyright}<br>"
                "Email: {email}<br>"
                "License: {license}<br>"
                "Website: {website}"
            ).format(
                copyright=COPYRIGHT,
                email=email_link,
                license=LICENSE,
                website=website_link,
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
        body.setSpacing(20)
        body.addWidget(icon_label, 0, Qt.AlignmentFlag.AlignTop)
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
