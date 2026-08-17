"""Search and synonyms dialogs for ChordFlow."""

from __future__ import annotations

import os
import re

import chardet
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDialog,
    QFileDialog,
    QGridLayout,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
)


class FindInFilesDialog(QDialog):
    """Busqueda/Reemplazo en archivos con filtros opcionales."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_widget = parent
        self.setWindowTitle("Buscar en archivos")
        self.resize(700, 520)

        layout = QVBoxLayout(self)

        form = QGridLayout()
        layout.addLayout(form)

        form.addWidget(QLabel("Carpeta:"), 0, 0)
        self.dir_edit = QLineEdit(os.getcwd())
        form.addWidget(self.dir_edit, 0, 1)
        btn_browse = QPushButton("Examinar...")
        form.addWidget(btn_browse, 0, 2)

        form.addWidget(QLabel("Patrones (sep. por ;):"), 1, 0)
        self.patterns = QLineEdit("*.txt;*.md;*.chord;*.pro")
        form.addWidget(self.patterns, 1, 1, 1, 2)

        form.addWidget(QLabel("Buscar:"), 2, 0)
        self.find_edit = QLineEdit()
        form.addWidget(self.find_edit, 2, 1, 1, 2)

        form.addWidget(QLabel("Reemplazar con:"), 3, 0)
        self.replace_edit = QLineEdit()
        form.addWidget(self.replace_edit, 3, 1, 1, 2)

        opts = QHBoxLayout()
        layout.addLayout(opts)
        self.case_cb = QCheckBox("Mayusculas/minusculas")
        self.word_cb = QCheckBox("Palabra completa")
        self.regex_cb = QCheckBox("Usar expresiones regulares")
        self.recursive_cb = QCheckBox("Buscar recursivamente")
        self.recursive_cb.setChecked(True)
        opts.addWidget(self.case_cb)
        opts.addWidget(self.word_cb)
        opts.addWidget(self.regex_cb)
        opts.addWidget(self.recursive_cb)
        opts.addStretch(1)

        self.table = QTableWidget(0, 4)
        self.table.setHorizontalHeaderLabels(["Archivo", "Linea", "Col", "Vista previa"])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.table, 1)

        btns = QHBoxLayout()
        layout.addLayout(btns)
        self.btn_search = QPushButton("Buscar")
        self.btn_replace_sel = QPushButton("Reemplazar en archivos")
        self.btn_close = QPushButton("Cerrar")
        btns.addWidget(self.btn_search)
        btns.addWidget(self.btn_replace_sel)
        btns.addStretch(1)
        btns.addWidget(self.btn_close)

        btn_browse.clicked.connect(self._browse)
        self.btn_search.clicked.connect(self._do_search)
        self.btn_replace_sel.clicked.connect(self._do_replace_all)
        self.btn_close.clicked.connect(self.close)
        self.table.cellDoubleClicked.connect(self._open_match)

    def _browse(self):
        directory = QFileDialog.getExistingDirectory(
            self, "Elegir carpeta", self.dir_edit.text() or os.getcwd()
        )
        if directory:
            self.dir_edit.setText(directory)

    def _iter_files(self, root, patterns, recursive=True):
        import fnmatch

        pats = [pattern.strip() for pattern in patterns.split(";") if pattern.strip()]
        if not pats:
            pats = ["*"]

        if recursive:
            for base, _dirs, files in os.walk(root):
                for name in files:
                    if any(fnmatch.fnmatch(name, pat) for pat in pats):
                        yield os.path.join(base, name)
        else:
            for name in os.listdir(root):
                file_path = os.path.join(root, name)
                if os.path.isfile(file_path) and any(fnmatch.fnmatch(name, pat) for pat in pats):
                    yield file_path

    def _compile(self, text):
        flags = 0
        if not self.case_cb.isChecked():
            flags |= re.IGNORECASE

        pattern = text if self.regex_cb.isChecked() else re.escape(text)
        if self.word_cb.isChecked():
            pattern = r"\b" + pattern + r"\b"
        return re.compile(pattern, flags)

    def _do_search(self):
        self.table.setRowCount(0)
        root = self.dir_edit.text().strip() or os.getcwd()
        query = self.find_edit.text()
        if not query:
            return

        try:
            regex = self._compile(query)
        except re.error as error:
            QMessageBox.warning(self, "Expresion invalida", str(error))
            return

        for file_path in self._iter_files(root, self.patterns.text(), self.recursive_cb.isChecked()):
            try:
                with open(file_path, "rb") as file:
                    raw = file.read()
                encoding = chardet.detect(raw).get("encoding") or "utf-8"
                text = raw.decode(encoding, errors="ignore")
            except Exception:
                continue

            for line_number, line in enumerate(text.splitlines(), start=1):
                for match in regex.finditer(line):
                    row = self.table.rowCount()
                    self.table.insertRow(row)
                    self.table.setItem(row, 0, QTableWidgetItem(file_path))
                    self.table.setItem(row, 1, QTableWidgetItem(str(line_number)))
                    self.table.setItem(row, 2, QTableWidgetItem(str(match.start() + 1)))
                    self.table.setItem(row, 3, QTableWidgetItem(line.strip()))

    def _do_replace_all(self):
        root = self.dir_edit.text().strip() or os.getcwd()
        query = self.find_edit.text()
        replacement = self.replace_edit.text()
        if not query:
            return

        try:
            regex = self._compile(query)
        except re.error as error:
            QMessageBox.warning(self, "Expresion invalida", str(error))
            return

        count_total = 0
        files_changed = 0
        for file_path in self._iter_files(root, self.patterns.text(), self.recursive_cb.isChecked()):
            try:
                with open(file_path, "rb") as file:
                    raw = file.read()
                encoding = chardet.detect(raw).get("encoding") or "utf-8"
                text = raw.decode(encoding, errors="ignore")
                new_text, count = regex.subn(replacement, text)
                if count > 0:
                    with open(file_path, "w", encoding=encoding, newline="") as out:
                        out.write(new_text)
                    count_total += count
                    files_changed += 1
            except Exception:
                continue

        QMessageBox.information(
            self,
            "Reemplazo en archivos",
            f"Reemplazos: {count_total}\nArchivos modificados: {files_changed}",
        )

    def _open_match(self, row, _col):
        file_path = self.table.item(row, 0).text()
        line = int(self.table.item(row, 1).text())
        col = int(self.table.item(row, 2).text())
        self.parent_widget.open_file_at(file_path, line, col)


class SynonymsDialog(QDialog):
    def __init__(self, parent, word, language_index=0):
        super().__init__(parent)
        self.parent_widget = parent
        self.word = word
        self.language_index = language_index
        self.setWindowTitle(
            f"Sinonimos ({self.parent_widget.thesaurus.language_label(language_index)})"
        )
        self.resize(560, 430)

        layout = QVBoxLayout(self)

        form = QGridLayout()
        layout.addLayout(form)

        form.addWidget(QLabel("Palabra actual:"), 0, 1)

        back_button = QPushButton("<-")
        back_button.setEnabled(False)
        form.addWidget(back_button, 1, 0)

        self.word_edit = QLineEdit(word)
        self.word_edit.returnPressed.connect(self.refresh_results)
        form.addWidget(self.word_edit, 1, 1)

        search_button = QPushButton("v")
        search_button.clicked.connect(self.refresh_results)
        form.addWidget(search_button, 1, 2)

        self.language_combo = QComboBox()
        for language in self.parent_widget.thesaurus.languages:
            self.language_combo.addItem(language["label"])
        if self.parent_widget.thesaurus.languages:
            self.language_combo.setCurrentIndex(language_index)
        self.language_combo.currentIndexChanged.connect(self.change_language)
        form.addWidget(self.language_combo, 1, 3)

        layout.addWidget(QLabel("Alternativas:"))

        self.results = QListWidget()
        self.results.itemClicked.connect(self.select_synonym)
        self.results.itemDoubleClicked.connect(self.replace_selected)
        layout.addWidget(self.results, 1)

        layout.addWidget(QLabel("Reemplazar por:"))
        self.replace_edit = QLineEdit()
        layout.addWidget(self.replace_edit)

        buttons = QHBoxLayout()
        layout.addLayout(buttons)
        help_button = QPushButton("Ayuda")
        help_button.clicked.connect(self.show_help)
        buttons.addWidget(help_button)
        buttons.addStretch(1)

        cancel_button = QPushButton("Cancelar")
        cancel_button.clicked.connect(self.reject)
        buttons.addWidget(cancel_button)

        replace_button = QPushButton("Reemplazar")
        replace_button.clicked.connect(self.replace_selected)
        buttons.addWidget(replace_button)

        self.refresh_results()

    def change_language(self, index):
        self.language_index = index
        self.setWindowTitle(f"Sinonimos ({self.parent_widget.thesaurus.language_label(index)})")
        self.refresh_results()

    def refresh_results(self):
        self.results.clear()
        self.word = self.word_edit.text().strip()
        groups = self.parent_widget.thesaurus.lookup(self.word, self.language_index)

        if not groups:
            item = QListWidgetItem("No se encontraron sinonimos")
            item.setFlags(Qt.ItemFlag.NoItemFlags)
            self.results.addItem(item)
            self.replace_edit.clear()
            return

        first_synonym = ""
        for index, group in enumerate(groups, start=1):
            header_text = f"{index}. - {group[0]}"
            header = QListWidgetItem(header_text)
            font = header.font()
            font.setBold(True)
            header.setFont(font)
            header.setFlags(Qt.ItemFlag.NoItemFlags)
            self.results.addItem(header)

            for synonym in group:
                item = QListWidgetItem(synonym)
                item.setData(Qt.ItemDataRole.UserRole, synonym)
                self.results.addItem(item)
                if not first_synonym:
                    first_synonym = synonym

        self.replace_edit.setText(first_synonym)
        if self.results.count() > 1:
            self.results.setCurrentRow(1)

    def select_synonym(self, item):
        synonym = item.data(Qt.ItemDataRole.UserRole)
        if synonym:
            self.replace_edit.setText(synonym)

    def replace_selected(self):
        replacement = self.replace_edit.text()
        if not replacement:
            return
        self.parent_widget.replace_selected_word(replacement)
        self.accept()

    def show_help(self):
        QMessageBox.information(
            self,
            "Sinonimos",
            "Selecciona una alternativa y pulsa Reemplazar para cambiar la palabra seleccionada.",
        )


__all__ = ["FindInFilesDialog", "SynonymsDialog"]
