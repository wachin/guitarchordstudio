"""Main window implementation for ChordFlow."""

from __future__ import annotations

import math
import os
import re
from PyQt6.QtCore import QLibraryInfo, QRegularExpression, Qt, QTimer, QTranslator
from PyQt6.QtGui import (
    QAction,
    QActionGroup,
    QColor,
    QDragEnterEvent,
    QDropEvent,
    QFont,
    QKeySequence,
    QShortcut,
    QTextCursor,
    QTextDocument,
)
from PyQt6.QtWidgets import (
    QApplication,
    QCheckBox,
    QDialog,
    QFileDialog,
    QFontDialog,
    QGridLayout,
    QHBoxLayout,
    QInputDialog,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMenu,
    QMessageBox,
    QPushButton,
    QSlider,
    QTabWidget,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from .chord_transposer import transpose_text
from .config_manager import ConfigManager
from .file_operations import (
    add_to_recent_files,
    detect_encoding,
    read_file,
    write_file,
)
from .search_dialog import FindInFilesDialog, SynonymsDialog
from .thesaurus import MythesThesaurus


class CustomTextEdit(QTextEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(False)


class TextScrollerApp(QMainWindow):
    def show_about_dialog(self):
        about_text = (
            "<h2><b>Chord autoscroll</b></h2>"
            "<p>Este programa sirve para la transposicion de acordes. "
            "Podras cargar tus canciones que contengan letras y acordes para "
            "transportarlas facilmente y desplazarte automaticamente por el texto "
            "durante tus ensayos.</p>"
            "<p>Copyright 2025 (c) Washington Indacochea Delgado.<br>"
            "wachin.id@gmail.com<br>"
            "Licencia GPL 3</p>"
            "<p>Para mas informacion revisa:</p>"
            '<a href="https://github.com/wachin/py_chord_autoscroll">'
            "https://github.com/wachin/py_chord_autoscroll</a>"
        )

        dialog = QMessageBox(self)
        dialog.setWindowTitle("Acerca de Chord Autoscroll")
        dialog.setTextFormat(Qt.TextFormat.RichText)
        dialog.setText(about_text)
        dialog.setStandardButtons(QMessageBox.StandardButton.Ok)
        dialog.setTextInteractionFlags(Qt.TextInteractionFlag.TextBrowserInteraction)
        dialog.exec()

    def __init__(self):
        super().__init__()
        self.translator = QTranslator()

        translations_path = QLibraryInfo.path(QLibraryInfo.LibraryPath.TranslationsPath)
        if self.translator.load("qtbase_es", translations_path):
            QApplication.installTranslator(self.translator)

        self.setWindowTitle("Lector y Editor de Letras con Acordes")
        self.setGeometry(100, 100, 800, 500)

        self.current_file = None
        self.is_scrolling = False
        self.max_speed = 400
        self.scroll_speed = self.calculate_speed(15)
        self.config_manager = ConfigManager("config12.json")
        self.opened_files = {}
        self.file_encodings = {}
        self.config = self.config_manager.load()
        self.thesaurus = MythesThesaurus()
        self.opened_files = {}

        self.init_ui()

        self.replace_btn.clicked.connect(self.replace_one)
        self.replace_all_btn.clicked.connect(self.replace_all)
        self.update_recent_files_menu()

    def select_font(self):
        font, ok = QFontDialog.getFont(
            QFont(self.config.get("font_family", "Noto Mono"), self.config.get("font_size", 10)),
            self,
            "Selecciona una fuente",
        )

        if ok:
            current_widget = self.get_current_text_widget()
            if current_widget:
                current_widget.setFont(font)

            self.config["font_family"] = font.family()
            self.config["font_size"] = font.pointSize()
            self.save_config()

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        self.tab_widget = QTabWidget()
        self.tab_widget.setTabsClosable(True)
        self.tab_widget.tabCloseRequested.connect(self.close_tab)
        layout.addWidget(self.tab_widget)
        self.add_new_tab()

        control_layout = QHBoxLayout()
        layout.addLayout(control_layout)

        self.start_button = QPushButton("Iniciar")
        self.start_button.clicked.connect(self.start_scrolling)
        control_layout.addWidget(self.start_button)

        self.pause_button = QPushButton("Pausar")
        self.pause_button.clicked.connect(self.pause_scrolling)
        control_layout.addWidget(self.pause_button)

        control_layout.addWidget(QLabel("Velocidad:"))

        self.speed_slider = QSlider(Qt.Orientation.Horizontal)
        self.speed_slider.setRange(1, 30)
        last_position = self.config.get("last_slider_position", 15)
        self.speed_slider.setValue(last_position)
        self.update_speed()
        self.speed_slider.valueChanged.connect(self.update_speed)
        control_layout.addWidget(self.speed_slider)

        self.transpose_button = QPushButton("Transponer")
        self.transpose_button.clicked.connect(self.show_transpose_menu)
        control_layout.addWidget(self.transpose_button)

        self.encoding_label = QLabel("Codificacion: UTF-8")
        self.encoding_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        layout.addWidget(self.encoding_label)

        self.create_menu_bar()

        shortcut = QShortcut(QKeySequence("Ctrl+Space"), self)
        shortcut.activated.connect(self.toggle_scroll)

        self.tab_widget.currentChanged.connect(self.update_encoding_label)
        self.setAcceptDrops(True)

        self.search_panel = QWidget()
        self.search_panel.setVisible(False)

        search_layout = QVBoxLayout(self.search_panel)

        find_layout = QHBoxLayout()

        self.find_input = QLineEdit()
        self.find_input.setPlaceholderText("Buscar")

        self.find_prev_btn = QPushButton("Anterior")
        self.find_next_btn = QPushButton("Siguiente")

        self.find_next_btn.clicked.connect(self.find_next)
        self.find_prev_btn.clicked.connect(self.find_previous)
        self.find_input.returnPressed.connect(self.find_next)

        find_layout.addWidget(QLabel("Buscar:"))
        find_layout.addWidget(self.find_input)
        find_layout.addWidget(self.find_prev_btn)
        find_layout.addWidget(self.find_next_btn)

        search_layout.addLayout(find_layout)

        options_layout = QHBoxLayout()

        self.match_case_cb = QCheckBox("Coincidir mayusculas")
        self.regex_cb = QCheckBox("Expresiones regulares")

        options_layout.addWidget(self.match_case_cb)
        options_layout.addWidget(self.regex_cb)

        search_layout.addLayout(options_layout)

        replace_layout = QHBoxLayout()

        self.replace_input = QLineEdit()
        self.replace_input.setPlaceholderText("Reemplazar")

        self.replace_btn = QPushButton("Reemplazar")
        self.replace_all_btn = QPushButton("Reemplazar todo")

        self.replace_label = QLabel("Reemplazar:")
        replace_layout.addWidget(self.replace_label)
        replace_layout.addWidget(self.replace_input)
        replace_layout.addWidget(self.replace_btn)
        replace_layout.addWidget(self.replace_all_btn)

        search_layout.addLayout(replace_layout)

        self.replace_label.setVisible(False)
        self.replace_input.setVisible(False)
        self.replace_btn.setVisible(False)
        self.replace_all_btn.setVisible(False)

        layout.addWidget(self.search_panel)

    def find_previous(self):
        editor = self.get_current_text_widget()
        if not editor:
            return

        text = self.find_input.text()
        if not text:
            return

        flags = QTextDocument.FindFlag.FindBackward
        if self.match_case_cb.isChecked():
            flags |= QTextDocument.FindFlag.FindCaseSensitively

        found = editor.find(text, flags)
        if not found:
            cursor = editor.textCursor()
            cursor.movePosition(QTextCursor.MoveOperation.End)
            editor.setTextCursor(cursor)
            editor.find(text, flags)

    def replace_one(self):
        editor = self.get_current_text_widget()
        if not editor:
            return

        cursor = editor.textCursor()
        if cursor.hasSelection():
            cursor.insertText(self.replace_input.text())
            self.find_next()

    def replace_all(self):
        editor = self.get_current_text_widget()
        if not editor:
            return

        text = editor.toPlainText()
        find = self.find_input.text()
        replace = self.replace_input.text()

        if self.regex_cb.isChecked():
            flags = 0 if self.match_case_cb.isChecked() else re.IGNORECASE
            text = re.sub(find, replace, text, flags=flags)
        else:
            if self.match_case_cb.isChecked():
                text = text.replace(find, replace)
            else:
                text = re.sub(re.escape(find), replace, text, flags=re.IGNORECASE)

        editor.setPlainText(text)

    def highlight_all_matches(self):
        editor = self.get_current_text_widget()
        if not editor:
            return

        text = self.find_input.text()
        if not text:
            editor.setExtraSelections([])
            return

        cursor = editor.textCursor()
        cursor.beginEditBlock()

        selections = []
        doc = editor.document()
        flags = QTextDocument.FindFlag(0)

        if self.match_case_cb.isChecked():
            flags |= QTextDocument.FindFlag.FindCaseSensitively

        cursor = QTextCursor(doc)
        while True:
            if self.regex_cb.isChecked():
                pattern = QRegularExpression(text)
                cursor = doc.find(pattern, cursor)
            else:
                cursor = doc.find(text, cursor, flags)

            if cursor.isNull():
                break

            selection = QTextEdit.ExtraSelection()
            selection.cursor = cursor
            selection.format.setBackground(QColor("#fff59d"))
            selections.append(selection)

        editor.setExtraSelections(selections)
        cursor.endEditBlock()

    def update_encoding_label(self, index):
        file_path = self.opened_files.get(index, None)
        if file_path and file_path in self.file_encodings:
            encoding = self.file_encodings[file_path]["encoding"]
            line_ending = self.file_encodings[file_path]["line_ending"]
            self.encoding_label.setText(
                f"Codificacion: {encoding} | Terminador de linea: {line_ending}"
            )
            self.setWindowTitle(f"{os.path.basename(file_path)} - Lector y Editor de Texto con acordes")
        else:
            self.encoding_label.setText("Codificacion: N/A | Terminador de linea: N/A")
            self.setWindowTitle("Lector y Editor de Texto con acordes")

    def show_find_panel(self):
        self.search_panel.setVisible(True)
        self.replace_label.setVisible(False)
        self.replace_input.setVisible(False)
        self.replace_btn.setVisible(False)
        self.replace_all_btn.setVisible(False)
        self.find_input.setFocus()

    def show_replace_panel(self):
        self.search_panel.setVisible(True)
        self.replace_label.setVisible(True)
        self.replace_input.setVisible(True)
        self.replace_btn.setVisible(True)
        self.replace_all_btn.setVisible(True)
        self.find_input.setFocus()

    def toggle_scroll(self):
        if self.is_scrolling:
            self.pause_scrolling()
        else:
            self.start_scrolling()

    def find_next(self):
        self.highlight_all_matches()

        editor = self.get_current_text_widget()
        if not editor:
            return

        flags = QTextDocument.FindFlag(0)
        if self.match_case_cb.isChecked():
            flags |= QTextDocument.FindFlag.FindCaseSensitively

        text = self.find_input.text()
        if not text:
            return

        if self.regex_cb.isChecked():
            pattern = QRegularExpression(text)
            editor.find(pattern)
        else:
            editor.find(text, flags)

    def add_new_tab(self, file_name=None, content="", file_path=None):
        text_widget = CustomTextEdit()
        text_widget.setUndoRedoEnabled(True)
        text_widget.document().setModified(False)
        text_widget.textChanged.connect(self.on_text_changed)

        default_font = self.config.get("font_family", "Noto Mono")
        default_font_size = self.config.get("font_size", 10)
        text_widget.setFont(QFont(default_font, default_font_size))

        if content:
            text_widget.setPlainText(content)
            text_widget.document().setModified(False)

        tab_name = file_name if file_name else "Nuevo archivo"
        index = self.tab_widget.addTab(text_widget, tab_name)

        if file_path:
            self.opened_files[index] = file_path
        else:
            self.opened_files[index] = None

        self.tab_widget.setCurrentWidget(text_widget)
        self.update_window_title()

    def on_text_changed(self):
        current_widget = self.get_current_text_widget()
        if current_widget:
            current_index = self.tab_widget.currentIndex()
            file_path = self.opened_files.get(current_index, None)

            if file_path:
                encoding = self.file_encodings.get(file_path, {}).get("encoding", "utf-8")

                try:
                    with open(file_path, "r", encoding=encoding) as file:
                        saved_content = file.read()
                except Exception:
                    saved_content = ""

                current_content = current_widget.toPlainText()
                is_modified = current_content != saved_content
                current_widget.document().setModified(is_modified)
                self.update_window_title()

    def update_window_title(self):
        current_index = self.tab_widget.currentIndex()
        file_path = self.opened_files.get(current_index, "Nuevo archivo")
        file_name = os.path.basename(file_path) if file_path else "Nuevo archivo"
        modified = "*" if self.get_current_text_widget().document().isModified() else ""
        self.setWindowTitle(f"{file_name} {modified} - Lector y Editor de Letras con Acordes")

    def close_tab(self, index):
        current_widget = self.tab_widget.widget(index)
        if isinstance(current_widget, CustomTextEdit) and current_widget.document().isModified():
            reply = QMessageBox.question(
                self,
                "Cerrar documento",
                f'El documento "{self.tab_widget.tabText(index)}" ha sido modificado. '
                "Desea guardar los cambios, o descartarlos?",
                QMessageBox.StandardButton.Save
                | QMessageBox.StandardButton.Discard
                | QMessageBox.StandardButton.Cancel,
            )
            if reply == QMessageBox.StandardButton.Save:
                self.tab_widget.setCurrentIndex(index)
                self.save_file()
            elif reply == QMessageBox.StandardButton.Cancel:
                return

        self.tab_widget.removeTab(index)

    def closeEvent(self, event):
        for index in range(self.tab_widget.count()):
            self.tab_widget.setCurrentIndex(index)
            current_widget = self.tab_widget.widget(index)
            if isinstance(current_widget, CustomTextEdit) and current_widget.document().isModified():
                reply = QMessageBox.question(
                    self,
                    "Cerrar aplicacion",
                    f'El documento "{self.tab_widget.tabText(index)}" ha sido modificado. '
                    "Desea guardar los cambios, o descartarlos?",
                    QMessageBox.StandardButton.Save
                    | QMessageBox.StandardButton.Discard
                    | QMessageBox.StandardButton.Cancel,
                )
                if reply == QMessageBox.StandardButton.Save:
                    self.save_file()
                elif reply == QMessageBox.StandardButton.Cancel:
                    event.ignore()
                    return

        event.accept()

    def get_current_text_widget(self):
        widget = self.tab_widget.currentWidget()
        if isinstance(widget, CustomTextEdit):
            return widget
        return None

    def copy_text(self):
        current_widget = self.get_current_text_widget()
        if current_widget:
            current_widget.copy()

    def paste_text(self):
        current_widget = self.get_current_text_widget()
        if current_widget:
            current_widget.paste()

    def cut_text(self):
        current_widget = self.get_current_text_widget()
        if current_widget:
            current_widget.cut()

    def create_menu_bar(self):
        menu_bar = self.menuBar()

        file_menu = menu_bar.addMenu("Archivo")

        new_action = QAction("Nuevo archivo", self)
        new_action.triggered.connect(self.add_new_tab)
        new_action.setShortcut("Ctrl+N")
        file_menu.addAction(new_action)

        open_action = QAction("Abrir", self)
        open_action.triggered.connect(self.open_file)
        open_action.setShortcut("Ctrl+O")
        file_menu.addAction(open_action)

        recent_menu = file_menu.addMenu("Abrir reciente")
        self.recent_menu = recent_menu

        save_action = QAction("Guardar", self)
        save_action.triggered.connect(self.save_file)
        save_action.setShortcut("Ctrl+S")
        file_menu.addAction(save_action)

        save_as_action = QAction("Guardar como", self)
        save_as_action.triggered.connect(self.save_file_as_original)
        save_as_action.setShortcut("Ctrl+Shift+S")
        file_menu.addAction(save_as_action)

        save_as_encoding_action = QAction("Guardar Codificacion como...", self)
        save_as_encoding_action.triggered.connect(self.save_file_with_encoding)
        file_menu.addAction(save_as_encoding_action)

        file_menu.addSeparator()

        exit_action = QAction("Salir", self)
        exit_action.triggered.connect(self.close)
        exit_action.setShortcut("Ctrl+Q")
        file_menu.addAction(exit_action)

        edit_menu = menu_bar.addMenu("Editar")

        undo_action = QAction("Deshacer", self)
        undo_action.triggered.connect(lambda: self.get_current_text_widget().undo())
        undo_action.setShortcut("Ctrl+Z")
        edit_menu.addAction(undo_action)

        redo_action = QAction("Rehacer", self)
        redo_action.triggered.connect(lambda: self.get_current_text_widget().redo())
        redo_action.setShortcut("Ctrl+Shift+Z")
        edit_menu.addAction(redo_action)

        edit_menu.addSeparator()

        find_action = QAction("Buscar", self)
        find_action.setShortcut("Ctrl+F")
        find_action.triggered.connect(self.show_find_panel)
        edit_menu.addAction(find_action)

        replace_action = QAction("Reemplazar", self)
        replace_action.setShortcut("Ctrl+H")
        replace_action.triggered.connect(self.show_replace_panel)
        edit_menu.addAction(replace_action)

        find_in_files_action = QAction("Buscar/Reemplazar en archivos...", self)
        find_in_files_action.setShortcut("Ctrl+Shift+F")
        find_in_files_action.triggered.connect(self.show_find_in_files_dialog)
        edit_menu.addAction(find_in_files_action)

        edit_menu.addSeparator()

        copy_action = QAction("Copiar", self)
        copy_action.triggered.connect(self.copy_text)
        copy_action.setShortcut("Ctrl+C")
        edit_menu.addAction(copy_action)

        paste_action = QAction("Pegar", self)
        paste_action.triggered.connect(self.paste_text)
        paste_action.setShortcut("Ctrl+V")
        edit_menu.addAction(paste_action)

        cut_action = QAction("Cortar", self)
        cut_action.triggered.connect(self.cut_text)
        cut_action.setShortcut("Ctrl+X")
        edit_menu.addAction(cut_action)

        select_all_action = QAction("Seleccionar todo", self)
        select_all_action.triggered.connect(lambda: self.get_current_text_widget().selectAll())
        select_all_action.setShortcut("Ctrl+A")
        edit_menu.addAction(select_all_action)

        tools_menu = menu_bar.addMenu("Herramientas")

        synonyms_action = QAction("Sinonimos...", self)
        synonyms_action.setShortcut("Ctrl+F7")
        synonyms_action.triggered.connect(self.show_synonyms_dialog)
        tools_menu.addAction(synonyms_action)

        options_menu = menu_bar.addMenu("Opciones")

        sharps_action = QAction("Usar Sostenidos al bajar semitonos", self)
        sharps_action.setCheckable(True)
        sharps_action.setChecked(self.config["use_sharps"])
        sharps_action.triggered.connect(lambda: self.toggle_accidentals(True))
        options_menu.addAction(sharps_action)

        flats_action = QAction("Usar Bemoles al bajar semitonos", self)
        flats_action.setCheckable(True)
        flats_action.setChecked(not self.config["use_sharps"])
        flats_action.triggered.connect(lambda: self.toggle_accidentals(False))
        options_menu.addAction(flats_action)

        options_menu.addSeparator()

        group = QActionGroup(self)
        group.addAction(sharps_action)
        group.addAction(flats_action)

        change_font_action = QAction("Cambiar fuente", self)
        change_font_action.triggered.connect(self.select_font)
        change_font_action.setShortcut("Ctrl+Alt+F")
        options_menu.addAction(change_font_action)

        change_speed_action = QAction("Cambiar velocidad maxima", self)
        change_speed_action.triggered.connect(self.change_max_speed)
        change_speed_action.setShortcut("Ctrl+Shift+V")
        options_menu.addAction(change_speed_action)

        help_menu = menu_bar.addMenu("Ayuda")

        about_action = QAction("Acerca de...", self)
        about_action.triggered.connect(self.show_about_dialog)
        about_action.setShortcut("Ctrl+H")
        help_menu.addAction(about_action)

    def selected_word_for_synonyms(self):
        text_widget = self.get_current_text_widget()
        if not text_widget:
            return ""

        cursor = text_widget.textCursor()
        selected = cursor.selectedText().strip()
        if selected:
            return selected

        cursor.select(QTextCursor.SelectionType.WordUnderCursor)
        selected = cursor.selectedText().strip()
        if selected:
            text_widget.setTextCursor(cursor)
        return selected

    def show_synonyms_dialog(self):
        if not self.thesaurus.languages:
            QMessageBox.warning(
                self,
                "Sinonimos",
                "No se encontraron diccionarios Mythes en /usr/share/mythes.",
            )
            return

        word = self.selected_word_for_synonyms()
        if not word:
            QMessageBox.information(self, "Sinonimos", "Selecciona una palabra para buscar sinonimos.")
            return

        dialog = SynonymsDialog(self, word)
        dialog.exec()

    def replace_selected_word(self, replacement):
        text_widget = self.get_current_text_widget()
        if not text_widget:
            return

        cursor = text_widget.textCursor()
        if not cursor.hasSelection():
            cursor.select(QTextCursor.SelectionType.WordUnderCursor)

        cursor.insertText(replacement)
        text_widget.setTextCursor(cursor)
        text_widget.setFocus()

    def show_find_in_files_dialog(self):
        try:
            self._fif_dialog.show()
            self._fif_dialog.raise_()
            self._fif_dialog.activateWindow()
            return
        except AttributeError:
            pass

        self._fif_dialog = FindInFilesDialog(self)
        self._fif_dialog.show()

    def open_file_at(self, file_path: str, line: int, col: int):
        self.open_dropped_file(file_path)
        text_widget = self.get_current_text_widget()
        if not text_widget:
            return

        line = max(1, line)
        block = text_widget.document().findBlockByLineNumber(line - 1)
        if not block.isValid():
            return

        cursor = text_widget.textCursor()
        cursor.setPosition(block.position() + max(0, col - 1))
        text_widget.setTextCursor(cursor)
        text_widget.setFocus()

    def update_recent_files_menu(self):
        self.recent_menu.clear()
        recent_files = self.config.get("recent_files", [])

        for entry in recent_files:
            file_path = entry["path"]
            timestamp = entry["timestamp"]

            action = QAction(f"{os.path.basename(file_path)} - {timestamp}", self)
            action.triggered.connect(lambda checked, path=file_path: self.open_recent_file(path))
            self.recent_menu.addAction(action)

            path_action = QAction(f"Ruta: {file_path}", self)
            path_action.setEnabled(False)
            self.recent_menu.addAction(path_action)

        if not recent_files:
            self.recent_menu.addAction("No hay archivos recientes").setEnabled(False)

    def open_recent_file(self, file_path):
        if os.path.exists(file_path):
            self.open_dropped_file(file_path)
        else:
            QMessageBox.warning(self, "Error", f"El archivo '{file_path}' no existe.")

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            event.ignore()

    def dragMoveEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            event.ignore()

    def dropEvent(self, event: QDropEvent):
        if event.mimeData().hasUrls():
            url = event.mimeData().urls()[0]
            file_path = url.toLocalFile()
            self.open_dropped_file(file_path)
            event.acceptProposedAction()
        else:
            event.ignore()

    def open_dropped_file(self, file_path):
        if os.path.exists(file_path) and file_path.lower().endswith(".txt"):
            try:
                content, info = read_file(file_path)
                encoding = info["encoding"]
                line_ending = info["line_ending"]

                self.file_encodings[file_path] = {
                    "encoding": encoding,
                    "line_ending": line_ending,
                }
                self.encoding_label.setText(
                    f"Codificacion: {encoding} | Terminador de linea: {line_ending}"
                )

                current_widget = self.get_current_text_widget()
                if current_widget and not current_widget.toPlainText().strip():
                    current_widget.setPlainText(content)
                    index = self.tab_widget.indexOf(current_widget)
                    self.tab_widget.setTabText(index, os.path.basename(file_path))
                    self.opened_files[index] = file_path
                else:
                    self.add_new_tab(
                        file_name=os.path.basename(file_path),
                        content=content,
                        file_path=file_path,
                    )

                self.config["last_opened_path"] = os.path.dirname(file_path)
                self.save_config()
                self.update_window_title()
                self.add_to_recent_files(file_path)
            except Exception as error:
                QMessageBox.critical(self, "Error", f"No se pudo abrir el archivo: {error}")
        else:
            QMessageBox.warning(self, "Error", "El archivo no es valido o no existe.")

    def new_file(self):
        current_widget = self.get_current_text_widget()
        if current_widget:
            current_widget.clear()
        self.current_file = None
        self.setWindowTitle("Lector y Editor de Texto - Nuevo archivo")

    def add_to_recent_files(self, file_path):
        self.config = add_to_recent_files(self.config, file_path)
        self.save_config()
        self.update_recent_files_menu()

    def open_file(self):
        last_path = self.config.get("last_opened_path", "")
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Abrir archivo", last_path, "Archivos de texto (*.txt)"
        )
        if file_path:
            try:
                content, info = read_file(file_path)
                encoding = info["encoding"]
                line_ending = info["line_ending"]

                self.file_encodings[file_path] = {
                    "encoding": encoding,
                    "line_ending": line_ending,
                }
                self.encoding_label.setText(
                    f"Codificacion: {encoding} | Terminador de linea: {line_ending}"
                )

                current_widget = self.get_current_text_widget()
                if current_widget and not current_widget.toPlainText().strip():
                    current_widget.setPlainText(content)
                    index = self.tab_widget.indexOf(current_widget)
                    self.tab_widget.setTabText(index, os.path.basename(file_path))
                    self.opened_files[index] = file_path
                else:
                    self.add_new_tab(
                        file_name=os.path.basename(file_path),
                        content=content,
                        file_path=file_path,
                    )

                self.config["last_opened_path"] = os.path.dirname(file_path)
                self.save_config()
                self.update_window_title()
                self.add_to_recent_files(file_path)
            except Exception as error:
                QMessageBox.critical(self, "Error", f"No se pudo abrir el archivo: {error}")

    def load_file(self, file_path):
        try:
            with open(file_path, "r", encoding="utf-8") as file:
                content = file.read()
                current_widget = self.get_current_text_widget()
                if current_widget:
                    current_widget.setPlainText(content)
            self.current_file = file_path
            self.setWindowTitle(f"Lector y Editor de Texto - {os.path.basename(file_path)}")
        except Exception as error:
            QMessageBox.critical(self, "Error", f"No se pudo abrir el archivo: {error}")

    def save_file(self):
        current_widget = self.get_current_text_widget()
        if not current_widget:
            QMessageBox.warning(self, "Error", "No hay ninguna pestana activa para guardar.")
            return

        index = self.tab_widget.currentIndex()
        file_path = self.opened_files.get(index)

        if file_path:
            try:
                encoding = self.file_encodings.get(file_path, {}).get("encoding", "utf-8")
                line_ending = self.file_encodings.get(file_path, {}).get(
                    "line_ending", "Unix (LF)"
                )

                content = current_widget.toPlainText()
                write_file(file_path, content, encoding, line_ending)
            except Exception as error:
                QMessageBox.critical(self, "Error", f"No se pudo guardar el archivo: {error}")
        else:
            self.save_file_as()

        current_widget.document().setModified(False)
        self.update_window_title()

    def save_file_as(self):
        self.save_file_as_original()

    def save_file_as_original(self):
        current_widget = self.get_current_text_widget()
        if not current_widget:
            QMessageBox.warning(self, "Error", "No hay ninguna pestana activa para guardar.")
            return

        index = self.tab_widget.currentIndex()
        suggested_name = self.opened_files.get(index, "Nuevo archivo.txt")
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Guardar archivo", suggested_name, "Archivos de texto (*.txt)"
        )
        if file_path:
            try:
                encoding = self.file_encodings.get(suggested_name, {}).get("encoding", "utf-8")
                line_ending = self.file_encodings.get(suggested_name, {}).get(
                    "line_ending", "Unix (LF)"
                )

                content = current_widget.toPlainText()
                write_file(file_path, content, encoding, line_ending)

                self.opened_files[index] = file_path
                self.file_encodings[file_path] = {
                    "encoding": encoding,
                    "line_ending": line_ending,
                }
                self.tab_widget.setTabText(index, os.path.basename(file_path))
            except Exception as error:
                QMessageBox.critical(self, "Error", f"No se pudo guardar el archivo: {error}")

    def save_file_with_encoding(self):
        current_widget = self.get_current_text_widget()
        if not current_widget:
            QMessageBox.warning(self, "Error", "No hay ninguna pestana activa para guardar.")
            return

        index = self.tab_widget.currentIndex()
        suggested_name = self.opened_files.get(index, "Nuevo archivo.txt")
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Guardar archivo", suggested_name, "Archivos de texto (*.txt)"
        )
        if file_path:
            encoding, ok = QInputDialog.getItem(
                self,
                "Seleccionar codificacion",
                "Codificacion:",
                ["UTF-8", "UTF-16 LE", "UTF-16 BE", "UTF-8 con BOM", "ANSI", "ISO-8859-1"],
                0,
                False,
            )
            if not ok:
                return

            line_ending, ok = QInputDialog.getItem(
                self,
                "Seleccionar terminador de linea",
                "Terminador de linea:",
                ["Windows (CRLF)", "Unix (LF)", "Mac (CR)"],
                0,
                False,
            )
            if not ok:
                return

            try:
                content = current_widget.toPlainText()

                if encoding == "UTF-8 con BOM":
                    with open(file_path, "w", encoding="utf-8-sig") as file:
                        file.write(content)
                elif encoding == "ANSI":
                    with open(file_path, "w", encoding="windows-1252") as file:
                        file.write(content)
                else:
                    write_file(file_path, content, encoding.lower().replace(" ", "-"), line_ending)

                self.opened_files[index] = file_path
                self.file_encodings[file_path] = {
                    "encoding": encoding,
                    "line_ending": line_ending,
                }
                self.tab_widget.setTabText(index, os.path.basename(file_path))
            except Exception as error:
                QMessageBox.critical(self, "Error", f"No se pudo guardar el archivo: {error}")

    def start_scrolling(self):
        if not self.is_scrolling:
            self.is_scrolling = True
            self.scroll_text()

    def pause_scrolling(self):
        self.is_scrolling = False

    def scroll_text(self):
        if self.is_scrolling:
            current_widget = self.get_current_text_widget()
            if current_widget:
                scrollbar = current_widget.verticalScrollBar()
                scrollbar.setValue(scrollbar.value() + 1)
            QTimer.singleShot(self.scroll_speed, self.scroll_text)

    def calculate_speed(self, value):
        min_speed = 1
        factor = math.log(self.max_speed / min_speed) / 29
        return max(1, int(min_speed * math.exp(factor * (30 - value))))

    def update_speed(self):
        self.scroll_speed = self.calculate_speed(self.speed_slider.value())
        self.config["last_slider_position"] = self.speed_slider.value()
        self.save_config()

    def change_max_speed(self):
        new_max_speed, ok = QInputDialog.getInt(
            self,
            "Cambiar velocidad maxima",
            "Ingrese la nueva velocidad maxima (1-1000):",
            value=self.max_speed,
            min=1,
            max=1000,
        )
        if ok:
            self.max_speed = new_max_speed
            self.update_speed()
            self.save_config()
            QMessageBox.information(
                self,
                "Velocidad actualizada",
                f"La velocidad maxima se ha actualizado a {self.max_speed}.\n"
                f"Use el control deslizante para ajustar la velocidad entre 1 y {self.max_speed}.",
            )

    def show_transpose_menu(self):
        transpose_menu = QMenu(self)
        for semitones in range(-7, 8):
            action = QAction(f"{semitones:+d}" if semitones != 0 else "0 (Original)", self)
            action.triggered.connect(lambda checked, value=semitones: self.transpose_chords(value))
            transpose_menu.addAction(action)
        transpose_menu.exec(self.transpose_button.mapToGlobal(self.transpose_button.rect().bottomLeft()))

    def transpose_chords(self, semitones):
        current_widget = self.get_current_text_widget()
        if current_widget:
            current_scroll_position = current_widget.verticalScrollBar().value()
            content = current_widget.toPlainText()
        else:
            return

        transposed_content = self.transpose_text(content, semitones)
        cursor = current_widget.textCursor()
        cursor.beginEditBlock()
        cursor.select(QTextCursor.SelectionType.Document)
        cursor.insertText(transposed_content)
        cursor.endEditBlock()
        current_widget.verticalScrollBar().setValue(current_scroll_position)

    def transpose_text(self, text, semitones):
        return transpose_text(text, semitones, self.config["use_sharps"])

    def save_config(self):
        self.config_manager.save(self.config)

    def toggle_accidentals(self, use_sharps):
        self.config["use_sharps"] = use_sharps
        self.save_config()


__all__ = ["CustomTextEdit", "TextScrollerApp"]
