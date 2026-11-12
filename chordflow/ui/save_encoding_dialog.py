"""Dialog for choosing a save encoding and line-ending style."""

from __future__ import annotations

from PyQt6.QtWidgets import (
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QVBoxLayout,
    QWidget,
)


ENCODING_OPTIONS = (
    ("UTF-8", "utf-8"),
    ("UTF-16 LE", "utf-16-le"),
    ("UTF-16 BE", "utf-16-be"),
    ("UTF-8 con BOM", "utf-8-sig"),
    ("ANSI (Windows-1252)", "cp1252"),
    ("ISO-8859-1", "iso-8859-1"),
)
LINE_ENDING_OPTIONS = (
    ("Windows (CRLF)", "Windows (CRLF)"),
    ("Unix (LF)", "Unix (LF)"),
    ("Mac (CR)", "Mac (CR)"),
)


class SaveEncodingDialog(QDialog):
    """Choose encoding and line endings for Save Encoding As."""

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self.setWindowTitle("Guardar codificación como")
        self.setMinimumWidth(380)

        self.encoding_combo = QComboBox(self)
        self.encoding_combo.setObjectName("saveEncodingComboBox")
        for label, codec in ENCODING_OPTIONS:
            self.encoding_combo.addItem(label, codec)

        self.line_ending_combo = QComboBox(self)
        self.line_ending_combo.setObjectName("saveLineEndingComboBox")
        for label, value in LINE_ENDING_OPTIONS:
            self.line_ending_combo.addItem(label, value)

        form = QFormLayout()
        form.addRow("Codificación:", self.encoding_combo)
        form.addRow("Terminador de línea:", self.line_ending_combo)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok
            | QDialogButtonBox.StandardButton.Cancel,
            parent=self,
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        layout = QVBoxLayout(self)
        layout.addLayout(form)
        layout.addWidget(buttons)

    def selected_codec(self) -> str:
        value = self.encoding_combo.currentData()
        return str(value) if value else "utf-8"

    def selected_line_ending(self) -> str:
        value = self.line_ending_combo.currentData()
        return str(value) if value else "Windows (CRLF)"


__all__ = [
    "ENCODING_OPTIONS",
    "LINE_ENDING_OPTIONS",
    "SaveEncodingDialog",
]
