"""Application preferences dialog with a LibreOffice-style section list."""

from __future__ import annotations

from PyQt6.QtWidgets import (
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QHBoxLayout,
    QListWidget,
    QListWidgetItem,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from chordpages.settings import (
    DEFAULT_ICON_SIZE,
    DEFAULT_LANGUAGE,
    ICON_SIZE_EXTRA_LARGE,
    ICON_SIZE_LARGE,
    ICON_SIZE_SMALL,
    ICON_SIZE_VERY_SMALL,
    normalized_icon_size,
)


LANGUAGE_CODES = (DEFAULT_LANGUAGE, "en", "es")
ICON_SIZE_CODES = (
    ICON_SIZE_VERY_SMALL,
    ICON_SIZE_SMALL,
    ICON_SIZE_LARGE,
    ICON_SIZE_EXTRA_LARGE,
)


class PreferencesDialog(QDialog):
    """Edit application-level preferences."""

    def __init__(
        self,
        language: str = DEFAULT_LANGUAGE,
        icon_size: str = DEFAULT_ICON_SIZE,
        parent: QWidget | None = None,
    ):
        super().__init__(parent)
        self.setWindowTitle(self.tr("Preferences"))
        self.resize(680, 440)
        self.setMinimumSize(560, 360)

        self._section_list = QListWidget()
        self._section_list.setObjectName("preferencesSections")
        self._section_list.setFixedWidth(170)
        self._stack = QStackedWidget()

        self._add_section(self.tr("General"), self._build_general_page(language))
        self._add_section(self.tr("View"), self._build_view_page(icon_size))
        self._section_list.currentRowChanged.connect(self._stack.setCurrentIndex)

        body = QHBoxLayout()
        body.addWidget(self._section_list)
        body.addWidget(self._stack, 1)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        layout = QVBoxLayout(self)
        layout.addLayout(body, 1)
        layout.addWidget(buttons)
        self._section_list.setCurrentRow(0)

    def _add_section(self, title: str, page: QWidget) -> None:
        self._section_list.addItem(QListWidgetItem(title))
        self._stack.addWidget(page)

    def _build_general_page(self, language: str) -> QWidget:
        page = QWidget()
        form_layout = QFormLayout(page)

        self._language_combo = QComboBox()
        self._language_combo.setObjectName("languageComboBox")
        language_labels = {
            DEFAULT_LANGUAGE: self.tr("System default"),
            "en": self.tr("English"),
            "es": self.tr("Spanish"),
        }
        for language_code in LANGUAGE_CODES:
            self._language_combo.addItem(language_labels[language_code], language_code)

        selected_index = self._language_combo.findData(language or DEFAULT_LANGUAGE)
        if selected_index < 0:
            selected_index = self._language_combo.findData(DEFAULT_LANGUAGE)
        self._language_combo.setCurrentIndex(max(0, selected_index))
        form_layout.addRow(self.tr("Language"), self._language_combo)
        return page

    def _build_view_page(self, icon_size: str) -> QWidget:
        page = QWidget()
        form_layout = QFormLayout(page)

        self._icon_size_combo = QComboBox()
        self._icon_size_combo.setObjectName("iconSizeComboBox")
        icon_size_labels = {
            ICON_SIZE_VERY_SMALL: self.tr("Very small"),
            ICON_SIZE_SMALL: self.tr("Small"),
            ICON_SIZE_LARGE: self.tr("Large"),
            ICON_SIZE_EXTRA_LARGE: self.tr("Extra large"),
        }
        for size_code in ICON_SIZE_CODES:
            self._icon_size_combo.addItem(icon_size_labels[size_code], size_code)

        selected_index = self._icon_size_combo.findData(normalized_icon_size(icon_size))
        self._icon_size_combo.setCurrentIndex(max(0, selected_index))
        form_layout.addRow(self.tr("Icon size"), self._icon_size_combo)
        return page

    def selected_language(self) -> str:
        """Return the selected language code."""
        value = self._language_combo.currentData()
        return str(value) if value else DEFAULT_LANGUAGE

    def selected_icon_size(self) -> str:
        """Return the selected toolbar icon-size code."""
        value = self._icon_size_combo.currentData()
        return str(value) if value else DEFAULT_ICON_SIZE


__all__ = ["PreferencesDialog"]
