<p align="center">
  <h1 align="center">GuitarChordStudio</h1>
  <p align="center">
    A suite of guitar chord editing applications for musicians, singers and songwriters
  </p>
</p>

<p align="center">
  <a href="LICENSE">
    <img src="https://img.shields.io/badge/License-GPL%20v3-blue.svg?style=flat-square" alt="License: GPL v3">
  </a>
  <img src="https://img.shields.io/badge/Python-3.11%2B-3776AB?style=flat-square&logo=python&logoColor=white" alt="Python 3.11+">
  <img src="https://img.shields.io/badge/Platform-Linux%20%7C%20Windows%20%7C%20macOS-9cf?style=flat-square" alt="Platform">
  <img src="https://img.shields.io/badge/GUI-PyQt6-41CD52?style=flat-square&logo=qt&logoColor=white" alt="PyQt6">
  <img src="https://img.shields.io/badge/Code%20Style-PEP%208-ff69b4?style=flat-square" alt="PEP 8">
</p>

---

## Overview

This repository is organized as a suite of applications for working with guitar
chord lyrics, similar to how WPS Office bundles multiple tools. It currently
includes:

| Application | Description |
|---|---|
| **chordflow** | Single-page lyrics and chords editor with autoscroll for rehearsals and performances |
| **chordpages** | Page-oriented WYSIWYG editor with multi-page layout, configurable margins, and print-ready output |

### Quick Start

```bash
# Run chordflow
python3 -m chordflow

# Run chordpages
python3 -m chordpages
```

After installing the Python package, the same commands work as system-wide
launchers:

```bash
chordflow
chordpages
```

---

## Table of Contents

- [ChordFlow — Autoscroll Editor](#chordflow-application)
- [ChordPages — WYSIWYG Page Editor](#chordpages-application)
- [Development Dependencies](#development-dependencies)
- [Roadmap](#roadmap)
- [License](#license)

---

# ChordFlow Application

A tabbed text editor for guitarists, singers and musicians who work with song
lyrics and chords in plain text files. Open songs, transpose chords, scroll
automatically during practice, search across multiple files, and look up
synonyms using system Mythes dictionaries.

Designed for **Debian 12**, **MX Linux 23**, **antiX 23** and derivative
distributions.

## Features

- Tabbed text editor with drag-and-drop support
- Automatic encoding and line-ending detection
- Chord transposition by semitones (sharps/flats toggle)
- Autoscroll with adjustable speed for hands-free rehearsals
- Search and replace within a document or across multiple files
- Thesaurus integration via system Mythes dictionaries
- Customizable monospaced font
- Save with encoding selection (UTF-8, UTF-16, ANSI, ISO-8859-1, etc.)
- Recent files list with timestamps
- Undo/redo support

## Installing Dependencies

On Debian 12, MX Linux 23, antiX 23 and derivatives:

```bash
sudo apt-get update
sudo apt-get install python3 python3-pyqt6 python3-chardet \
    qt6-translations-l10n fonts-noto-mono mythes mythes-en-us mythes-es
```

For synonyms in other languages, install the corresponding Mythes package.
The following dictionaries are available in Debian and Ubuntu:

| Package | Language |
|---|---|
| `mythes-ar` | Arabic |
| `mythes-bg` | Bulgarian |
| `mythes-ca` | Catalan |
| `mythes-cs` | Czech |
| `mythes-da` | Danish |
| `mythes-de` | German |
| `mythes-de-ch` | Swiss German |
| `mythes-en-au` | Australian English |
| `mythes-en-us` | American English |
| `mythes-es` | Spanish |
| `mythes-fr` | French |
| `mythes-gl` | Galician |
| `mythes-gug` | Guarani |
| `mythes-hu` | Hungarian |
| `mythes-id` | Indonesian |
| `mythes-is` | Icelandic |
| `mythes-it` | Italian |
| `mythes-lv` | Latvian |
| `mythes-ne` | Nepali |
| `mythes-no` | Norwegian |
| `mythes-pl` | Polish |
| `mythes-pt-br` | Brazilian Portuguese |
| `mythes-pt-pt` | European Portuguese |
| `mythes-ro` | Romanian |
| `mythes-ru` | Russian |
| `mythes-sk` | Slovak |
| `mythes-sl` | Slovenian |
| `mythes-sv` | Swedish |
| `mythes-uk` | Ukrainian |

Install one or more of them, for example:

```bash
sudo apt-get install mythes-en-us mythes-fr mythes-de
```

## Running

```bash
python3 -m chordflow
```

## Basic Usage

### Opening Songs

- Drag a `.txt` file onto the window.
- Or use `File > Open`.

Example songs are included in the `Ejemplo/` folder.

### Transposing Chords

Use the `Transpose` button to raise or lower semitones. In `Options` you can
choose between sharps or flats.

### Autoscroll

| Action | Description |
|---|---|
| `Start` | Begins automatic scrolling |
| `Pause` | Stops scrolling |
| Speed slider | Adjusts the scroll speed |
| `Options > Change max speed` | Adjusts the speed range |

### Search and Replace

The `Edit` menu provides `Find`, `Replace`, and `Find/Replace in files...` for
searching across a folder. Supports case-sensitive matching and regular
expressions.

### Thesaurus

Select a word and use `Tools > Thesaurus...` or `Ctrl+F7` to look up synonyms
via system Mythes dictionaries.

## Saving Files

| Option | Description |
|---|---|
| **Save** | Saves using the original encoding and line ending |
| **Save As...** | Saves to a new location preserving original encoding |
| **Save Encoding As...** | Saves with a chosen encoding and line ending |

Available encodings: UTF-8, UTF-16 LE, UTF-16 BE, UTF-8 with BOM, ANSI,
ISO-8859-1.

Available line endings: Windows (CRLF), Unix (LF), Mac (CR).

## Keyboard Shortcuts

| Function | Shortcut |
|---|---|
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

The [Cancionero](https://github.com/wachin/Cancionero) repository provides a
collection of lyrics and chords compatible with this program.

## Fonts

Monospaced fonts are recommended for chord alignment. The default is
`Noto Mono`. Other options include Consolas, Iosevka, Liberation Mono, and
DejaVu Sans Mono.

## Dependency Notes

- **`python3`** — Python interpreter required to run the program.
- **`python3-pyqt6`** — GUI framework providing the user interface (windows,
  buttons, menus, text editor, file dialogs, etc.).
- **`python3-chardet`** — Automatically detects text file encoding on open
  (UTF-8, ISO-8859-1, Windows-1252, etc.). Without it, the user would have to
  specify the encoding manually. Also used in the "Find/Replace in files"
  feature to read files with any encoding.
- **`qt6-translations-l10n`** — Translations for native Qt dialogs (Open, Save,
  Cancel buttons appear in the system language).
- **`fonts-noto-mono`** — Default monospaced font for the editor.
- **`mythes`** — Base support for thesaurus dictionaries (the same ones used by
  LibreOffice). Without this package, the Thesaurus feature has no dictionaries
  to load.
- **`mythes-es`** — Spanish thesaurus dictionary. For other languages, install
  the corresponding package from the table above.

---

# ChordPages Application

A WYSIWYG page-oriented editor for songs with guitar lyrics and chords. Unlike
`chordflow`, which displays text in a single scrollable view, ChordPages
organizes content into real pages (A4, Letter, custom sizes) that appear on
screen exactly as they would be printed.

Designed for composers, arrangers, and musicians who prefer a real page layout
with configurable margins and a multi-page view.

## Features

- WYSIWYG editing on real pages with background, border, and shadow
- 3-up view: three pages per row within a vertical scroll
- View modes: one page, two pages, or three pages per row
- Configurable margins in millimeters with presets (normal, narrow, moderate,
  wide, mirror)
- Page size support: A4, Letter, Legal, landscape/portrait, and custom
- Zoom: zoom in, zoom out, 100%, fit to width, fit to page — font scales with
  zoom (like LibreOffice)
- Basic editing: typing, Enter, Tab, Backspace, Delete, mouse/keyboard selection
- Copy, cut, paste, select all, undo/redo
- Open and save files in `.mchord` and plain text formats
- PDF export through Qt's printing system
- Built-in paginator that splits text into pages
- Automatic reflow when changing zoom, paper, font, or margins
- Cursor measured with `QTextLayout` for precise alignment
- Application theme: system, light, and dark
- Preferences dialog with live language selection
- Background autosave for crash recovery
- Automatic backups before overwriting documents
- Recovery dialog on startup if unsaved drafts exist
- Version snapshots for restorable `.mchord` history
- Spanish and English translations via Qt Linguist
- Drag-and-drop file support

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

## Running

```bash
python3 -m chordpages
```

## Running the Tests

```bash
pytest -q chordpages/tests/
```

## Translation Workflow

ChordPages uses Qt Linguist for translations. Update translation files after
changing user-visible strings:

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

# Development Dependencies

These packages are only required for running tests or working with translations,
not for running the applications themselves.

### Debian / MX Linux

```bash
sudo apt-get install python3-pytest python3-pytest-qt \
    pyqt6-dev-tools qt6-l10n-tools
```

- **`python3-pytest`** — Test runner for the test suite.
- **`python3-pytest-qt`** — Provides the `qtbot` fixture for testing Qt widgets
  (opening windows, clicking, typing, etc.).
- **`pyqt6-dev-tools`** — Provides `pylupdate6` for extracting translatable
  strings from source code.
- **`qt6-l10n-tools`** — Provides `linguist-qt6` (translation editor) and
  `lrelease` (`.ts` to `.qm` compiler).

### Windows / macOS

```bash
pip install pytest pytest-qt
```

---

# Configuration Files

Each application stores its settings in the platform's standard configuration
directory, under a shared `guitarchs` folder:

| Application | Linux | Windows | macOS |
|---|---|---|---|
| **chordflow** | `~/.config/guitarchs/chordflow/config.json` | `%APPDATA%\guitarchs\chordflow\config.json` | `~/Library/Application Support/guitarchs/chordflow/config.json` |
| **chordpages** | `~/.config/guitarchs/chordpages/settings.ini` | `%APPDATA%\guitarchs\chordpages\settings.ini` | `~/Library/Application Support/guitarchs/chordpages/settings.ini` |

The files are created automatically when you first run the corresponding
application. You can delete them to reset all settings to defaults.

---

# Roadmap

See [ROADMAP.md](ROADMAP.md) for the current implementation status and planned
features for both applications.

---

# License

<p align="center">
  <img src="https://www.gnu.org/graphics/gplv3-127x51.png" alt="GPL v3 Logo">
</p>

This project is intended to be released under the **GNU General Public License
v3**. See the [LICENSE](LICENSE) file for details.

---

*God bless you.*