# Agent instructions for GuitarChordStudio

Read `docs/AGENT-HANDOFF.md` and
`ROADMAP—PyQt6_Linguistic_Tools.md` before continuing linguistic-toolkit work.
The handoff identifies the current checkpoint and the next locally actionable
objective; the roadmap remains the source of truth for project scope.

## Repository boundaries

This checkout contains independent Git repositories:

- GuitarChordStudio is the top-level repository on `main`.
- `libs/pyqt6-linguistic-tools` is a submodule on `main` and owns reusable
  linguistic code, tests, examples, package metadata, and toolkit CI.
- `libs/pyqt6-linguistic-tools/libs/spylls` and `libs/pyqt6-linguistic-tools/libs/pythes`
  are maintained engine-fork submodules on `master`.
- `third-party/hunspell`, `third-party/mythes`, and `third-party/sonnet` inside
  the toolkit are reference sources, not initial runtime dependencies.
- `third-party/libreoffice-dictionaries-collection` in GuitarChordStudio is
  external test data. Never rewrite its dictionaries to make a test pass.

Make a change in the repository that owns the affected files. Commit and push
from the deepest changed repository toward the top-level repository. Follow
`docs/GIT-SUBMODULE-COMMIT-AND-PUSH-GUIDE.md`; do not commit generated caches,
build outputs, virtual environments, or unrelated user changes.

## Linguistic architecture

- Keep one cross-platform public API for ChordFlow, ChordPages, and other
  PyQt6 applications.
- Spylls and PyThes are the portable spelling and thesaurus engines for the
  initial release on Linux, Windows, and macOS.
- Linux may discover installed Hunspell/MyThes *dictionary files*, but those
  files are read through Spylls/PyThes. Do not start native Hunspell/MyThes
  backend development unless Phase 41's post-1.0 go/no-go gate is satisfied.
- Keep engines, dictionary discovery, application services, and Qt widgets in
  separate layers. Platform conditionals belong in providers, not editors.
- Keep GuitarChordStudio-specific chord recognition outside the standalone
  toolkit and pass it through the generic token-filter API.
- Treat official and system dictionaries as immutable. Persistent user words
  belong in the separate personal dictionary; ignored words remain in memory.
- Do not make Sonnet, KDE Frameworks, native Hunspell, or native MyThes a
  required dependency.

## Development contract

- The supported language floor is Python 3.10. Avoid APIs introduced later.
- Preserve the optional PyQt6 boundary: importing the core must not require Qt.
- Add focused regression tests before changing an engine fork or fixing a
  compatibility defect.
- Keep corpus paths configurable; never hard-code the parent checkout path in
  the standalone package.
- Update the toolkit README/CHANGELOG/docs and the top-level roadmap when an
  objective is genuinely complete. Do not check off platform or remote-policy
  work that was not actually verified.
- Run the smallest relevant tests while iterating, then the documented fast
  suite and `python3 -m mypy` before handoff. Corpus and platform commands are
  listed in `libs/pyqt6-linguistic-tools/docs/testing.md`.

