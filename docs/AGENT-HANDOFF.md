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

## Next objective: Phase 41 — Optional native Linux backends (post-1.0)

This is optional post-1.0 work. The maintainer should decide whether to
proceed based on measured performance, memory, or compatibility problems
that a native backend could solve. See the roadmap for the go/no-go gate.

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
