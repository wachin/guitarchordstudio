# GuitarChordStudio

This repository is organized as a suite of applications, similar to WPS Office.
It currently includes:

- `chordflow`: lyrics and chords editor with autoscroll.
- `chordpages`: page-oriented WYSIWYG editor with real page layout,
  configurable margins and multi-page support.

## Running the Applications

From the repository root:

```bash
python3 -m chordflow
python3 -m chordpages
```

If you install the project as a Python package, two launchers will be available:

```bash
chordflow
chordpages
```

---

# ChordFlow Application

Lyrics and chords editor for guitarists, singers and musicians who work with
songs in text files. It lets you open songs, transpose chords, scroll
automatically during practice, search and replace text, search across multiple
files, and look up synonyms using Mythes dictionaries installed on Linux.

The program is designed for Debian 12, MX Linux 23, antiX 23 and derivative
distributions.

## Features

- Tabbed text editor.
- Open `.txt` files.
- Drag and drop files onto the window.
- Save, `Save As...` and save with a chosen encoding.
- Encoding and line-ending detection.
- Recent files list.
- Autoscroll for rehearsals.
- Scroll speed control.
- Chord transposition by semitones.
- Option to use sharps or flats.
- Search and replace within the document.
- Search and replace in files from `Edit > Find/Replace in files...`.
- Synonyms from `Tools > Thesaurus...`, using Mythes dictionaries such as `mythes-es`.
- Font selection.
- Keyboard shortcuts for the main actions.

## Tested Systems

- Debian 12 32-bit.
- MX Linux 23 32-bit and 64-bit.

## Installing Dependencies

On Debian 12, MX Linux 23, antiX 23 and derivatives, install the dependencies
with:

```bash
sudo apt-get update
sudo apt-get install python3 python3-pyqt6 python3-chardet \
    qt6-translations-l10n fonts-noto-mono mythes mythes-es
```

To get synonyms in another language, install the corresponding Mythes package.
For example:

```bash
sudo apt-get install mythes-de
```

## Running the Program

From the project folder:

```bash
python3 -m chordflow
```

You can also run it from a file manager if your distribution has an option to
launch Python scripts.

## Basic Usage

### Opening Songs

You can open songs in two ways:

- Drag a `.txt` file onto the window.
- Use `File > Open`.

The project includes example songs in the `Ejemplo/` folder.

### Transposing Chords

Use the `Transpose` button to raise or lower semitones. This lets you adapt a
song to your voice or instrument tuning.

In `Options` you can choose whether the transposition uses sharps or flats.

### Autoscroll

The program can scroll the lyrics automatically while you play or sing.

- `Start`: begins scrolling.
- `Pause`: stops scrolling.
- Speed control: adjusts how fast the text scrolls.
- `Options > Change max speed`: changes the available speed range.

### Search and Replace

The `Edit` menu provides:

- `Find`: shows the search panel.
- `Replace`: shows the search and replace panel.
- `Find/Replace in files...`: searches or replaces text in multiple files within
  a folder.

The search supports case-sensitive matching and regular expressions.

### Synonyms

If you have packages like `mythes` and `mythes-es` installed, you can select a
word and use:

```text
Tools > Thesaurus...
```

or the shortcut:

```text
Ctrl+F7
```

A window similar to LibreOffice's will open, with alternatives and a field to
replace the selected word.

### Changing the Font

In `Options > Change font` you can choose the editor font. A monospaced font is
recommended to keep chords aligned with the lyrics. The default is `Noto Mono`.

## Saving Files

The `File` menu includes three save options:

### Save

Saves the file using the same encoding and line ending detected when it was
opened.

### Save As...

Saves the file to another location, preserving the original encoding and line
ending.

### Save Encoding As...

Lets you choose the encoding and line ending before saving.

Available encodings:

- UTF-8
- UTF-16 LE
- UTF-16 BE
- UTF-8 with BOM
- ANSI
- ISO-8859-1

Available line endings:

- Windows (CRLF)
- Unix (LF)
- Mac (CR)

## Keyboard Shortcuts

| Function | Shortcut |
| --- | --- |
| New file | `Ctrl+N` |
| Open file | `Ctrl+O` |
| Save file | `Ctrl+S` |
| Save as | `Ctrl+Shift+S` |
| Quit | `Ctrl+Q` |
| Find | `Ctrl+F` |
| Find/Replace in files | `Ctrl+Shift+F` |
| Thesaurus | `Ctrl+F7` |
| Select all | `Ctrl+A` |
| Change font | `Ctrl+Alt+F` |
| Change max speed | `Ctrl+Shift+V` |
| About | `Ctrl+H` |
| Undo | `Ctrl+Z` |
| Redo | `Ctrl+Shift+Z` |
| Start/Pause scroll | `Ctrl+Space` |

## Recommended Songbook

You can also use this program with the lyrics and chords songbook available at:

[https://github.com/wachin/Cancionero](https://github.com/wachin/Cancionero)

The songs are in the folder:

```text
Acordes de Guitarra para celular (63x110mm)
```

## Fonts

When editing songs with chords, monospaced fonts are recommended. Some
recommendations:

- Noto Mono
- Consolas
- Iosevka
- Liberation Mono
- DejaVu Sans Mono

Related articles:

- [Installing Windows fonts on Linux](https://facilitarelsoftwarelibre.blogspot.com/2018/11/instalar-fuentes-de-windows-en.html)
- [How to install downloaded fonts on Linux](https://facilitarelsoftwarelibre.blogspot.com/2021/01/como-instalar-fuentes-tipograficas-en-linux.html)
- [Monospaced fonts misaligned in WPS Office](https://facilitarelsoftwarelibre.blogspot.com/2022/05/problema-con-las-fuentes-monoespaciadas.html)

## Dependency Notes

- `python3`: interpreter required to run the program.
- `python3-pyqt6`: GUI library providing the user interface (windows, buttons,
  menus, text editor, file dialogs, etc.).
- `python3-chardet`: automatically detects the encoding of a text file when
  opened (UTF-8, ISO-8859-1, Windows-1252, etc.). Without this library, the
  user would have to specify the encoding manually every time they open a file,
  and files created on Windows (ANSI, UTF-8 with BOM) or macOS (Mac Roman)
  would not open correctly. It is also used in the "Find/Replace in files"
  feature to read files with any encoding within a folder.
- `qt6-translations-l10n`: translations of native Qt dialogs into Spanish and
  other languages. For example, the "Open", "Save", "Cancel" buttons in file
  dialogs appear in Spanish when the system is set to that language.
- `fonts-noto-mono`: default recommended monospaced font for the editor.
  Monospaced fonts keep chords vertically aligned with the lyrics, which is
  essential for correct song display.
- `mythes`: base support for thesaurus dictionaries. The program uses Mythes
  dictionaries installed on the system (the same ones used by LibreOffice) to
  offer synonyms. Without this package, the "Thesaurus..." option in the Tools
  menu would have no dictionaries to load.
- `mythes-es`: Spanish thesaurus dictionary for Mythes. Lets you look up
  synonyms in Spanish from the `Tools > Thesaurus...` menu. For other languages
  you can install packages such as `mythes-de` (German), `mythes-en` (English),
  etc.

---

# ChordPages Application

ChordPages is a page-oriented WYSIWYG editor for songs with guitar lyrics and
chords. Unlike `chordflow`, which displays text in a single scrollable view,
ChordPages organizes content into real pages (such as A4 or Letter) that appear
on screen exactly as they would be printed.

The program is designed for composers, arrangers and musicians who prefer to
work with a real page layout, configurable margins and a multi-page view.

## Features

- WYSIWYG editing on real pages with background, border and shadow.
- 3-up view: three pages per row within a vertical scroll.
- View modes: one page, two pages, and three pages per row.
- Configurable margins in millimeters with presets (normal, narrow, moderate,
  wide, mirror).
- Page size support: A4, Letter, Legal, landscape/portrait and custom size.
- Zoom: zoom in, zoom out, 100%, fit to width and fit to page.
- Basic editing: typing, Enter, Tab, Backspace, Delete, mouse and keyboard
  selection.
- Copy, cut, paste and select all.
- Open and save files in `.mchord` and plain text formats.
- PDF export through Qt's printing system.
- Built-in paginator that splits text into pages based on characters per line
  and lines per page.
- Automatic reflow when changing zoom, paper, font and margins.
- Cursor measured with `QTextLayout` for precise alignment like a native editor.
- Application theme: system, light and dark.
- Preferences dialog with live language selection.
- Background autosave for crash recovery.
- Automatic backups before overwriting documents.
- Recovery dialog on startup if unsaved drafts exist.
- Version snapshots for restorable `.mchord` history.
- Spanish and English translations via Qt Linguist.
- Drag and drop file support.

## Tested Systems

- Debian 12 / MX Linux 23 64-bit.
- Windows (with Python 3.11+ and PyQt6).
- macOS (with Python 3.11+ and PyQt6).

## Installing Dependencies

### Debian / MX Linux

```bash
sudo apt-get update
sudo apt-get install python3 python3-pyqt6 \
    qt6-translations-l10n
```

### Windows

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install PyQt6 pytest
```

### macOS

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install PyQt6 pytest
```

## Running the Program

```bash
python3 -m chordpages
```

## Running the Tests

```bash
pytest -q chordpages/tests/
```

## Translation Workflow

ChordPages maintains Qt Linguist translation files in `chordpages/translations/`.
On startup, it loads `chordpages_<locale>.qm` with `QTranslator`.

Update translation files after changing user-visible strings:

```bash
pylupdate6 chordpages/ --ts chordpages/translations/chordpages_es.ts
pylupdate6 chordpages/ --ts chordpages/translations/chordpages_en.ts
```

Edit with Qt Linguist and compile:

```bash
linguist-qt6 chordpages/translations/chordpages_es.ts
lrelease chordpages/translations/chordpages_es.ts -qm chordpages/translations/chordpages_es.qm
lrelease chordpages/translations/chordpages_en.ts -qm chordpages/translations/chordpages_en.qm
```

---

## Development Dependencies

These packages are only needed if you plan to run the tests or work with
translations. They are not required to run the applications.

### Debian / MX Linux

```bash
sudo apt-get install python3-pytest python3-pytest-qt \
    pyqt6-dev-tools qt6-l10n-tools
```

- `python3-pytest`: test runner. Required to run the test suite with `pytest`.
- `python3-pytest-qt`: provides the `qtbot` fixture for creating and
  manipulating Qt widgets during tests (opening windows, clicking, typing text,
  etc.). Without this package, tests that interact with the graphical interface
  cannot be run.
- `pyqt6-dev-tools`: provides `pylupdate6`, the tool that extracts translatable
  strings from source code to generate `.ts` files for Qt Linguist.
- `qt6-l10n-tools`: provides `linguist-qt6` (visual translation editor) and
  `lrelease` (compiler from `.ts` to `.qm`). They are used in the translation
  workflow.

### Windows / macOS

```bash
pip install pytest pytest-qt
```

---

## Roadmap

See [ROADMAP.md](ROADMAP.md) for what has already been implemented and the
planned ideas for future versions of both applications.

## License

The programs are intended to be released under GPL 3.

God bless you.