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

There will be **one repository and one public API** for every supported
platform:

```text
pyqt6-linguistic-tools
```

Do not create separate `pyqt6-linguistic-tools-Linux` and
`pyqt6-linguistic-tools-win` repositories. Platform differences belong in
replaceable providers and backends, not in copies of the Qt integration or
application-facing API.

The first portable implementation will use:

- **Spylls** for Hunspell-compatible spelling on Linux, Windows and macOS.
- **PyThes** for MyThes-compatible thesaurus lookup on Linux, Windows and
  macOS.
- System dictionary discovery on Linux, while still reading those dictionaries
  through the same portable backends.
- Managed/user dictionaries on Windows and macOS.

Native Hunspell and MyThes engines may be added later as optional performance
backends. They must never be required by the public API or by ChordFlow,
ChordPages, or another host application.

Current intended architecture:

```text
GuitarChordStudio
        │
        └── libs/
            └── pyqt6-linguistic-tools
                     │
                     ├── libs/
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
libs/pyqt6-linguistic-tools/third-party/sonnet
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

# IMPORTANT ARCHITECTURAL REFERENCE: HUNSPELL

The developer has intentionally placed as sub-module the **hunspell** source code at:

```text
libs/pyqt6-linguistic-tools/third-party/hunspell
```

Use Hunspell as the behavioral and dictionary-format reference when reinforcing
Spylls, which is a Python port of Hunspell concepts. Native Hunspell remains a
test oracle and a possible optional backend; it is not a runtime requirement for
the first portable release.

---

# IMPORTANT BEHAVIORAL REFERENCE: MYTHES

The developer has intentionally placed the original **MyThes** source code as
a submodule at:

```text
libs/pyqt6-linguistic-tools/third-party/mythes
```

MyThes is the native C++ implementation on which PyThes is based. Use this
source as the authoritative behavioral and file-format reference whenever the
maintained PyThes fork needs reinforcement, especially for:

- `.dat` parsing and meaning records.
- `.idx` generation, declared entry counts and byte offsets.
- Character-encoding behavior.
- Lookup edge cases and malformed-file handling.
- Compatibility tests that require comparison with the original engine.

PyThes remains the required portable thesaurus engine for the first release.
The MyThes submodule is a development reference and possible test oracle; it
must not become an implicit runtime dependency.

## Critical restriction

- [ ] DO NOT require MyThes to run PyThes or the toolkit.
- [ ] DO NOT compile or bundle MyThes in the first portable implementation.
- [ ] DO NOT expose native MyThes types through the public Python API.
- [ ] DO NOT copy C++ implementation code directly into Python.
- [ ] DO compare focused PyThes behavior with MyThes when resolving a verified
  compatibility defect.
- [ ] Keep any future native integration behind the optional
  `NativeMyThesBackend` interface.

---

# MANDATORY PRELIMINARY STAGE — Stabilize Spylls and PyThes

This stage comes before development of the toolkit itself because every higher
layer depends on these two portable engines. The currently selected upstream
projects have shown little or no recent development activity for approximately
two years. Therefore, the project must not assume that upstream will implement
missing behavior or fix compatibility problems on our schedule.

Only the minimum repository and pytest scaffolding from Phase 0 may be created
first when needed to execute this gate. Feature development above the engine
layer remains blocked until the exit criteria below are satisfied.

The copies under `libs/spylls` and `libs/pythes` are maintained forks. Their
improvement is part of this project, not an incidental task.

Before changing either fork:

- [x] Record the exact upstream repository, commit and license.
- [x] Create a branch/release policy for the maintained fork.
- [ ] Commit engine fixes and tests in each fork repository, then update the
  pinned submodule commit in `pyqt6-linguistic-tools`.
- [x] Define how future upstream changes will be reviewed and merged without
  losing local regression fixes.
- [x] Run the existing upstream tests unchanged and record the baseline.
- [x] Add a changelog containing every deviation from upstream.
- [ ] Add a regression test before fixing each discovered defect.
- [ ] Keep fixes focused so they can be proposed upstream when appropriate.
- [ ] Never hide an incompatibility by silently changing a source dictionary.

## Spylls stabilization gate

Spylls is the required initial spelling backend on all three platforms. It is a
port of Hunspell behavior, but it is not assumed to be fully equivalent to
native Hunspell.

- [ ] Review the complete Spylls fork.
- [x] Inventory parsed, implemented, partially implemented and ignored Hunspell
  directives.
- [x] Understand `.aff` parsing, `.dic` parsing, `lookup()` and `suggest()`.
- [ ] Verify Hunspell `SET` handling and Python codec-name normalization.
- [x] Test UTF-8, ISO-8859-1, ISO-8859-2, ISO-8859-7, ISO-8859-13,
  ISO-8859-15 and every other encoding found in the corpus.
- [ ] Test accented Spanish words, `ñ`, combining Unicode characters and
  scripts outside Western European alphabets.
- [ ] Compare representative results with native Hunspell using the same
  `.aff/.dic` files.
- [x] Cover compound rules, affix flags, forbidden words, capitalization,
  replacement tables, input conversion and output conversion.
- [ ] Audit incomplete behaviors documented by Spylls, including rare Hunspell
  directives and language-specific branches.
- [x] Benchmark dictionary loading, `lookup()` and `suggest()`.
- [x] Measure peak memory for small, medium and very large dictionaries.
- [ ] Never add arbitrary limits such as rejecting suggestions above 12
  characters.
- [x] Load dictionaries lazily and define a bounded cache policy.
- [ ] Add tests before changing Spylls behavior.
- [x] Document every deviation from upstream Spylls.
- [ ] Do not declare this gate complete merely because a dictionary loads; its
  representative morphology and suggestions must also pass.

## PyThes stabilization gate

PyThes is the required initial thesaurus backend on all three platforms. Its
handling of encodings and `.idx` byte offsets must be validated before building
the thesaurus UI.

- [x] Review the complete PyThes fork.
- [x] Understand `.dat` parsing, `.idx` parsing and lookup behavior.
- [x] Verify that `.idx` offsets are treated as byte offsets and remain correct
  for UTF-8 and legacy encodings.
- [x] Test UTF-8, ISO-8859-* and every other encoding found in the corpus.
- [x] Handle BOMs, CRLF/LF differences and encoding aliases safely.
- [x] Detect missing, truncated, malformed and stale indexes.
- [x] Validate index entry counts and verify that indexed words match `.dat`
  entries.
- [x] Regenerate an index from `.dat` when explicitly requested.
- [x] Allow a safe fallback without a usable `.idx`.
- [x] Preserve meanings, parts of speech, alternate senses and phrases.
- [x] Add Unicode normalization and bounded caching.
- [x] Modernize paths, typing, exceptions and structured result types.
- [x] Add tests before changing PyThes behavior.
- [x] Document every deviation from upstream PyThes.

## LibreOffice dictionary compatibility corpus

Use the collection currently available in GuitarChordStudio at:

```text
third-party/libreoffice-dictionaries-collection/dicts/
```

The standalone library must not hard-code that GuitarChordStudio-specific path.
Tests must accept the corpus root through a pytest option or an environment
variable such as:

```text
LIBREOFFICE_DICTIONARIES_PATH
```

CI for the standalone repository may check out the dictionary collection in a
known test-data location.

Create these test levels under `tests/`:

### Fast suite — every commit

- [ ] Keep small, license-compatible fixtures covering each important encoding
  and Hunspell/MyThes feature.
- [ ] Run parser, lookup, suggestion and byte-offset regression tests.
- [ ] Keep execution time suitable for local development and pull requests.
- [ ] Convert every corpus failure into the smallest useful regression fixture,
  while preserving its required license and attribution.

### Curated integration suite — every pull request

- [x] Load a representative matrix of real LibreOffice dictionaries.
- [x] Include small, medium and large dictionaries.
- [ ] Include regional variants and spelling-only/thesaurus-only languages.
- [ ] Check representative correct words, incorrect words and suggestions.
- [ ] Check representative thesaurus entries and index offsets.

### Full corpus suite — scheduled/manual

- [ ] Discover every `.aff/.dic` and `.dat/.idx` pair in the collection.
- [ ] Validate every dictionary without converting its original encoding.
- [ ] Record load time, peak memory, warnings, failures and backend version.
- [ ] Produce a machine-readable compatibility report by locale.
- [ ] Compare results against the previous baseline to detect regressions.
- [ ] Run outside the fast unit-test job because the full collection is large.

Dictionary licenses vary. Tests and packaged releases must preserve attribution
and must not assume that every file in the collection has identical
redistribution terms.

### Current corpus audit baseline — 2026-08-20

The encoding-agnostic Spylls audit tool scanned all 88 LibreOffice `.aff`
files currently available to GuitarChordStudio. It now finds 49 supported raw
directive names, 7 with partial behavior, 8 metadata or non-spelling
extensions, and one probable source typo (`SFT` inside a Mongolian `SFX`
block). No dictionary was rewritten. Historical aliases `COMPOUNDFIRST` and
`ONLYROOT`, present alongside their modern Hungarian equivalents, now have
focused regression tests. `FULLSTRIP` is now enforced for prefix and suffix
lookup, with tests covering enabled, disabled, and partial-strip behavior; all
nine real dictionaries that declare it load successfully. The more frequent
`WORDCHARS` belongs to the future shared tokenizer.

`CHECKCOMPOUNDPATTERN` replacement and special `0` boundary behavior are now
implemented, including `ONLYINCOMPOUND` linking-affix placement. The lookup
baseline is 105 passing, 2 explicitly pending, and 0 failing out of 107
scenarios.

A subprocess-isolated performance matrix now covers small, medium and
very-large Spylls and PyThes data sets. It records load time, Python allocation
peak, process RSS where available, hit/miss lookup latency, suggestion latency,
and cached thesaurus latency in machine-readable JSON. The 2026-08-20 baseline
and diagnostic budgets are documented in
`libs/pyqt6-linguistic-tools/docs/performance-budgets.md`. The measurements
require lazy background loading: `es_EC` used about 111 MiB RSS and 4.26 s to
load under instrumentation, while the 583,521-entry Mongolian dictionary used
about 1.0 GiB and 43.8 s.

## Exit criteria for the preliminary stage

- [ ] The fast and curated suites pass on Linux, Windows and macOS.
- [ ] Known incompatibilities have explicit expected-failure tests and tracked
  issues; they are not silent.
- [ ] Spylls and PyThes expose stable primitives needed by their toolkit
  backends.
- [x] Performance budgets are documented for dictionary loading, memory,
  lookup, suggestion and thesaurus lookup.
- [ ] The compatibility report identifies which LibreOffice dictionaries are
  ready, limited or unsupported.

---

# Phase 0 — Repository foundation

- [x] Review the current repository structure.
- [x] Create a clean Python package structure.
- [x] Create `pyproject.toml`.
- [x] Define minimum supported Python version.
- [ ] Define minimum supported PyQt6 version.
- [x] Create `README.md`.
- [x] Create `CHANGELOG.md`.
- [x] Create `CONTRIBUTING.md`.
- [x] Keep this `ROADMAP—PyQt6_Linguistic_Tools.md` updated.
- [x] Add `.gitignore`.
- [ ] Add typing configuration.
- [x] Add `pytest`.
- [ ] Add basic logging infrastructure.
- [x] Define semantic versioning.
- [x] Start development version as `0.1.0-dev`.

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
│   ├── sonnet/
│   ├── hunspell/
│   └── mythes/
│
├── src/
│   └── pyqt6_linguistic_tools/
│
├── tests/
├── examples/
├── pyproject.toml
└── ROADMAP.md
```

- [x] Keep `third-party/sonnet` only as architectural reference.
- [x] Keep `third-party/hunspell` only as reference for the `spylls` hunspell fork, In case it is necessary to reinforce the source code.
- [x] Keep `third-party/mythes` only as the behavioral and file-format
  reference for the maintained `pythes` fork unless the optional native phase
  is explicitly activated later.
- [x] Ensure applications using this repository do not need to add Spylls and PyThes separately.

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

# Phase 3 — Integrate the stabilized Spylls fork

The audit, improvement and compatibility work happens in the mandatory
preliminary stage. This phase exposes the stabilized fork through the toolkit
backend interface.

- [x] Implement `SpyllsBackend` without exposing Spylls types publicly.
- [x] Translate fork exceptions into structured toolkit errors.
- [x] Expose backend version, capabilities and active dictionary metadata.
- [x] Keep personal dictionaries and ignore lists outside the immutable source
  dictionary.
- [x] Verify that applications never need to import Spylls directly.
- [x] Reuse the preliminary compatibility tests as backend contract tests.
- [ ] Make Spylls the default spelling backend on Linux, Windows and macOS for
  the first portable release.

---

# Phase 4 — Integrate the stabilized PyThes fork

The audit, improvement and compatibility work happens in the mandatory
preliminary stage. This phase exposes the stabilized fork through the toolkit
backend interface.

- [x] Implement `PyThesBackend` without exposing PyThes types publicly.
- [x] Translate fork exceptions into structured toolkit errors.
- [x] Return stable structured results for meanings, parts of speech and
  synonyms.
- [x] Expose backend version, capabilities and active thesaurus metadata.
- [x] Verify that applications never need to import PyThes directly.
- [x] Reuse the preliminary compatibility tests as backend contract tests.
- [ ] Make PyThes the default thesaurus backend on Linux, Windows and macOS for
  the first portable release.

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

- [x] Create `SpellCheckerBackend`.
- [x] Define `load_dictionary()`.
- [x] Define `check_word()`.
- [x] Define `suggest()`.
- [x] Define `add_word()` where supported.
- [x] Define `remove_word()` where supported.
- [x] Define `available()`.
- [x] Define backend metadata.

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

Create a backend resolver without platform conditionals in host applications:

```text
Configured backend
        ↓
Available and compatible?
        ├── yes → use it
        └── no  → portable SpyllsBackend fallback
```

- [ ] Default to `SpyllsBackend` on Linux, Windows and macOS in the first
  portable release.
- [ ] Allow explicit backend selection for diagnostics and conformance tests.
- [ ] Never silently change a document language when falling back between
  engines.
- [ ] Report the selected backend and fallback reason through structured
  diagnostics.
- [x] Ensure adding a native backend does not change the public service or Qt
  APIs.

---

# Phase 8 — Thesaurus backend interface

Create:

```text
ThesaurusBackend
```

- [x] Define `load_dictionary()`.
- [x] Define `lookup()`.
- [x] Define `synonyms()`.
- [x] Preserve meanings.
- [x] Preserve parts of speech.
- [x] Preserve alternate senses.
- [x] Expose capabilities.
- [x] Implement `PyThesBackend`.

Potential future implementations must remain possible without changing the public API.

- [ ] Default to `PyThesBackend` on Linux, Windows and macOS in the first
  portable release.
- [x] Keep a future `NativeMyThesBackend` optional and behind the same
  `ThesaurusBackend` interface.
- [x] Do not require `libmythes`, a DLL or a dylib for the first portable
  release.

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

A provider returning Linux system files does not imply use of a native engine.
For example, `LinuxSystemDictionaryProvider` may find
`/usr/share/hunspell/es_EC.aff`, and `SpyllsBackend` may read it. Providers and
backends must remain independently selectable.

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
- [ ] Read discovered system dictionaries through Spylls/PyThes by default.
- [ ] Do not require the Hunspell or MyThes shared libraries merely to use
  their installed dictionary files.
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
- [ ] Prepare integration with `libreoffice-dictionaries-collection` through the `/dictionaries.json` file which contains the list to download and decompress all the dictionaries that were packaged from `/third-party/libreoffice-dictionaries-collection`
- [ ] Do not require system-wide Hunspell.
- [ ] Do not require DLL-based Hunspell.
- [ ] Use Spylls and PyThes by default.

---

# Phase 13 — macOS provider

- [ ] Use application/user data directories.
- [ ] Use `QStandardPaths`.
- [ ] Support managed dictionaries.
- [ ] Support manual import.
- [ ] Prepare integration with `libreoffice-dictionaries-collection` through the `/dictionaries.json` file which contains the list to download and decompress all the dictionaries that were packaged from `/third-party/libreoffice-dictionaries-collection`
- [ ] Avoid native binary dependencies whenever possible.
- [ ] Use Spylls and PyThes by default.

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

Do not rely solely on `\b\w+\b`. The tokenizer must correctly preserve tokens
such as:

```text
Señor
creación
Straße
français
Москва
d’Artagnan
O'Connor
```

Evaluate Unicode properties such as `\p{L}` and `\p{M}` if the third-party
`regex` package provides a material correctness benefit. Avoid adding that
dependency if equivalent behavior can be implemented reliably with Python's
Unicode facilities.

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
- [ ] Preserve offsets exactly even when a token contains combining marks or a
  typographic apostrophe.
- [ ] Provide a host-supplied token-filter interface so applications can exclude
  domain-specific tokens without coupling the core library to those domains.
- [ ] Test `123`, `2026`, `x3`, URLs, `www` addresses and email addresses as
  configurable non-word exclusions.

---

# Phase 17 — LinguisticService

Create the main application-facing service.

Target API, example for spanish:

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
- [ ] Keep spelling and thesaurus capabilities independently enableable.
- [ ] Lazy-load thesaurus data only when synonyms are requested.
- [ ] Ensure spell checking continues to work when no thesaurus exists for the
  active locale.

---

# Phase 18 — Caching

- [ ] Cache spelling results by `(locale, word)`.
- [ ] Cache suggestions by `(locale, word)`.
- [ ] Cache thesaurus results by `(locale, word)`.
- [ ] Invalidate caches when dictionaries change.
- [ ] Invalidate relevant entries when personal dictionary changes.
- [ ] Invalidate relevant entries when a personal word is removed.
- [ ] Invalidate language-dependent caches whenever the language changes.
- [ ] Use bounded caches.
- [x] Benchmark memory consumption.

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


- [ ] Do not require subclassing `QTextEdit`.
- [ ] Do not require subclassing `QPlainTextEdit`.
- [ ] Attach behavior to existing editors.
- [ ] Allow removal/disabling of integration.
- [ ] Preserve host application's existing context menu.
- [ ] Preserve host application's signals and behavior.
- [ ] Allow host applications to add custom actions.
- [ ] Allow host applications to register domain-specific token filters.
- [ ] Expose explicit enable/disable methods without requiring editor
  subclassing, for example `integration.set_spellcheck_enabled(False)`.
- [ ] Allow thesaurus integration to be disabled independently.

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
- [ ] Keep the highlighter's responsibility narrow: tokenize, apply configured
  filters, query cached spelling status and underline misspellings.
- [ ] Never download dictionaries, inspect package managers, rescan the whole
  filesystem or rebuild an engine from the highlighter.

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
- [ ] Show spelling suggestions only for misspelled words.
- [ ] Allow synonyms and language selection for correctly spelled words without
  manufacturing a spelling error.
- [ ] Keep every library-owned action string translatable, using English source
  strings.
- [ ] Bound the number of inline suggestions and synonyms so context menus do
  not become enormous; provide a `More synonyms...` dialog when appropriate.

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
- [ ] Replace exactly the word under the cursor when a synonym is selected.
- [ ] Preserve simple capitalization where safe (`word`, `Word`, `WORD`).
- [ ] Do not attempt unsupported morphological transformations that could
  produce an incorrect replacement.

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
- [ ] On language changes, unload the previous portable dictionary when it is
  no longer cached, load the relevant personal dictionary, invalidate spelling
  and suggestion caches, and update thesaurus availability.
- [ ] Test repeated sequences such as
  `es_ES → de_DE → ru_RU → fr_FR → es_ES`.

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
- [ ] Prepare integration with `libreoffice-dictionaries-collection` through the `/dictionaries.json` file which contains the list to download and decompress all the dictionaries that were packaged from `/third-party/libreoffice-dictionaries-collection`

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

The engine-level fast, curated and full-corpus suites are defined in the
mandatory preliminary stage. This phase adds toolkit service and Qt integration
coverage on top of those suites.

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
- [ ] Backend resolver selection and fallback.
- [ ] Portable backend contracts that do not expose concrete Spylls/PyThes
  implementation types.
- [ ] Unicode tokenizer cases: `Señor`, `creación`, `Straße`, `français`,
  `Москва`, `d’Artagnan` and `O'Connor`.
- [ ] Language switching, cache invalidation and personal-dictionary reload.
- [ ] Spell-check-only languages, thesaurus-only languages and missing optional
  resources.
- [ ] Explicit skips with a reason when an optional real dictionary is absent;
  tests must not pretend that a resource exists.
- [ ] PyThes lookup for existing/missing Unicode words, multiple meanings and
  duplicate synonyms.
- [ ] Verify that the Qt/service layer exposes backend suggestions unchanged;
  do not hard-code results that are not guaranteed by the selected dictionary
  version.

## Qt tests

- [ ] QTextEdit integration.
- [ ] QPlainTextEdit integration.
- [ ] QSyntaxHighlighter.
- [ ] Context menu.
- [ ] Thesaurus dialog.
- [ ] Language changes.
- [ ] Cleanup/decorator removal.
- [ ] Enable/disable spelling and thesaurus independently.
- [ ] Exact replacement under the cursor and safe capitalization preservation.
- [ ] Bounded suggestion/synonym menus and translatable actions.

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

Representative acceptance words should include, when the corresponding real
dictionary is available:

```text
Spanish: Canta, Toda, maravillas, creación, Señor
German:  Haus, Straße, schön, Deutschland
Russian: Москва, привет, Россия
French:  français, création, école
```

Use clearly invented misspellings alongside valid words. Expected results must
come from the pinned real dictionary or its recorded compatibility baseline,
not from a second hard-coded word list in the application.

---

# Phase 33 — Platform test matrix

## Linux

- [ ] Debian.
- [ ] Ubuntu.
- [ ] MX Linux.
- [ ] System Hunspell dictionaries.
- [ ] System MyThes dictionaries.
- [ ] User dictionaries.
- [ ] Spylls/PyThes reading system-installed dictionary files.
- [ ] Portable fallback when native shared libraries are absent.

## Windows

- [ ] Windows 10.
- [ ] Windows 11.
- [ ] Virtual environment.
- [ ] App-managed dictionaries.
- [ ] Packaged executable.
- [ ] Spylls/PyThes operation without Hunspell/MyThes DLLs.

## macOS

- [ ] Intel macOS where available.
- [ ] Apple Silicon where available.
- [ ] Virtual environment.
- [ ] App-managed dictionaries.
- [ ] Packaged application.
- [ ] Spylls/PyThes operation without bundled native linguistic libraries.

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
- [ ] Run the fast engine suite on every job.
- [ ] Run the curated LibreOffice corpus suite on pull requests.
- [ ] Run the full corpus suite on a schedule and by manual dispatch.
- [ ] Upload the machine-readable dictionary compatibility report.
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

service = LinguisticService(language="en_US")

decorator = LinguisticTextEditDecorator(
    editor,
    service
)
```

or:

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
- [ ] Create `docs/linguistics-architecture.md`.
- [ ] Installation.
- [ ] Submodule installation.
- [ ] Recursive cloning.
- [ ] Spylls backend.
- [ ] PyThes backend.
- [ ] Portable default backend policy.
- [ ] LibreOffice corpus test configuration.
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
- [ ] Use the same `LinguisticService` and Qt integration in ChordFlow and
  ChordPages.
- [ ] Keep backend and platform selection out of ChordFlow and ChordPages.
- [ ] Keep GuitarChordStudio-specific code outside the library.
- [ ] Remove duplicated linguistic logic from GuitarChordStudio where appropriate.
- [ ] Integrate spell checking.
- [ ] Integrate suggestions.
- [ ] Integrate personal dictionary.
- [ ] Integrate ignore-word actions.
- [ ] Integrate synonyms.
- [ ] Integrate thesaurus dialog.
- [ ] Integrate language settings.
- [ ] Implement a GuitarChordStudio-owned `is_chord_token(token)` filter using
  the existing chord parser/grammar rather than duplicating it with a new
  regular expression inside the linguistic library.
- [ ] Pass that filter through the library's generic host token-filter API.
- [ ] Confirm that chord symbols such as `A`, `Am`, `A#m`, `Bb`, `C#m7`,
  `Fmaj7`, `Gsus4`, `D/F#` and `Cadd9` are never sent to Spylls.
- [ ] Add a GuitarChordStudio integration acceptance test using a realistic
  lyrics-and-chords document:

  ```text
  INTRO X3
  A#m   G#   F#

  VERSE
  C#       G#       A#m      G#    F#
  Mi Cristo, mi Rey, nadie es como tú
  C#       F#       G#
  Toda mi vida, quiero exaltar,
  A#m      B        G#
  las maravillas de tu amor
  ```

- [ ] Verify that chords/non-word markers are ignored while ordinary Spanish
  words are checked according to the active dictionary.
- [ ] Verify that a misspelling such as `marabillas` exposes the suggestions
  returned by the active pinned dictionary, including `maravillas` when that
  dictionary actually provides it.
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
- [ ] Spylls is the tested portable spelling backend on all three platforms.
- [ ] PyThes is the tested portable thesaurus backend on all three platforms.
- [ ] Linux automatically discovers and uses supported system dictionaries.
- [ ] Windows and macOS do not require native Hunspell/MyThes libraries.
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
- [ ] Maintain one repository and one public API for every platform.
- [ ] Use Spylls and PyThes as the initial portable backends on every platform.
- [ ] Do not require native Hunspell DLL/SO/dylib for the initial architecture.
- [ ] Treat native Hunspell/MyThes engines as optional replaceable backends.
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
- [ ] Do not hard-code a GuitarChordStudio path in the standalone library.

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
            ┌──────────────┼──────────────┐
            │              │              │
            ▼              ▼              ▼
   BackendResolver  DictionaryRegistry  Settings/PersonalDictionary
            │              │
      ┌─────┴─────┐        ┌───────┼───────┐
      ▼           ▼        ▼       ▼       ▼
 SpellCheckerBackend  ThesaurusBackend  Linux  Managed  User
      │           │        system   files   files
 ┌───┴───┐   ┌───┴────┐
 ▼       ▼   ▼        ▼
Spylls  Native* PyThes  Native*
 │               │
 ▼               ▼
.aff/.dic         .dat/.idx

* Optional and deferred; portable Spylls/PyThes remain the fallback.
```

`third-party/sonnet` remains outside this runtime architecture and exists only to help the Agent study proven architectural ideas from a mature Qt spell-checking framework.

---

# Phase 41 — OPTIONAL POST-1.0 native Linux backends (last)

This is deliberately the final and optional phase. Do not spend implementation
or investigation effort here until the complete Spylls/PyThes path works to the
quality required by version `1.0.0` in ChordFlow, ChordPages and the independent
reuse example.

Discovering Linux system dictionary **files** earlier in the roadmap does not
activate this phase: Spylls and PyThes can read those files without loading
`libhunspell.so` or `libmythes.so`.

## Go/no-go decision before implementation

- [ ] Confirm that every portable `1.0.0` requirement and test passes first.
- [ ] Measure an actual performance, memory, compatibility or distribution
  problem that a native backend could solve.
- [ ] Estimate implementation, CI, packaging, security, licensing and ongoing
  maintenance cost.
- [ ] Decide explicitly whether the measured benefit justifies that cost.
- [ ] If no material benefit exists, close this phase as `not planned`; native
  integration is not required for project completeness.

## Native work, only after a positive go decision

- [ ] Implement `NativeHunspellBackend` only behind `SpellCheckerBackend`.
- [ ] Prefer distribution-provided Hunspell libraries on Linux; never install
  packages automatically or request root privileges.
- [ ] Implement `NativeMyThesBackend` only behind `ThesaurusBackend` and only if
  separate measurements justify it.
- [ ] Keep native dependencies optional at installation and runtime.
- [ ] Fall back safely to Spylls/PyThes when a native engine cannot load.
- [ ] Run the same backend contracts and LibreOffice dictionary conformance
  tests against portable and native implementations.
- [ ] Add native lifecycle stress tests covering repeated create, check,
  suggest, result release, destruction and language switching.
- [ ] Check for leaks, invalid frees, stale handles and encoding changes.
- [ ] Document behavioral differences instead of pretending portable and
  native engines are identical.
- [ ] Do not change the public service, Qt integration, ChordFlow or ChordPages
  APIs to accommodate a native backend.
- [ ] Do not create Linux- or Windows-specific copies of the core, Qt layer,
  registry, settings, tests or documentation.
- [ ] If native packaging needs a separate distribution, publish a small
  optional plugin such as `pyqt6-linguistic-tools-native-hunspell`, not a fork
  of the complete toolkit.
- [ ] Consider native backends for Windows or macOS only in a later proposal
  supported by separate evidence; they are outside this phase.
