# PyQt6 Linguistic Tools Development Handoff

This document is the continuation point for an agent working from the
GuitarChordStudio checkout. Read it together with the top-level
`ROADMAP—PyQt6_Linguistic_Tools.md`. The roadmap defines the complete product;
this document distinguishes the next actionable work from items that need
external systems or have deliberately been deferred.

## Current checkpoint

The working architecture is a standalone toolkit submodule at
`libs/pyqt6-linguistic-tools`, with maintained Spylls and PyThes forks nested
inside it. The implemented toolkit currently includes:

- portable, lazy Spylls and PyThes backends behind engine-neutral contracts;
- cross-platform dictionary providers and read-only Linux system discovery;
- validation, registry, managed/user storage, personal dictionaries, backups,
  and session/document ignored-word scopes;
- a Unicode/UTF-16-aware tokenizer and generic host token filter;
- a fault-isolating `LinguisticService` with bounded backend/result caches;
- optional PyQt6 decorators for `QTextEdit` and `QPlainTextEdit`, highlighting,
  asynchronous checking, context actions, language selection, thesaurus UI,
  and the Dictionary Download Manager;
- deterministic, Qt, platform, curated-corpus, and full-corpus test layers;
- manually dispatched GitHub Actions for fast cross-platform tests, static
  typing, Linux installed dictionary smoke tests, and corpus tests.

Phase 34's static typing objective is complete. Mypy checks all core and Qt
source files against Python 3.10. At the checkpoint used to create this
handoff, the deterministic suite had 255 passing tests, the Linux platform
suite had 2 passing tests, the curated corpus suite had 34 passing tests, and
mypy reported no issues in 31 source files. Treat these counts as a historical
baseline rather than assertions that must never change.

## Latest completed objective — Dictionary Download Manager and host integration

- `DictionaryDownloadManagerWidget` and `DictionaryDownloadManagerDialog`
  provide search, state/component filters, spelling/thesaurus badges, installed
  and available groups, a details panel, progress, and automatic verified
  downloads in a worker thread. The base `DictionaryManagerWidget`/`Dialog`
  retain the host-delegated `download_requested` mode.
- `download_dictionary()` streams HTTPS assets, checks catalog size and
  SHA-256, rejects unsafe archive paths and links, deep validates every
  component, skips malformed regional variants, and atomically publishes into
  `ManagedDictionaryProvider`. `install_dictionary_archive()` handles assets a
  host already downloaded.
- The bundled 57-entry catalog was regenerated with SHA-256 checksums and
  `spelling`/`thesaurus` flags. `tools/fetch-dict-list.py` accepts
  `--dicts-dir` to derive the flags from the local LibreOffice collection.
- ChordFlow and ChordPages now open the shared Dictionary Download Manager,
  install into the `guitarchordstudio` managed namespace, refresh their
  service, and attach the toolkit decorator to every editor. ChordPages has a
  new Edit-menu action and uses a process-wide toolkit service.
- The toolkit ships Spanish and English `.ts` sources and `.qm` catalogs via
  `install_toolkit_translations()`. The manager, thesaurus dialog and context
  menu are covered. See
  `libs/pyqt6-linguistic-tools/docs/translations.md`.
- Current toolkit fast suite: 313 passed, 12 skipped, 50 deselected; mypy clean
  in 36 source files. ChordPages is at 200 tests and ChordFlow at 171. The main
  screenshot is `libs/pyqt6-linguistic-tools/images/01-pyqt6-linguistic-tools.png`.
- The dialog is now a normal modeless window with minimize/maximize/close,
  corner resizing, a screen-aware initial size and remembered geometry in
  `QSettings`. ChordFlow and ChordPages keep a reference and raise an existing
  window instead of opening duplicates.
- ChordPages now exposes **Tools → Synonyms...** for the selected page word,
  using the same shared `LinguisticService` and `ThesaurusDialog` as ChordFlow.
  Its editor spellcheck also runs through the toolkit decorator. When a MyThes
  data set has no part-of-speech metadata (the Spanish LibreOffice thesaurus
  uses `-`), the dialog hides the empty category column, keeps meanings as bold
  groups with indented synonyms, and shows a short note.
- The thesaurus dialog now copies HTML/RTF with bold meaning headings and
  synonym bullets for LibreOffice, plus Markdown (`**bold**` groups and `-`
  bullets) for Markdown editors.
- Removed the oversized **Language** submenu from the editor context menu in
  both ChordFlow and ChordPages. Language selection remains available from the
  application's main menu and preferences.
- Fixed ChordPages' page editor spelling highlighter: its first page now gets a
  fresh QTextDocument after layout, document signals are no longer blocked
  during pagination, unchanged page text is not reassigned, and chord tokens
  are filtered. This makes Hunspell system dictionaries visibly underline
  misspellings and preserves the underline after typing.
- ChordPages now uses the toolkit as its only spell-checking path. Its legacy
  `chordflow.spellcheck` fallback was removed, language-menu entries report the
  dictionary source (`system`, `corpus`, `managed`, `user`), and the system-only
  factory test verifies Linux Hunspell/MyThes discovery without a corpus.
- Fixed ChordFlow's thesaurus replacement: the shared dialog emits
  `replacement_requested(source, replacement)`, but ChordFlow connected that
  two-argument signal directly to a one-argument slot and therefore applied the
  source word. It now unpacks the signal and passes the replacement.
- The thesaurus dialog now defaults to a compact 540×480, has
  minimize/maximize and resize controls, and remembers its position and size
  through `QSettings`.
- The thesaurus window now matches the LibreOffice layout: editable current
  word, installed-thesaurus language selector with native names, numbered
  alternatives, an editable **Replace with** field, and Replace/Cancel.
- `create_service()` is now the reusable toolkit factory; ChordFlow and
  ChordPages both call it instead of assembling providers themselves.
  ChordPages no longer imports ChordFlow's service factory.
- `ThesaurusWidget` is the embeddable browser and `ThesaurusDialog` is its thin
  window wrapper. A new `examples/thesaurus_demo.py` shows both, and
  `pyqt6_linguistic_tools_bootstrap.py` supports a `libs/` git submodule
  workflow without pip.
- Still external: manual Windows/macOS runtime verification and additional
  languages beyond Spanish/English. ChordFlow keeps its legacy dialog only as a
  fallback when the toolkit cannot be imported.

Before editing, verify the live state instead of trusting recorded commit IDs:

```bash
git status --short
git submodule status --recursive
git -C libs/pyqt6-linguistic-tools status --short
git -C libs/pyqt6-linguistic-tools branch --show-current
```

The expected normal branches are `main` for GuitarChordStudio and the toolkit,
and `master` for the Spylls and PyThes forks. A clean nested engine generally
does not need to be touched for toolkit-layer work.

## Completed objective: Phase 40 — First stable release

The toolkit has been released as version 1.0.0:

- `__version__` updated to `1.0.0` in `__init__.py` and `pyproject.toml`.
- `CHANGELOG.md` updated with the 1.0.0 release notes.
- All 19 architectural principles verified by code audit:
  - No Qt imports in core (guarded lazy imports only)
  - No GuitarChordStudio paths in toolkit
  - No Spylls/PyThes leaked to application API
  - No platform conditionals in editor code
  - No native engine dependencies
  - No hard-coded user paths
- Phase 40 requirements: 21 of 22 items verified on Linux (Windows/macOS
  verification requires those platforms).
- 276 fast tests pass, mypy clean, whitespace clean.

## Completed objective: Phase 38 — Linux integration verification

The GuitarChordStudio integration acceptance criteria that can be checked
locally are now verified on Linux:

- `chordflow/tests/test_integration_acceptance.py` runs the roadmap's realistic
  lyrics-and-chords document through the toolkit tokenizer with the
  GuitarChordStudio token filter and a pinned LibreOffice `es_ES` dictionary
  read by Spylls. Only the lyric words survive the filter, all of them are
  accepted by the dictionary, `marabillas` is rejected, and `maravillas` is
  offered as a suggestion. The test skips with a concrete message when no
  dictionary is configured instead of pretending to pass.
- The filter reuses one shared chord grammar
  (`chordflow/chord_transposer.py`: `CHORD_SYMBOL_PATTERN`, `is_chord_symbol`)
  instead of keeping a second chord regular expression, and it reads the source
  chunk through the token offsets. That excludes the `m` fragment the tokenizer
  splits out of `A#m`/`C#m7`, which previously leaked to Spylls.
- Section labels (`INTRO`, `VERSE`, ...) and repeat counts (`X3`) are excluded.
  A lowercase or mixed-case marker is only ignored when its whole line contains
  just markers, repeats and chords, so lyrics such as `Solo tú` keep their
  words.
- Reported ChordPages GUI defects fixed: the window title is now `ChordPages`
  (`WINDOW_TITLE_NAME`) instead of `ChordFlow Guitar`, and the spell-check
  context menu no longer replaces the user's selection with the word under the
  pointer, so Copy and Cut act on the selected text again. Regression tests
  live in `chordflow/tests/test_spellcheck_context_menu.py`.
- ChordPages toolbar: ten SVG icons in `chordpages/assets/toolbar/` cover new,
  open, save, save as, export PDF, transpose down/up, zoom out/in and fit
  width; Save As now sits next to Save. `chordpages/resources.py` tints the
  `currentColor` SVGs for the light and dark palettes, and every action gets
  its text as a hover tooltip. Covered by `chordpages/tests/test_toolbar.py`.
- ChordFlow now installs its own icon from `chordflow/assets/chordflow.svg`
  through `chordflow/resources.py` and `build_application`, so the application
  and the main window share it. ChordPages points at its own
  `chordpages/assets/chordpages.svg` after the ChordFlow icon moved out of
  `chordpages/assets/`. ChordFlow's icon uses a warm amber/orange/red palette,
  the complement of ChordPages' blue/teal, so both launchers are easy to tell
  apart. Covered by `chordflow/tests/test_resources.py`.
- The toolkit no longer vendors the Hunspell, MyThes or Sonnet study sources.
  The three `third-party/` submodules were removed from `.gitmodules`, from the
  index, and from the cached git module directories; only the Spylls and PyThes
  engine submodules remain. The design lessons are recorded in
  `libs/pyqt6-linguistic-tools/docs/hunspell-sonnet-mythes-study.md`. Do not
  add those sources back as submodules.
- The 57-entry dictionary catalog now lives in the toolkit as package data at
  `libs/pyqt6-linguistic-tools/src/pyqt6_linguistic_tools/data/dictionaries.json`
  and is loaded with `load_bundled_dictionary_catalog()`. Its generator moved
  to `libs/pyqt6-linguistic-tools/tools/fetch-dict-list.py`; the top-level
  `dictionaries.json` and `tools/fetch-dict-list.py` were removed.
- Validation at this checkpoint: ChordFlow suite 171 passed; ChordPages suite
  200 passed; toolkit fast suite 313 passed, 12 skipped, 50 deselected; toolkit
  `mypy` clean in 36 source files. The ChordPages suite no longer depends on
  the host locale: `chordpages/tests/conftest.py` installs the
  source-language UI before each test, so a Spanish desktop no longer fails
  the English menu assertions.

Windows and macOS integration tests, and a manual GUI regression pass, remain
unchecked in the roadmap because they need those platforms or a human review.
`chordflow/spellcheck.py` still carries the legacy native-Hunspell fallback
used only when the toolkit cannot be imported; removing that duplicate is a
candidate objective, not completed work.

## Next objective: Phase 41 — Optional native Linux backends (post-1.0)

This is optional post-1.0 work. The maintainer should decide whether to
proceed based on measured performance, memory, or compatibility problems
that a native backend could solve. See the roadmap for the go/no-go gate.

No mandatory Phase 40 item is actionable from this checkout anymore: the
remaining unchecked boxes need Windows/macOS hardware or a manual GUI review.
Do not check them off from Linux evidence.

## Deliberately deferred or externally gated work

- Phase 28 automatic language detection is optional and not required for
  1.0. Do not let it interrupt the compatibility-report/release path.
- Unchecked Windows 10/11 and macOS hardware/package tests require those
  environments. Preserve explicit skips; never mark them complete based only
  on Linux or on reading CI configuration.
- Branch protection and stable-release blocking require GitHub repository
  policy and a future release workflow. Workflow failures alone are not proof
  that releases are protected.
- All GitHub Actions are intentionally manual-only to control minutes,
  notifications, and artifact storage. Do not restore push, pull-request, tag,
  or scheduled triggers. Any future release must also require an explicit
  manual dispatch by the repository user.
- Phase 35 standalone examples follow the compatibility report unless the
  maintainer explicitly reprioritizes them.
- Phase 41 native Hunspell/MyThes backends is optional post-1.0 work. The
  maintainer explicitly chose to continue with portable Spylls/PyThes; do not
  restart native backend development.

## Files to understand first

- `ROADMAP—PyQt6_Linguistic_Tools.md`: scope, ordering, and acceptance criteria.
- `libs/pyqt6-linguistic-tools/README.md`: supported installation and source-use
  modes.
- `libs/pyqt6-linguistic-tools/CONTRIBUTING.md`: engine-fork and contribution
  policy.
- `libs/pyqt6-linguistic-tools/src/pyqt6_linguistic_tools/service.py`:
  application-facing linguistic facade.
- `libs/pyqt6-linguistic-tools/src/pyqt6_linguistic_tools/qt/decorator.py`:
  widget-independent Qt editor integration.
- `libs/pyqt6-linguistic-tools/docs/linguistics-architecture.md`: architecture
  overview, module map, and data-flow diagrams.
- `libs/pyqt6-linguistic-tools/docs/hunspell-sonnet-mythes-study.md`: why the
  three reference sources were studied and where their lessons landed.
- `libs/pyqt6-linguistic-tools/docs/`: existing documentation (linguistic
  service, backend API, registry, Qt architecture, testing, etc.).

## Repository and commit discipline

Do not commit from the top level first. For integration or token-filter
work, commit and push the toolkit, then record its new pointer plus roadmap
and handoff updates in GuitarChordStudio:

```bash
cd libs/pyqt6-linguistic-tools
git add .
git diff --cached
git commit -m "feat(integration): add chord token filter and integration test"
git push

cd ../..
git add .
git diff --cached
git commit -m "docs(roadmap): record GuitarChordStudio integration"
git push
```

If a verified engine defect requires Spylls or PyThes changes, add the
regression test and commit that deepest fork first. Then update the toolkit
pointer, and finally the GuitarChordStudio pointer. Never force-reset a dirty
submodule or include unrelated user work.
