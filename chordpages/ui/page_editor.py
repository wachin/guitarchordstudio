"""A page-oriented QTextEdit surface for the initial prototype."""

from __future__ import annotations

from collections.abc import Sequence

from PyQt6.QtCore import QSize, Qt, pyqtSignal
from PyQt6.QtGui import QColor, QFont, QTextCursor, QTextDocument
from PyQt6.QtWidgets import (
    QFrame,
    QGridLayout,
    QGraphicsDropShadowEffect,
    QScrollArea,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from chordpages.document.page import DEFAULT_SCREEN_DPI, PageLayout
from chordpages.fonts import default_editor_font
from chordpages.chord_token_filter import is_chord_token
from chordpages.spellcheck import install_spell_checker


PAGE_CANVAS_MARGIN_PX = 24
PAGE_SPACING_PX = 24
MIN_ZOOM = 0.25
MAX_ZOOM = 4.0
SINGLE_PAGE_VIEW_COLUMNS = 1
MULTIPLE_PAGE_VIEW_COLUMNS = 3
PAGE_GRID_START_COLUMN = 1
MISSPELLING_COLOR_LIGHT = "#d02020"
MISSPELLING_COLOR_DARK = "#ffd54f"


class PageWidget(QFrame):
    """Visual page frame with a writable text area inside the margins."""

    def __init__(
        self,
        layout: PageLayout | None = None,
        editor_font: QFont | None = None,
        editable: bool = True,
        dark_mode: bool = False,
        parent: QWidget | None = None,
    ):
        super().__init__(parent)
        self._layout = layout or PageLayout()
        self._zoom = 1.0
        self._dark_mode = bool(dark_mode)
        self._base_font = QFont(editor_font or default_editor_font())
        self.editor = QTextEdit(self)
        self.editor.setObjectName("pageTextEditor")
        self.editor.setFrameShape(QFrame.Shape.NoFrame)
        self.editor.setAcceptRichText(False)
        self.editor.setLineWrapMode(QTextEdit.LineWrapMode.WidgetWidth)
        self._apply_zoom_font()
        decorator = install_spell_checker(self.editor)
        if decorator is not None:
            decorator.add_token_filter(is_chord_token)
        self._apply_misspelling_color()
        self.editor.setVerticalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )
        self.editor.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )
        self.editor.setPlaceholderText(self.tr("Write your song here..."))
        self.safe_area_frame = QFrame(self)
        self.safe_area_frame.setObjectName("printerSafeAreaFrame")
        self.safe_area_frame.setAttribute(
            Qt.WidgetAttribute.WA_TransparentForMouseEvents,
            True,
        )

        self.setObjectName("pageWidget")
        self._apply_page_style()
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(18.0)
        shadow.setOffset(0.0, 4.0)
        shadow.setColor(QColor(0, 0, 0, 55))
        self.setGraphicsEffect(shadow)
        self.set_editable(editable)
        self._apply_layout()

    def set_dark_mode(self, dark_mode: bool) -> None:
        """Apply dark or light paper colors without changing the document."""
        dark_mode = bool(dark_mode)
        if dark_mode == self._dark_mode:
            return
        self._dark_mode = dark_mode
        self._apply_page_style()
        self._apply_misspelling_color()

    def _apply_misspelling_color(self) -> None:
        """Use a high-contrast wave underline on dark paper."""
        decorator = getattr(self.editor, "_linguistic_decorator", None)
        if decorator is None:
            return
        try:
            highlighter = decorator.highlighter
            text_format = highlighter.misspelling_format
            text_format.setUnderlineColor(
                QColor(
                    MISSPELLING_COLOR_DARK
                    if self._dark_mode
                    else MISSPELLING_COLOR_LIGHT
                )
            )
            highlighter.set_misspelling_format(text_format)
        except (AttributeError, RuntimeError):
            return

    def _apply_page_style(self) -> None:
        if self._dark_mode:
            page_background = "#1e1f22"
            page_text = "#f1f3f4"
            page_border = "#3c4043"
            selection_background = "#3d8bfd"
            selection_text = "#ffffff"
            safe_area_border = "#6b7280"
        else:
            page_background = "white"
            page_text = "#202124"
            page_border = "#c8c8c8"
            selection_background = "#b8d7ff"
            selection_text = "#111827"
            safe_area_border = "#9aa0a6"
        self.setStyleSheet(
            f"""
            QFrame#pageWidget {{
                background: {page_background};
                border: 1px solid {page_border};
            }}

            QTextEdit#pageTextEditor {{
                background: {page_background};
                color: {page_text};
                selection-background-color: {selection_background};
                selection-color: {selection_text};
            }}

            QFrame#printerSafeAreaFrame {{
                background: transparent;
                border: 1px dashed {safe_area_border};
            }}
            """
        )

    def page_layout(self) -> PageLayout:
        return self._layout

    def set_page_layout(self, layout: PageLayout) -> None:
        self._layout = layout
        self._apply_layout()

    def set_zoom(self, zoom: float) -> None:
        self._zoom = clamped_zoom(zoom)
        self._apply_layout()
        self._apply_zoom_font()

    def zoom(self) -> float:
        return self._zoom

    def set_editable(self, editable: bool) -> None:
        self.editor.setReadOnly(not editable)
        self.editor.setFocusPolicy(
            Qt.FocusPolicy.StrongFocus if editable else Qt.FocusPolicy.NoFocus
        )

    def is_editable(self) -> bool:
        return not self.editor.isReadOnly()

    def editor_font(self) -> QFont:
        return self.editor.document().defaultFont()

    def set_editor_font(self, font: QFont) -> None:
        self._base_font = QFont(font)
        self._apply_zoom_font()

    def text(self) -> str:
        return self.editor.toPlainText()

    def set_text(self, text: str) -> None:
        self.editor.setPlainText(text)

    def reset_spellcheck_document(self) -> None:
        """Rebuild the document and highlighter after the page is laid out.

        The first QTextEdit document created inside the page-editor layout does
        not reliably accept QSyntaxHighlighter formats on Qt 6. Replacing it
        with a fresh document keeps the decorator and chord filter attached.
        """
        decorator = getattr(self.editor, "_linguistic_decorator", None)
        if decorator is not None:
            decorator.detach()
        self.editor.setDocument(QTextDocument(self.editor))
        self._apply_zoom_font()
        decorator = install_spell_checker(self.editor)
        if decorator is not None:
            decorator.add_token_filter(is_chord_token)
        self._apply_misspelling_color()

    def text_height_for(self, text: str) -> float:
        document = QTextDocument()
        document.setDefaultFont(self.editor.font())
        document.setDocumentMargin(self.editor.document().documentMargin())
        document.setTextWidth(self._document_text_width())
        document.setPlainText(text)
        return document.documentLayout().documentSize().height()

    def text_fits(self, text: str) -> bool:
        return self.text_height_for(text) <= self.editor.height() + 0.5

    def sizeHint(self) -> QSize:
        width, height = self._layout.page_size_px(DEFAULT_SCREEN_DPI, self._zoom)
        return QSize(width, height)

    def resizeEvent(self, event) -> None:  # noqa: ANN001 - Qt override
        super().resizeEvent(event)
        self._place_safe_area_frame()
        self._place_editor()

    def _apply_layout(self) -> None:
        width, height = self._layout.page_size_px(DEFAULT_SCREEN_DPI, self._zoom)
        self.setFixedSize(width, height)
        self.updateGeometry()
        self._place_safe_area_frame()
        self._place_editor()

    def _apply_zoom_font(self) -> None:
        """Scale the base font by the current zoom factor."""
        scaled = QFont(self._base_font)
        scaled.setPointSizeF(self._base_font.pointSizeF() * self._zoom)
        self.editor.setFont(scaled)
        self.editor.document().setDefaultFont(scaled)

    def _place_editor(self) -> None:
        left, top, right, bottom = self._layout.margin_px(
            DEFAULT_SCREEN_DPI,
            self._zoom,
        )
        self.editor.setGeometry(
            left,
            top,
            max(1, self.width() - left - right),
            max(1, self.height() - top - bottom),
        )
        self.safe_area_frame.raise_()

    def _document_text_width(self) -> int:
        document_margin = int(self.editor.document().documentMargin() * 2)
        return max(1, self.editor.width() - document_margin)

    def _place_safe_area_frame(self) -> None:
        if not self._layout.has_printer_safe_area():
            self.safe_area_frame.setVisible(False)
            return

        left, top, right, bottom = self._layout.printer_margin_px(
            DEFAULT_SCREEN_DPI,
            self._zoom,
        )
        self.safe_area_frame.setGeometry(
            left,
            top,
            max(1, self.width() - left - right),
            max(1, self.height() - top - bottom),
        )
        self.safe_area_frame.setVisible(True)


class PageEditor(QWidget):
    """Scrollable editor that presents a real page boundary."""

    textChanged = pyqtSignal()

    def __init__(
        self,
        editor_font: QFont | None = None,
        parent: QWidget | None = None,
    ):
        super().__init__(parent)
        self.setObjectName("pageEditor")
        self._pages: list[PageWidget] = []
        self._dark_mode = False
        self._pages_per_row = MULTIPLE_PAGE_VIEW_COLUMNS
        self._editor_font = editor_font or default_editor_font()
        self._full_text = ""
        self._setting_page_text = False

        self._scroll_area = QScrollArea()
        self._scroll_area.setObjectName("pageScrollArea")
        self._scroll_area.setWidgetResizable(True)
        self._scroll_area.setAlignment(
            Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop
        )

        self._content = QWidget()
        self._content.setObjectName("pageCanvas")
        self._content_layout = QGridLayout(self._content)
        self._content_layout.setContentsMargins(
            PAGE_CANVAS_MARGIN_PX,
            PAGE_CANVAS_MARGIN_PX,
            PAGE_CANVAS_MARGIN_PX,
            PAGE_CANVAS_MARGIN_PX,
        )
        self._content_layout.setSpacing(PAGE_SPACING_PX)
        self._scroll_area.setWidget(self._content)
        self.page = self._append_page(PageLayout(), editable=True)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self._scroll_area)
        self.page.reset_spellcheck_document()
        self.page.editor.document().contentsChanged.connect(
            lambda page=self.page: self._handle_page_text_changed(page)
        )

    def center_page(self) -> None:
        """Center the current page horizontally after a viewport change."""
        self._content_layout.activate()
        scrollbar = self._scroll_area.horizontalScrollBar()
        scrollbar.setValue((scrollbar.minimum() + scrollbar.maximum()) // 2)

    def text(self) -> str:
        return self._full_text

    def set_text(self, text: str) -> None:
        self._full_text = text
        self._paginate_full_text()

    def text_document(self):
        return self.page.editor.document()

    def set_dark_mode(self, dark_mode: bool) -> None:
        """Apply the page theme to every current page and future pages."""
        dark_mode = bool(dark_mode)
        self._dark_mode = dark_mode
        for page in self._pages:
            page.set_dark_mode(dark_mode)

    def editor_font(self) -> QFont:
        return QFont(self._editor_font)

    def set_editor_font(self, font: QFont) -> None:
        self._editor_font = QFont(font)
        cursor_position = self._global_cursor_position(self._active_page())
        self._setting_page_text = True
        try:
            for page in self._pages:
                page.set_editor_font(self._editor_font)
        finally:
            self._setting_page_text = False
        if self._full_text:
            self._paginate_full_text(cursor_position)

    def page_count(self) -> int:
        return len(self._pages)

    def pages(self) -> tuple[PageWidget, ...]:
        return tuple(self._pages)

    def page_at(self, page_index: int) -> PageWidget:
        if page_index < 0 or page_index >= len(self._pages):
            raise IndexError("Page editor page index out of range.")
        return self._pages[page_index]

    def page_layout(self) -> PageLayout:
        return self.page.page_layout()

    def set_page_layout(self, layout: PageLayout) -> None:
        self.set_page_layouts(tuple(layout for _ in self._pages))
        if self._full_text:
            self._paginate_full_text()

    def page_layouts(self) -> tuple[PageLayout, ...]:
        return tuple(page.page_layout() for page in self._pages)

    def set_page_layouts(self, layouts: Sequence[PageLayout]) -> None:
        page_layouts = tuple(layouts)
        if not page_layouts:
            raise ValueError("Page editor must contain at least one page.")

        while len(self._pages) > len(page_layouts):
            self._remove_last_page()

        while len(self._pages) < len(page_layouts):
            self._append_page(page_layouts[len(self._pages)], editable=True)

        for page, layout in zip(self._pages, page_layouts):
            page.set_editable(True)
            page.set_page_layout(layout)
            page.set_zoom(self.zoom())

        self.page = self._pages[0]

    def set_page_count(
        self,
        page_count: int,
        layout: PageLayout | None = None,
    ) -> None:
        if page_count < 1:
            raise ValueError("Page editor must contain at least one page.")
        page_layout = layout or self.page_layout()
        self.set_page_layouts(tuple(page_layout for _ in range(page_count)))

    def zoom(self) -> float:
        return self.page.zoom()

    def set_zoom(self, zoom: float) -> None:
        for page in self._pages:
            page.set_zoom(zoom)
        if self._full_text:
            self._paginate_full_text()

    def pages_per_row(self) -> int:
        return self._pages_per_row

    def set_pages_per_row(self, pages_per_row: int) -> None:
        if pages_per_row < 1:
            raise ValueError("Pages per row must be at least one.")
        self._pages_per_row = pages_per_row
        self._reflow_page_grid()

    def set_single_page_view(self) -> None:
        self.set_pages_per_row(SINGLE_PAGE_VIEW_COLUMNS)

    def set_multiple_page_view(self) -> None:
        self.set_pages_per_row(MULTIPLE_PAGE_VIEW_COLUMNS)

    def fit_width_zoom(self, viewport_size: QSize | None = None) -> float:
        """Return the zoom needed to fit the widest visible page row."""
        page_width, _ = self._unzoomed_view_size()
        available_width, _ = self._available_canvas_size(viewport_size)
        return clamped_zoom(available_width / page_width)

    def fit_page_zoom(self, viewport_size: QSize | None = None) -> float:
        """Return the zoom needed to fit the visible page row in the viewport."""
        page_width, page_height = self._unzoomed_view_size()
        available_width, available_height = self._available_canvas_size(viewport_size)
        return clamped_zoom(
            min(available_width / page_width, available_height / page_height)
        )

    def fit_width(self) -> float:
        self.set_zoom(self.fit_width_zoom())
        return self.zoom()

    def fit_page(self) -> float:
        self.set_zoom(self.fit_page_zoom())
        return self.zoom()

    def _append_page(self, layout: PageLayout, editable: bool) -> PageWidget:
        page = PageWidget(
            layout=layout,
            editor_font=self._editor_font,
            editable=editable,
            dark_mode=self._dark_mode,
            parent=self._content,
        )
        page.editor.document().contentsChanged.connect(
            lambda page=page: self._handle_page_text_changed(page)
        )
        self._pages.append(page)
        self._reflow_page_grid()
        return page

    def _remove_last_page(self) -> None:
        page = self._pages.pop()
        self._content_layout.removeWidget(page)
        page.setParent(None)
        page.deleteLater()
        self._reflow_page_grid()

    def _reflow_page_grid(self) -> None:
        for page in self._pages:
            self._content_layout.removeWidget(page)

        self._reset_grid_stretch()

        for page_index, page in enumerate(self._pages):
            row = page_index // self._pages_per_row
            column = PAGE_GRID_START_COLUMN + (page_index % self._pages_per_row)
            self._content_layout.addWidget(
                page,
                row,
                column,
                Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop,
            )

        self._content_layout.setColumnStretch(0, 1)
        self._content_layout.setColumnStretch(
            PAGE_GRID_START_COLUMN + self._pages_per_row,
            1,
        )
        row_count = max(
            1,
            (len(self._pages) + self._pages_per_row - 1) // self._pages_per_row,
        )
        self._content_layout.setRowStretch(row_count, 1)
        self._content.updateGeometry()

    def _reset_grid_stretch(self) -> None:
        for column in range(self._content_layout.columnCount() + 1):
            self._content_layout.setColumnStretch(column, 0)
        for row in range(self._content_layout.rowCount() + 1):
            self._content_layout.setRowStretch(row, 0)

    def _paginate_full_text(self, cursor_position: int | None = None) -> None:
        page_chunks = self._page_text_chunks(self._full_text)
        page_layout = self.page_layout()
        self.set_page_layouts(tuple(page_layout for _ in page_chunks))
        self._set_page_texts(page_chunks)
        if cursor_position is not None:
            self._restore_cursor(cursor_position)

    def _set_page_texts(self, page_texts: Sequence[str]) -> None:
        self._setting_page_text = True
        try:
            for page, page_text in zip(self._pages, page_texts):
                # Keep document signals enabled: the spelling highlighter and
                # its async controller listen to contentsChange. The
                # _setting_page_text guard prevents recursive pagination.
                if page.text() != page_text:
                    page.set_text(page_text)
        finally:
            self._setting_page_text = False

    def _handle_page_text_changed(self, changed_page: PageWidget) -> None:
        if self._setting_page_text:
            return
        cursor_position = self._global_cursor_position(changed_page)
        self._full_text = "".join(page.text() for page in self._pages)
        self._paginate_full_text(cursor_position)
        self.textChanged.emit()

    def _global_cursor_position(self, cursor_page: PageWidget) -> int:
        cursor_position = 0
        for page in self._pages:
            if page is cursor_page:
                return cursor_position + page.editor.textCursor().position()
            cursor_position += len(page.text())
        return cursor_position

    def _active_page(self) -> PageWidget:
        for page in self._pages:
            if page.editor.hasFocus():
                return page
        return self.page

    def _restore_cursor(self, cursor_position: int) -> None:
        page_start = 0
        for page in self._pages:
            page_text_length = len(page.text())
            page_end = page_start + page_text_length
            if cursor_position <= page_end:
                cursor = QTextCursor(page.editor.document())
                cursor.setPosition(max(0, cursor_position - page_start))
                page.editor.setTextCursor(cursor)
                if page.is_editable():
                    page.editor.setFocus()
                return
            page_start = page_end

        if self._pages:
            last_page = self._pages[-1]
            cursor = QTextCursor(last_page.editor.document())
            cursor.setPosition(len(last_page.text()))
            last_page.editor.setTextCursor(cursor)

    def _page_text_chunks(self, text: str) -> tuple[str, ...]:
        if text == "":
            return ("",)

        chunks: list[str] = []
        current_chunk = ""

        for source_line in text.splitlines(keepends=True):
            candidate = f"{current_chunk}{source_line}"
            if current_chunk and not self.page.text_fits(candidate):
                chunks.append(current_chunk)
                current_chunk = source_line
            else:
                current_chunk = candidate

            if current_chunk and not self.page.text_fits(current_chunk):
                oversized_chunks = self._split_oversized_line(current_chunk)
                chunks.extend(oversized_chunks[:-1])
                current_chunk = oversized_chunks[-1]

        if current_chunk:
            chunks.append(current_chunk)

        return tuple(chunks) or ("",)

    def _split_oversized_line(self, line: str) -> tuple[str, ...]:
        chunks: list[str] = []
        current_chunk = ""
        for character in line:
            candidate = f"{current_chunk}{character}"
            if current_chunk and not self.page.text_fits(candidate):
                chunks.append(current_chunk)
                current_chunk = character
            else:
                current_chunk = candidate

        if current_chunk:
            chunks.append(current_chunk)

        return tuple(chunks) or (line,)

    def _available_canvas_size(
        self,
        viewport_size: QSize | None = None,
    ) -> tuple[int, int]:
        size = viewport_size or self._scroll_area.viewport().size()
        margins = self._content_layout.contentsMargins()
        return (
            max(1, size.width() - margins.left() - margins.right()),
            max(1, size.height() - margins.top() - margins.bottom()),
        )

    def _unzoomed_view_size(self) -> tuple[int, int]:
        row_widths: list[int] = []
        row_heights: list[int] = []
        for row_start in range(0, len(self._pages), self._pages_per_row):
            row_pages = self._pages[row_start : row_start + self._pages_per_row]
            page_sizes = [
                page.page_layout().page_size_px(DEFAULT_SCREEN_DPI)
                for page in row_pages
            ]
            row_widths.append(
                sum(width for width, _ in page_sizes)
                + (PAGE_SPACING_PX * max(0, len(page_sizes) - 1))
            )
            row_heights.append(max(height for _, height in page_sizes))

        return max(row_widths), max(row_heights)


def clamped_zoom(zoom: float) -> float:
    """Return a zoom value within the supported page rendering range."""
    return max(MIN_ZOOM, min(zoom, MAX_ZOOM))
