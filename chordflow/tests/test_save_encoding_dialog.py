"""Save-encoding dialog options and selected values."""

from __future__ import annotations

from chordflow.ui.save_encoding_dialog import SaveEncodingDialog


def test_dialog_exposes_encoding_and_line_ending_choices(qtbot):
    dialog = SaveEncodingDialog()
    qtbot.addWidget(dialog)

    encoding = dialog.findChild(type(dialog.encoding_combo), "saveEncodingComboBox")
    line_ending = dialog.findChild(
        type(dialog.line_ending_combo), "saveLineEndingComboBox"
    )
    assert encoding is not None
    assert line_ending is not None
    assert encoding.count() == 6
    assert line_ending.count() == 3
    assert [encoding.itemText(i) for i in range(encoding.count())] == [
        "UTF-8",
        "UTF-16 LE",
        "UTF-16 BE",
        "UTF-8 con BOM",
        "ANSI (Windows-1252)",
        "ISO-8859-1",
    ]
    assert dialog.selected_codec() == "utf-8"
    encoding.setCurrentIndex(4)
    assert dialog.selected_codec() == "cp1252"
