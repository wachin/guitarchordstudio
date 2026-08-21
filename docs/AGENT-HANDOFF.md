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

## Completed objective: public API (Phase 36)

The public API surface has been defined and documented:

- `docs/public-api.md` — stable public API surface with all exported names
  grouped by category (core service, Qt integration, models, errors,
  utilities).
- `docs/deprecation-policy.md` — pre-1.0 and post-1.0 deprecation cycle,
  what is not part of the public API, and how to report deprecations.
- `py.typed` — PEP 561 marker for static type checking support.
- `__init__.py` — reorganized `__all__` by category, added module docstring
  with typical usage example.

All existing imports remain backward-compatible. The `__all__` now clearly
separates the public API into categories: core service, registry/providers,
backends, validation, compatibility report, personal dictionary, ignored
words, locales, tokenizer, capabilities, models, errors, catalog, storage,
and version.

## Next objective: documentation (Phase 37)

Create comprehensive documentation including architecture overview,
installation guide, submodule installation, recursive cloning, backend
documentation, dictionary format documentation, encoding behavior, platform
dictionary handling, Qt integration, context-menu customization, thesaurus
usage, personal dictionary, and host-application integration.

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
- `libs/pyqt6-linguistic-tools/docs/public-api.md`: stable public API surface.
- `libs/pyqt6-linguistic-tools/docs/`: existing documentation (linguistic
  service, backend API, registry, Qt architecture, etc.).

## Repository and commit discipline

Do not commit from the top level first. For ordinary public-api work,
commit and push the toolkit, then record its new pointer plus roadmap and
handoff updates in GuitarChordStudio:

```bash
cd libs/pyqt6-linguistic-tools
git add .
git diff --cached
git commit -m "feat(api): define stable public API and deprecation policy"
git push

cd ../..
git add .
git diff --cached
git commit -m "docs(roadmap): record public API phase"
git push
```

If a verified engine defect requires Spylls or PyThes changes, add the
regression test and commit that deepest fork first. Then update the toolkit
pointer, and finally the GuitarChordStudio pointer. Never force-reset a dirty
submodule or include unrelated user work.
