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
  and the Dictionary Manager;
- deterministic, Qt, platform, curated-corpus, and full-corpus test layers;
- manually dispatched GitHub Actions for fast cross-platform tests, static
  typing, Linux installed dictionary smoke tests, and corpus tests.

Phase 34's static typing objective is complete. Mypy checks all core and Qt
source files against Python 3.10. At the checkpoint used to create this
handoff, the deterministic suite had 255 passing tests, the Linux platform
suite had 2 passing tests, the curated corpus suite had 34 passing tests, and
mypy reported no issues in 31 source files. Treat these counts as a historical
baseline rather than assertions that must never change.

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

## Completed objective: documentation (Phase 37)

All documentation items from the roadmap are covered:

- `docs/linguistics-architecture.md` — layer diagram, module map, data-flow
  diagrams, key design decisions, and installation method reference.
- Installation, submodule installation, and recursive cloning — documented
  in the README with `venv` setup instructions for Linux and Windows.
- Backend API (`docs/backend-api.md`) — Spylls/PyThes lifecycle, lazy loading,
  bounded LRU cache, resolver diagnostics.
- Dictionary registry (`docs/dictionary-registry.md`) — discovery, pairing,
  source priority, locale fallback.
- Dictionary validation (`docs/dictionary-validation.md`) — Hunspell/MyThes
  checks, encoding, entry count, representative words, index offsets.
- Testing (`docs/testing.md`) — fast suite, corpus suite, coverage map, pinned
  language acceptance matrix, compatibility report.
- Qt architecture (`docs/qt-architecture.md`) — QTextEdit/QPlainTextEdit
  integration, decorator, highlighter, context menu, thesaurus dialog,
  dictionary manager, async spell checking, settings.
- Personal dictionary (`docs/personal-dictionary.md`) — per-locale UTF-8 JSON
  storage, NFC normalization, atomic writes, cross-process locks.
- Ignored words (`docs/ignored-words.md`) — occurrence, document, session
  scopes, per-locale state.
- Error handling (`docs/error-handling.md`) — component isolation, structured
  diagnostics, logging bridge, strict mode.
- Result caching (`docs/result-caching.md`) — LRU caches, zero-sized mode,
  registry revision invalidation.
- Unicode tokenizer (`docs/unicode-tokenizer.md`) — combining marks, UTF-16
  offsets, configurable technical token exclusions.
- Managed dictionaries (`docs/managed-dictionaries.md`) — offline catalog,
  atomic import, dictionary bundles.
- Personal backups (`docs/personal-backups.md`) — versioned export, preview,
  merge/replace restore, concurrency.
- Engine baseline (`docs/engine-baseline.md`) — verified Hunspell directives,
  lookup/suggestion scenarios, encoding coverage.
- Performance budgets (`docs/performance-budgets.md`) — load time, memory,
  lookup latency by dataset size.
- Public API (`docs/public-api.md`) and deprecation policy
  (`docs/deprecation-policy.md`) — stable surface, deprecation cycle.

## Next objective: GuitarChordStudio integration (Phase 38)

Integrate the toolkit into ChordFlow and ChordPages. Initialize nested
submodules recursively, import `pyqt6-linguistic-tools`, use the same
`LinguisticService` and Qt integration in both applications, keep backend
and platform selection out of the host applications, keep
GuitarChordStudio-specific code outside the library, and remove duplicated
linguistic logic where appropriate.

Run commands from `libs/pyqt6-linguistic-tools`. Use the active virtual
environment if one exists; on this development machine the source checkout is
also configured by pytest's `pythonpath` setting.

```bash
QT_QPA_PLATFORM=offscreen python3 -m pytest -c pyproject.toml -q \
  -m 'not corpus and not platform'
python3 -m mypy
```

Run the examples (requires PyQt6 and a display or offscreen platform):

```bash
QT_QPA_PLATFORM=offscreen python3 examples/basic_qtextedit.py &
sleep 1 && kill %1
```

Validate edited workflow YAML and run `git diff --check` before handoff.

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
- Phase 38 GuitarChordStudio integration begins only after the standalone
  library is ready. ChordFlow and ChordPages must share the same service and Qt
  integration.
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
- `libs/pyqt6-linguistic-tools/docs/`: existing documentation (linguistic
  service, backend API, registry, Qt architecture, testing, etc.).

## Repository and commit discipline

Do not commit from the top level first. For documentation or integration
work, commit and push the toolkit, then record its new pointer plus roadmap
and handoff updates in GuitarChordStudio:

```bash
cd libs/pyqt6-linguistic-tools
git add .
git diff --cached
git commit -m "docs: add architecture overview and cross-references"
git push

cd ../..
git add .
git diff --cached
git commit -m "docs(roadmap): record documentation phase"
git push
```

If a verified engine defect requires Spylls or PyThes changes, add the
regression test and commit that deepest fork first. Then update the toolkit
pointer, and finally the GuitarChordStudio pointer. Never force-reset a dirty
submodule or include unrelated user work.
