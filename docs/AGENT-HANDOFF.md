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

## Completed objective: dictionary compatibility report

The machine-readable, locale-by-locale dictionary compatibility report has been
implemented and integrated with corpus CI. The implementation:

- Discovers the configured LibreOffice corpus using existing registry/provider
  infrastructure without GuitarChordStudio-specific paths.
- Validates every discoverable spelling and thesaurus component independently.
- Emits versioned UTF-8 JSON (schema version 1) with deterministic key ordering.
- Includes reproducibility metadata: toolkit/engine versions, Python/platform,
  generation time, and corpus identity.
- Records per locale/component: relative source paths, source encoding,
  validation checks/warnings/failures, and explicit classification
  (`ready`/`limited`/`unsupported`).
- Aggregates failures and writes a valid report even when components fail.
- Includes deterministic fixture tests (schema, serialization, ordering, errors)
  in the fast suite and real-corpus assertions without freezing suggestion
  lists.
- Provides a documented CLI entry point (`python -m
  pyqt6_linguistic_tools.compatibility_report`) that works without PyQt6.
- Generates the JSON report in `.github/workflows/corpus.yml` with a new
  `upload_compatibility_report` input (default false), 3-day retention, and
  preserves existing JUnit artifacts.
- Updates README, testing docs, CHANGELOG, and roadmap checkboxes.

## Next objective: standalone examples (Phase 35)

Create standalone examples that do not depend on GuitarChordStudio:

Run commands from `libs/pyqt6-linguistic-tools`. Use the active virtual
environment if one exists; on this development machine the source checkout is
also configured by pytest's `pythonpath` setting.

```bash
QT_QPA_PLATFORM=offscreen python3 -m pytest -c pyproject.toml -q \
  -m 'not corpus and not platform'
python3 -m mypy
```

Run the focused corpus-report test with the explicit local corpus:

```bash
python3 -m pytest -c pyproject.toml -q -m corpus \
  --dictionary-corpus=../../third-party/libreoffice-dictionaries-collection/dicts
```

The complete corpus can consume substantial time and memory. Run it only when
the implementation needs it or before declaring full-corpus compatibility;
do not repeatedly run it during small documentation or schema iterations.
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
- `libs/pyqt6-linguistic-tools/src/pyqt6_linguistic_tools/validation.py`:
  reusable structured validation.
- `libs/pyqt6-linguistic-tools/src/pyqt6_linguistic_tools/providers.py` and
  `registry.py`: discovery, priorities, and locale/component pairing.
- `libs/pyqt6-linguistic-tools/src/pyqt6_linguistic_tools/models.py`: existing
  immutable report and metadata types.
- `libs/pyqt6-linguistic-tools/tests/conftest.py`: corpus option/environment
  handling.
- `libs/pyqt6-linguistic-tools/.github/workflows/corpus.yml`: current corpus
  jobs and JUnit artifacts.
- `libs/pyqt6-linguistic-tools/docs/testing.md` and
  `docs/continuous-integration.md`: maintained test contracts.

## Repository and commit discipline

Do not commit from the top level first. For ordinary compatibility-report
work, commit and push the toolkit, then record its new pointer plus roadmap and
handoff updates in GuitarChordStudio:

```bash
cd libs/pyqt6-linguistic-tools
git add .
git diff --cached
git commit -m "feat(validation): add dictionary compatibility report"
git push

cd ../..
git add .
git diff --cached
git commit -m "docs(roadmap): record compatibility report support"
git push
```

If a verified engine defect requires Spylls or PyThes changes, add the
regression test and commit that deepest fork first. Then update the toolkit
pointer, and finally the GuitarChordStudio pointer. Never force-reset a dirty
submodule or include unrelated user work.
