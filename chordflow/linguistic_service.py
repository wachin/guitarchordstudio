"""Linguistic service factory for GuitarChordStudio applications.

Adds the ``pyqt6-linguistic-tools`` submodule to the Python import path and
provides a factory function that creates a ``LinguisticService`` configured
with the appropriate dictionary providers for the current platform.

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
    # Determine the repository root (parent of chordflow/)
    repo_root = Path(__file__).resolve().parent.parent
    toolkit_root = repo_root / "libs" / "pyqt6-linguistic-tools"

    paths = [
        str(toolkit_root / "src"),
        str(toolkit_root / "libs" / "spylls"),
        str(toolkit_root / "libs" / "pythes"),
    ]
    for path in paths:
        if path not in sys.path:
            sys.path.insert(0, path)


# Ensure the toolkit is importable before any other code uses it.
_ensure_toolkit_on_path()


from pyqt6_linguistic_tools import (  # noqa: E402
    DEFAULT_LINUX_DICTIONARY_PATHS,
    DictionaryRegistry,
    DictionarySourcePriority,
    DirectoryDictionaryProvider,
    LinguisticService,
    LinuxSystemDictionaryProvider,
    ManagedDictionaryProvider,
    UserDictionaryProvider,
    normalize_locale,
)


def _corpus_root() -> Path | None:
    """Return the path to the bundled LibreOffice dictionaries, or ``None``."""
    repo_root = Path(__file__).resolve().parent.parent

    # Check the submodule path first
    candidate = (
        repo_root
        / "third-party"
        / "libreoffice-dictionaries-collection"
        / "dicts"
    )
    if candidate.is_dir():
        return candidate

    # Check the resources directory (for packaged builds)
    candidate = repo_root / "resources" / "dicts"
    if candidate.is_dir():
        return candidate

    # Allow override via environment variable
    env = os.environ.get("LIBREOFFICE_DICTIONARIES_PATH")
    if env:
        candidate = Path(env).expanduser().resolve()
        if candidate.is_dir():
            return candidate

    return None


def _default_language() -> str:
    """Return a reasonable default language based on the environment."""
    import locale as _locale

    try:
        lang, _encoding = _locale.getdefaultlocale()
        if lang:
            return normalize_locale(lang)
    except Exception:
        pass
    return "es_ES"


def create_linguistic_service(
    *,
    language: str | None = None,
    namespace: str = "guitarchordstudio",
) -> LinguisticService:
    """Create and return a configured ``LinguisticService``.

    The service discovers dictionaries from:
    - Linux system paths (``/usr/share/hunspell``, ``/usr/share/mythes``)
    - Bundled LibreOffice corpus (``third-party/libreoffice-dictionaries-collection/dicts``)
    - Application-managed and user-imported dictionaries

    Args:
        language: Initial language (default: system locale or ``es_ES``).
        namespace: Namespace for managed and personal dictionary storage.

    Returns:
        A ready-to-use ``LinguisticService`` instance.
    """
    providers: list = [LinuxSystemDictionaryProvider()]

    corpus = _corpus_root()
    if corpus is not None:
        providers.append(
            DirectoryDictionaryProvider(
                corpus,
                source="libreoffice-corpus",
                priority=DictionarySourcePriority.MANAGED,
            )
        )

    providers.extend(
        [
            ManagedDictionaryProvider(namespace=namespace),
            UserDictionaryProvider(namespace=namespace),
        ]
    )

    registry = DictionaryRegistry(tuple(providers))
    lang = language or _default_language()

    return LinguisticService(
        lang,
        registry=registry,
        namespace=namespace,
    )


__all__ = [
    "create_linguistic_service",
]