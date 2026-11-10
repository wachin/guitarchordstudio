"""Linguistic service factory for GuitarChordStudio applications.

Adds the ``pyqt6-linguistic-tools`` submodule to the Python import path and
delegates provider selection to the toolkit's reusable ``create_service()``.

Usage::

    from chordflow.linguistic_service import create_linguistic_service

    service = create_linguistic_service()
    service.check_word("hello")
"""

from __future__ import annotations

import os
import sys
from pathlib import Path


def _ensure_toolkit_on_path() -> None:
    """Add the ``pyqt6-linguistic-tools`` submodule to ``sys.path``."""
    repo_root = Path(__file__).resolve().parent.parent
    toolkit_root = repo_root / "libs" / "pyqt6-linguistic-tools"
    paths = [
        toolkit_root / "src",
        toolkit_root / "libs" / "spylls",
        toolkit_root / "libs" / "pythes",
    ]
    for path in paths:
        text = str(path)
        if text not in sys.path:
            sys.path.insert(0, text)


# Ensure the toolkit is importable before any other code uses it.
_ensure_toolkit_on_path()


from pyqt6_linguistic_tools import LinguisticService, create_service  # noqa: E402


def _corpus_root() -> Path | None:
    """Return the path to the bundled LibreOffice dictionaries, or ``None``."""
    repo_root = Path(__file__).resolve().parent.parent

    candidate = (
        repo_root
        / "third-party"
        / "libreoffice-dictionaries-collection"
        / "dicts"
    )
    if candidate.is_dir():
        return candidate

    candidate = repo_root / "resources" / "dicts"
    if candidate.is_dir():
        return candidate

    env = os.environ.get("LIBREOFFICE_DICTIONARIES_PATH")
    if env:
        candidate = Path(env).expanduser().resolve()
        if candidate.is_dir():
            return candidate

    return None


def create_linguistic_service(
    *,
    language: str | None = None,
    namespace: str = "guitarchordstudio",
) -> LinguisticService:
    """Create a service with the shared GuitarChordStudio namespace."""
    return create_service(
        language=language,
        namespace=namespace,
        corpus_path=_corpus_root(),
    )


__all__ = ["create_linguistic_service"]
