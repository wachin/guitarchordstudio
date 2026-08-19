# ROADMAP — PyQt6 Linguistic Tools

## Project goal

Create a reusable, cross-platform linguistic toolkit for **Python + PyQt6** applications that provides:

- Spell checking.
- Spelling suggestions.
- Personal dictionaries.
- Ignore-word support.
- Thesaurus / synonyms.
- Unicode-safe text handling.
- Linux, Windows and macOS support.
- Integration with `QTextEdit`.
- Integration with `QPlainTextEdit`.
- Reusable architecture independent from GuitarChordStudio.

This repository must be designed as a reusable component that can be added as a Git submodule to multiple PyQt6 applications.

Current intended architecture:

```text
GuitarChordStudio
        │
        └── libs/
            └── pyqt6-linguistic-tools
                     │
                     ├── libss/
                     │      ├── spylls
                     │      └── pythes
                     │
                     ├── core/
                     │      ├── linguistic_service
                     │      ├── dictionary_registry
                     │      └── backends
                     │
                     └── qt/
                            ├── decorator
                            ├── spell_highlighter
                            ├── context_menu
                            └── thesaurus_dialog
```

---

# IMPORTANT ARCHITECTURAL REFERENCE: SONNET

The developer has intentionally placed as sub-module of the **Sonnet** source code at:

```text
third-party/sonnet
```

Sonnet must be studied as an **architectural reference only**.

Sonnet is a mature Qt spell-checking framework and contains useful architectural ideas such as:

- Plugin/backend abstraction.
- Separation between the text editor and the spell-checking engine.
- Spell-check decorators for existing Qt text widgets.
- Multiple spell-checking backends.
- Language management.
- Automatic language detection concepts.
- Context-menu integration.
- Personal dictionary handling.
- Spell-checking dialogs and UI integration.


## Critical restriction

- [ ] DO NOT integrate Sonnet into this project.
- [ ] DO NOT compile Sonnet.
- [ ] DO NOT create Python bindings for Sonnet.
- [ ] DO NOT make Sonnet a runtime dependency.
- [ ] DO NOT call Sonnet from PyQt6.
- [ ] DO NOT copy C++ implementation code directly into Python.
- [ ] DO NOT make the project depend on KDE Frameworks or other Sonnet dependencies.

The reason is simple:

```text
Sonnet = C++ / Qt
pyqt6-linguistic-tools = Python / PyQt6
```

Sonnet therefore does not fit our runtime architecture.

Use Sonnet only to understand **good architectural patterns** and then implement equivalent concepts cleanly and idiomatically in Python.

The final product must remain a **Python-first PyQt6 library**.

---

# Phase 0 — Repository foundation

- [ ] Review the current repository structure.
- [ ] Create a clean Python package structure.
- [ ] Create `pyproject.toml`.
- [ ] Define minimum supported Python version.
- [ ] Define minimum supported PyQt6 version.
- [ ] Create `README.md`.
- [ ] Create `CHANGELOG.md`.
- [ ] Create `CONTRIBUTING.md`.
- [ ] Keep this `ROADMAP.md` updated.
- [ ] Add `.gitignore`.
- [ ] Add typing configuration.
- [ ] Add `pytest`.
- [ ] Add basic logging infrastructure.
- [ ] Define semantic versioning.
- [ ] Start development version as `0.1.0-dev`.

---

# Phase 1 — Submodule structure

The library must own its linguistic engine dependencies.

Target structure:

```text
pyqt6-linguistic-tools/
│
├── libs/
│   ├── spylls/
│   └── pythes/
│
├── third-party/
│   ├── hunspell/
│   └── sonnet/
│
├── src/
│   └── pyqt6_linguistic_tools/
│
├── tests/
├── examples/
├── pyproject.toml
└── ROADMAP.md
```

- [ ] Keep `third-party/sonnet` only as architectural reference.
- [ ] Keep `third-party/sonnet` only as reference of the spylls hunspell fork
- [ ] Document submodule initialization.
- [ ] Document recursive cloning.
- [ ] Verify:

```bash
git submodule update --init --recursive
```

- [ ] Ensure applications using this repository do not need to add Spylls and PyThes separately.

---

# Phase 2 — Study Sonnet architecture

Before designing our public API, inspect the Sonnet source code in:

```text
third-party/sonnet
```

Study specifically:

- [ ] Backend/plugin architecture.
- [ ] Spell-check decorator architecture.
- [ ] Dictionary discovery logic.
- [ ] Language selection.
- [ ] Automatic language detection concepts.
- [ ] Personal dictionary architecture.
- [ ] Ignore-word architecture.
- [ ] Suggestion APIs.
- [ ] Context-menu integration.
- [ ] Text-editor integration.
- [ ] Configuration separation.
- [ ] Error-handling design.
- [ ] How Sonnet avoids coupling applications directly to Hunspell.

Create internal development notes describing:

```text
Sonnet concept
      ↓
Python/PyQt6 equivalent
```

Example:

```text
Sonnet SpellCheckDecorator
          ↓
LinguisticTextEditDecorator
```

Do not port implementation line by line.

---

# Phase 3 — Spylls audit

Spylls will be the initial primary spelling backend.

- [ ] Review the complete Spylls fork.
- [ ] Understand `.aff` parsing.
- [ ] Understand `.dic` parsing.
- [ ] Understand `lookup()`.
- [ ] Understand `suggest()`.
- [ ] Understand encoding handling.
- [ ] Verify Hunspell `SET` handling.
- [ ] Test UTF-8 dictionaries.
- [ ] Test ISO-8859-* dictionaries.
- [ ] Test other encodings found in LibreOffice dictionaries.
- [ ] Test accented Spanish words.
- [ ] Test `ñ`.
- [ ] Test combining Unicode characters.
- [ ] Test languages outside Western European alphabets.
- [ ] Benchmark `lookup()`.
- [ ] Benchmark `suggest()`.
- [ ] Investigate long-word suggestion performance.
- [ ] Never add arbitrary limits such as rejecting suggestions above 12 characters.
- [ ] Add tests before changing Spylls behavior.
- [ ] Keep modifications to the fork as small and maintainable as possible.
- [ ] Document every deviation from upstream Spylls.

---

# Phase 4 — PyThes audit and modernization

PyThes will provide the initial MyThes backend.

- [ ] Review the complete PyThes fork.
- [ ] Understand `.dat` parsing.
- [ ] Understand `.idx` parsing.
- [ ] Understand encoding detection.
- [ ] Understand byte-offset lookup.
- [ ] Modernize paths using `pathlib`.
- [ ] Add modern type hints.
- [ ] Improve exceptions.
- [ ] Add structured result types.
- [ ] Test UTF-8 thesauri.
- [ ] Test non-UTF-8 thesauri.
- [ ] Validate `.idx → .dat` byte offsets.
- [ ] Detect corrupted indexes.
- [ ] Add ability to regenerate an index from `.dat`.
- [ ] Allow fallback operation without a usable `.idx`.
- [ ] Add Unicode normalization.
- [ ] Add caching.
- [ ] Add extensive tests.
- [ ] Document every deviation from upstream PyThes.

---

# Phase 5 — Preserve original dictionary encodings

Do not assume all dictionaries must be converted to UTF-8.

General rule:

```text
Original LibreOffice dictionary encoding
                ↓
Spylls / PyThes
                ↓
Python Unicode str
                ↓
PyQt6
```

- [ ] Preserve original upstream encoding whenever the file is valid.
- [ ] Do not mass-convert dictionaries to UTF-8.
- [ ] Respect Hunspell `SET`.
- [ ] Respect MyThes encoding declarations.
- [ ] Ensure the application API always returns Python Unicode strings.
- [ ] Add tests for legacy encodings.
- [ ] Add tests for mixed-language collections.
- [ ] Repair dictionary files only when demonstrably broken.

---

# Phase 6 — Dictionary validation tools

Create reusable validation utilities.

## Hunspell

- [ ] Validate `.aff` existence.
- [ ] Validate `.dic` existence.
- [ ] Validate declared encoding.
- [ ] Load dictionary through Spylls.
- [ ] Test representative words.
- [ ] Detect malformed rules.

## MyThes

- [ ] Validate `.dat`.
- [ ] Validate `.idx`.
- [ ] Validate encoding.
- [ ] Validate index entry count.
- [ ] Validate every sampled byte offset.
- [ ] Confirm that the indexed word matches the `.dat` entry.
- [ ] Detect broken offsets caused by encoding conversion.
- [ ] Regenerate index when requested.

Output statuses such as:

```text
PASS
WARNING
FAIL
```

---

# Phase 7 — Core backend interfaces

The rest of the library must never depend directly on Spylls or PyThes.

Create abstract APIs.

## SpellCheckerBackend

- [ ] Create `SpellCheckerBackend`.
- [ ] Define `load_dictionary()`.
- [ ] Define `check_word()`.
- [ ] Define `suggest()`.
- [ ] Define `add_word()` where supported.
- [ ] Define `remove_word()` where supported.
- [ ] Define `available()`.
- [ ] Define backend metadata.

Potential future implementations:

```text
SpellCheckerBackend
        │
        ├── SpyllsBackend
        ├── EnchantBackend
        ├── NativeHunspellBackend
        └── OtherBackend
```

Only `SpyllsBackend` is required initially.

---

# Phase 8 — Thesaurus backend interface

Create:

```text
ThesaurusBackend
```

- [ ] Define `load_dictionary()`.
- [ ] Define `lookup()`.
- [ ] Define `synonyms()`.
- [ ] Preserve meanings.
- [ ] Preserve parts of speech.
- [ ] Preserve alternate senses.
- [ ] Expose capabilities.
- [ ] Implement `PyThesBackend`.

Potential future implementations must remain possible without changing the public API.

---

# Phase 9 — DictionaryRegistry

Create a central `DictionaryRegistry`.

Example model:

```python
@dataclass
class DictionaryInfo:
    locale: str
    aff_path: Path | None
    dic_path: Path | None
    thesaurus_dat: Path | None
    thesaurus_idx: Path | None
    source: str
```

- [ ] Discover spelling dictionaries.
- [ ] Discover thesauri.
- [ ] Pair files correctly by locale.
- [ ] Support regional variants.
- [ ] Detect spelling-only languages.
- [ ] Detect thesaurus-only languages.
- [ ] Detect languages providing both.
- [ ] Handle duplicate dictionaries.
- [ ] Define source priority.
- [ ] Cache discovery results.
- [ ] Provide human-readable language names.

---

# Phase 10 — Dictionary providers

Dictionary location must be separated from linguistic engines.

Create a provider interface.

```text
DictionaryProvider
        │
        ├── LinuxSystemDictionaryProvider
        ├── ManagedDictionaryProvider
        ├── UserDictionaryProvider
        └── future providers
```

---

# Phase 11 — Linux provider

Linux applications must use system dictionaries where possible.

Search locations such as:

```text
/usr/share/hunspell
/usr/share/myspell
/usr/share/myspell/dicts
/usr/share/mythes
```

- [ ] Detect system Hunspell dictionaries.
- [ ] Detect system MyThes thesauri.
- [ ] Never install Linux packages automatically.
- [ ] Never request root privileges.
- [ ] Never modify system dictionary files.
- [ ] Clearly report missing dictionaries.
- [ ] Allow applications to tell users which packages may need installation.
- [ ] Support user-provided dictionaries in addition to system dictionaries.

---

# Phase 12 — Windows provider

- [ ] Use application/user data directories.
- [ ] Use `QStandardPaths` when Qt is available.
- [ ] Support managed dictionaries.
- [ ] Support manual import.
- [ ] Prepare integration with `libreoffice-dictionaries-collection`.
- [ ] Do not require system-wide Hunspell.
- [ ] Do not require DLL-based Hunspell.

---

# Phase 13 — macOS provider

- [ ] Use application/user data directories.
- [ ] Use `QStandardPaths`.
- [ ] Support managed dictionaries.
- [ ] Support manual import.
- [ ] Prepare integration with `libreoffice-dictionaries-collection`.
- [ ] Avoid native binary dependencies whenever possible.

---

# Phase 14 — PersonalDictionary

Create a backend-independent personal dictionary.

- [ ] Store custom words by locale.
- [ ] Add words.
- [ ] Remove words.
- [ ] List words.
- [ ] Persist safely.
- [ ] Use UTF-8 for our own generated personal dictionary files.
- [ ] Support application-specific storage locations.
- [ ] Support shared storage if explicitly configured.
- [ ] Never modify LibreOffice/Hunspell source dictionaries.

---

# Phase 15 — Ignore-word management

Implement separately from personal dictionaries.

- [ ] Ignore once.
- [ ] Ignore for current document.
- [ ] Ignore for current session.
- [ ] Clear ignored words.
- [ ] Ensure ignored words do not modify permanent dictionaries.

---

# Phase 16 — Unicode tokenizer

Do not use limited patterns such as:

```python
[a-zA-ZÀ-ÿ]
```

Create Unicode-aware word tokenization.

- [ ] Support Spanish accents.
- [ ] Support `ñ`.
- [ ] Support apostrophes.
- [ ] Support linguistically valid hyphens.
- [ ] Support Cyrillic.
- [ ] Support Greek.
- [ ] Prepare for additional scripts.
- [ ] Exclude URLs.
- [ ] Exclude email addresses.
- [ ] Exclude numbers when appropriate.
- [ ] Exclude configurable technical tokens.
- [ ] Provide token positions in the original text.

---

# Phase 17 — LinguisticService

Create the main application-facing service.

Target API:

```python
service = LinguisticService(language="es_ES")

service.check_word("computadora")
service.suggestions("computdora")
service.synonyms("rápido")
```

- [ ] Integrate `DictionaryRegistry`.
- [ ] Integrate `SpellCheckerBackend`.
- [ ] Integrate `ThesaurusBackend`.
- [ ] Integrate `PersonalDictionary`.
- [ ] Integrate ignore-word management.
- [ ] Implement `set_language()`.
- [ ] Implement `check_word()`.
- [ ] Implement `suggestions()`.
- [ ] Implement `synonyms()`.
- [ ] Implement `available_languages()`.
- [ ] Implement `capabilities(locale)`.
- [ ] Add graceful error handling.
- [ ] Add caching.
- [ ] Keep the service independent of widgets.

---

# Phase 18 — Caching

- [ ] Cache spelling results by `(locale, word)`.
- [ ] Cache suggestions by `(locale, word)`.
- [ ] Cache thesaurus results by `(locale, word)`.
- [ ] Invalidate caches when dictionaries change.
- [ ] Invalidate relevant entries when personal dictionary changes.
- [ ] Use bounded caches.
- [ ] Benchmark memory consumption.

---

# Phase 19 — Qt integration architecture

Create a separate Qt integration package.

Suggested structure:

```text
qt/
├── decorator.py
├── spell_highlighter.py
├── context_menu.py
├── thesaurus_dialog.py
├── dictionary_manager.py
└── settings.py
```

Core linguistic logic must remain usable without importing Qt widgets.

---

# Phase 20 — Sonnet-inspired decorator

Implement a Python/PyQt6 equivalent of Sonnet's decorator concept.

Goal:

```python
editor = QTextEdit()

integration = LinguisticTextEditDecorator(
    editor,
    service
)
```

or eventually:

```python
enable_linguistics(
    editor,
    language="es_ES"
)
```

- [ ] Do not require subclassing `QTextEdit`.
- [ ] Do not require subclassing `QPlainTextEdit`.
- [ ] Attach behavior to existing editors.
- [ ] Allow removal/disabling of integration.
- [ ] Preserve host application's existing context menu.
- [ ] Preserve host application's signals and behavior.
- [ ] Allow host applications to add custom actions.

---

# Phase 21 — QTextEdit support

- [ ] Support existing `QTextEdit` instances.
- [ ] Detect word under cursor.
- [ ] Highlight misspellings.
- [ ] Replace misspelled words.
- [ ] Integrate context menu.
- [ ] Open thesaurus.
- [ ] Change language.
- [ ] Enable/disable spell checking.

---

# Phase 22 — QPlainTextEdit support

- [ ] Support existing `QPlainTextEdit` instances.
- [ ] Provide feature parity with `QTextEdit` where possible.
- [ ] Test large plain-text documents.
- [ ] Avoid excessive repainting.

---

# Phase 23 — QSyntaxHighlighter

Create:

```text
SpellCheckHighlighter
```

- [ ] Use `QSyntaxHighlighter`.
- [ ] Underline misspelled words.
- [ ] Prefer a red wave underline where supported.
- [ ] Do not perform expensive suggestion generation inside `highlightBlock()`.
- [ ] Avoid re-checking unchanged words unnecessarily.
- [ ] Rehighlight affected blocks only.
- [ ] Allow configurable visual style.
- [ ] Allow disabling highlighting separately from linguistic services.

---

# Phase 24 — Asynchronous spell checking

The UI must remain responsive.

- [ ] Add debounce after typing.
- [ ] Start around 300 ms and make configurable.
- [ ] Use worker infrastructure for expensive operations.
- [ ] Evaluate `QThreadPool`.
- [ ] Evaluate `QRunnable`.
- [ ] Never create one thread per word.
- [ ] Cancel obsolete jobs.
- [ ] Ignore stale results.
- [ ] Test long documents.
- [ ] Test long words.
- [ ] Test rapid typing.

---

# Phase 25 — Context menu

Create reusable context-menu integration.

For misspelled words, provide:

```text
Suggestion 1
Suggestion 2
Suggestion 3
────────────
Ignore
Ignore All
Add to Dictionary
────────────
Synonyms >
Open Thesaurus...
────────────
Language >
```

- [ ] Keep existing application actions.
- [ ] Insert linguistic actions cleanly.
- [ ] Replace words safely.
- [ ] Support configurable suggestion count.
- [ ] Support synonyms submenu.
- [ ] Support language submenu.
- [ ] Allow applications to disable individual actions.

---

# Phase 26 — Thesaurus dialog

Create a reusable `ThesaurusDialog`.

- [ ] Show queried word.
- [ ] Show meanings.
- [ ] Show part of speech.
- [ ] Show synonyms.
- [ ] Allow selecting a synonym.
- [ ] Allow replacement in the editor.
- [ ] Allow searching selected synonyms.
- [ ] Add navigation history.
- [ ] Add Back.
- [ ] Add Forward.
- [ ] Handle no-result cases.
- [ ] Keep UI translatable.

---

# Phase 27 — Language selection

- [ ] Show available locales.
- [ ] Show friendly language names.
- [ ] Show spelling availability.
- [ ] Show thesaurus availability.
- [ ] Support regional variants.
- [ ] Remember default language.
- [ ] Allow per-document language.
- [ ] Store settings using `QSettings` in the Qt layer.

---

# Phase 28 — Automatic language detection

Inspired by Sonnet, but implemented independently in Python.

This is not required for the first stable release.

- [ ] Design language detector interface.
- [ ] Do not tightly couple detection to spell checking.
- [ ] Evaluate lightweight Python solutions.
- [ ] Allow applications to disable automatic detection.
- [ ] Support manual language override.
- [ ] Test mixed-language documents.
- [ ] Avoid changing language aggressively while users type.

---

# Phase 29 — Dictionary Manager

Create reusable UI for dictionaries.

- [ ] List detected languages.
- [ ] Show locale.
- [ ] Show dictionary source.
- [ ] Show spelling status.
- [ ] Show thesaurus status.
- [ ] Show file paths in an advanced/details view.
- [ ] Allow manual dictionary import.
- [ ] Allow removal of app-managed dictionaries.
- [ ] Never remove Linux system dictionaries.
- [ ] Prepare optional future download integration.
- [ ] Prepare integration with `libreoffice-dictionaries-collection`.

---

# Phase 30 — Error handling

- [ ] Never crash the host application because one dictionary is malformed.
- [ ] Return clear structured errors.
- [ ] Log backend failures.
- [ ] Detect missing files.
- [ ] Detect encoding errors.
- [ ] Detect malformed Hunspell dictionaries.
- [ ] Detect malformed MyThes files.
- [ ] Disable only the failing language/backend where possible.
- [ ] Keep other languages available.

---

# Phase 31 — Tests

## Unit tests

- [ ] Tokenizer.
- [ ] Registry.
- [ ] Providers.
- [ ] Personal dictionary.
- [ ] Ignore-word management.
- [ ] Spylls backend.
- [ ] PyThes backend.
- [ ] LinguisticService.
- [ ] Caching.
- [ ] Encoding handling.

## Qt tests

- [ ] QTextEdit integration.
- [ ] QPlainTextEdit integration.
- [ ] QSyntaxHighlighter.
- [ ] Context menu.
- [ ] Thesaurus dialog.
- [ ] Language changes.
- [ ] Cleanup/decorator removal.

---

# Phase 32 — Language test matrix

Start with:

- [ ] English.
- [ ] Spanish.
- [ ] French.
- [ ] German.
- [ ] Italian.
- [ ] Portuguese.
- [ ] Dutch.

Then extend to:

- [ ] Polish.
- [ ] Russian.
- [ ] Ukrainian.
- [ ] Greek.
- [ ] Turkish.
- [ ] Other available LibreOffice languages.

---

# Phase 33 — Platform test matrix

## Linux

- [ ] Debian.
- [ ] Ubuntu.
- [ ] MX Linux.
- [ ] System Hunspell dictionaries.
- [ ] System MyThes dictionaries.
- [ ] User dictionaries.

## Windows

- [ ] Windows 10.
- [ ] Windows 11.
- [ ] Virtual environment.
- [ ] App-managed dictionaries.
- [ ] Packaged executable.

## macOS

- [ ] Intel macOS where available.
- [ ] Apple Silicon where available.
- [ ] Virtual environment.
- [ ] App-managed dictionaries.
- [ ] Packaged application.

---

# Phase 34 — GitHub Actions

- [ ] Linux CI.
- [ ] Windows CI.
- [ ] macOS CI.
- [ ] Multiple supported Python versions.
- [ ] Run `pytest`.
- [ ] Run typing checks.
- [ ] Test Spylls loading.
- [ ] Test PyThes loading.
- [ ] Test Unicode.
- [ ] Test representative legacy encodings.
- [ ] Run Qt tests headlessly where possible.
- [ ] Prevent stable releases when critical tests fail.

---

# Phase 35 — Examples

Create standalone examples that do not depend on GuitarChordStudio.

- [ ] `basic_qtextedit.py`.
- [ ] `basic_qplaintextedit.py`.
- [ ] `spellcheck_demo.py`.
- [ ] `thesaurus_demo.py`.
- [ ] `dictionary_manager_demo.py`.
- [ ] `full_demo.py`.

The full demo should prove that another PyQt6 application can integrate the toolkit with minimal code.

---

# Phase 36 — Public API

Target a clean public API such as:

```python
from pyqt6_linguistic_tools import LinguisticService
from pyqt6_linguistic_tools.qt import LinguisticTextEditDecorator

service = LinguisticService(language="es_ES")

decorator = LinguisticTextEditDecorator(
    editor,
    service
)
```

- [ ] Define public modules.
- [ ] Hide implementation details.
- [ ] Document stable APIs.
- [ ] Use semantic versioning.
- [ ] Add deprecation policy.
- [ ] Avoid breaking applications unnecessarily.

---

# Phase 37 — Documentation

- [ ] Architecture overview.
- [ ] Installation.
- [ ] Submodule installation.
- [ ] Recursive cloning.
- [ ] Spylls backend.
- [ ] PyThes backend.
- [ ] Dictionary formats.
- [ ] Encoding behavior.
- [ ] Linux dictionary discovery.
- [ ] Windows dictionary handling.
- [ ] macOS dictionary handling.
- [ ] QTextEdit integration.
- [ ] QPlainTextEdit integration.
- [ ] Context-menu customization.
- [ ] Thesaurus usage.
- [ ] Personal dictionary.
- [ ] Host-application integration.

---

# Phase 38 — Integration into GuitarChordStudio

Only integrate after the standalone library is functional.

- [ ] Initialize the nested submodules recursively.
- [ ] Import `pyqt6-linguistic-tools`.
- [ ] Keep GuitarChordStudio-specific code outside the library.
- [ ] Remove duplicated linguistic logic from GuitarChordStudio where appropriate.
- [ ] Integrate spell checking.
- [ ] Integrate suggestions.
- [ ] Integrate personal dictionary.
- [ ] Integrate ignore-word actions.
- [ ] Integrate synonyms.
- [ ] Integrate thesaurus dialog.
- [ ] Integrate language settings.
- [ ] Test Linux.
- [ ] Test Windows.
- [ ] Test macOS.
- [ ] Verify no regressions in existing GuitarChordStudio features.

---

# Phase 39 — Reuse in another PyQt6 application

This is a mandatory milestone before version `1.0.0`.

- [ ] Integrate the library into at least one second PyQt6 program.
- [ ] Confirm that no GuitarChordStudio imports exist.
- [ ] Confirm application-specific settings stay isolated.
- [ ] Confirm the library works as a Git submodule.
- [ ] Confirm nested Spylls and PyThes submodules initialize correctly.
- [ ] Document the reuse procedure.

---

# Phase 40 — First stable release

Target:

```text
1.0.0
```

Requirements:

- [ ] Spell checking works on Linux.
- [ ] Spell checking works on Windows.
- [ ] Spell checking works on macOS.
- [ ] Suggestions work.
- [ ] MyThes thesaurus works.
- [ ] Personal dictionaries work.
- [ ] Ignore-word support works.
- [ ] QTextEdit integration works.
- [ ] QPlainTextEdit integration works.
- [ ] Context menu works.
- [ ] Thesaurus dialog works.
- [ ] Unicode handling is robust.
- [ ] Legacy dictionary encodings are supported.
- [ ] Automated tests pass.
- [ ] Documentation is complete.
- [ ] Standalone demo works.
- [ ] GuitarChordStudio integration works.
- [ ] At least one additional PyQt6 application uses the library successfully.
- [ ] Publish release `1.0.0`.

---

# Architectural principles that must not be violated

- [ ] Keep linguistic engines separate from Qt widgets.
- [ ] Keep dictionary discovery separate from dictionary parsing.
- [ ] Keep platform differences inside providers.
- [ ] Do not place Windows/Linux/macOS conditionals throughout editor code.
- [ ] Do not require native Hunspell DLL/SO/dylib for the initial architecture.
- [ ] Do not require Sonnet.
- [ ] Do not require KDE Frameworks.
- [ ] Do not convert all dictionaries to UTF-8 unnecessarily.
- [ ] Do not subclass QTextEdit merely to obtain spell checking when a decorator/integration layer can be used.
- [ ] Do not tightly couple applications to Spylls.
- [ ] Do not tightly couple applications to PyThes.
- [ ] Keep backends replaceable.
- [ ] Keep the public API small.
- [ ] Preserve Unicode internally.
- [ ] Fail gracefully when a dictionary is unavailable or malformed.

---

# Final target architecture

```text
Host PyQt6 application
          │
          ▼
pyqt6-linguistic-tools
          │
          ├──────────── Qt Integration ────────────┐
          │                                         │
          │     LinguisticTextEditDecorator         │
          │     SpellCheckHighlighter               │
          │     ContextMenuIntegration              │
          │     ThesaurusDialog                     │
          │                                         │
          └──────────────────┬──────────────────────┘
                             │
                             ▼
                    LinguisticService
                             │
                ┌────────────┴─────────────┐
                │                          │
                ▼                          ▼
        SpellCheckerBackend        ThesaurusBackend
                │                          │
                ▼                          ▼
          SpyllsBackend              PyThesBackend
                │                          │
                ▼                          ▼
            .aff/.dic                  .dat/.idx
                │                          │
                └────────────┬─────────────┘
                             ▼
                    DictionaryRegistry
                             │
              ┌──────────────┼──────────────┐
              ▼              ▼              ▼
         Linux system    Managed files   User files
          dictionaries   Windows/macOS   dictionaries
```

`third-party/sonnet` remains outside this runtime architecture and exists only to help the Agent study proven architectural ideas from a mature Qt spell-checking framework.