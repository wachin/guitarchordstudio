"""Dictionary manager for downloading and installing Hunspell/Mythes dictionaries.

Uses the ``dictionaries.json`` catalog to discover available dictionaries
and downloads them on demand from GitHub Releases.
"""

from __future__ import annotations

import json
import sys
import tarfile
import tempfile
from pathlib import Path
from urllib.request import urlopen
from urllib.error import URLError

from PyQt6.QtCore import QStandardPaths


# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

def _dicts_base() -> Path:
    """Return the base directory for installed dictionaries.

    Linux:   ~/.local/share/guitarchs/dicts/
    Windows: %APPDATA%/guitarchs/dicts/
    macOS:   ~/Library/Application Support/guitarchs/dicts/
    """
    data = Path(
        QStandardPaths.writableLocation(
            QStandardPaths.StandardLocation.AppDataLocation
        )
    )
    base = data / "guitarchs" / "dicts"
    base.mkdir(parents=True, exist_ok=True)
    return base


def _catalog_path() -> Path:
    """Return the path to the dictionaries catalog (dictionaries.json).

    Searches in order:
    1. Project root /dictionaries.json (development)
    2. Bundled resources/dictionaries.json (Nuitka build)
    3. Falls back to built-in minimal catalog
    """
    module = Path(__file__).resolve().parent  # chordflow/
    for parent in (module.parent, module.parent.parent):
        candidate = parent / "dictionaries.json"
        if candidate.exists():
            return candidate
        # Also check resources/ for Nuitka builds
        resources = parent / "resources" / "dictionaries.json"
        if resources.exists():
            return resources
    return Path()


# ---------------------------------------------------------------------------
# Catalog
# ---------------------------------------------------------------------------

_BUILTIN_CATALOG = {
    "source": "wachin/libreoffice-dictionaries-collection/releases/tag/v1.0-dictionaries-thesaurus",
    "dictionaries": [
        {"code": "en", "name": "English", "url": "https://github.com/wachin/libreoffice-dictionaries-collection/releases/download/v1.0-dictionaries-thesaurus/dict-en.tar.gz"},
        {"code": "es", "name": "Spanish", "url": "https://github.com/wachin/libreoffice-dictionaries-collection/releases/download/v1.0-dictionaries-thesaurus/dict-es.tar.gz"},
    ],
}


def load_catalog() -> dict:
    """Load the dictionaries catalog from dictionaries.json or built-in."""
    catalog_file = _catalog_path()
    if catalog_file and catalog_file.exists():
        try:
            with open(catalog_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            pass
    return dict(_BUILTIN_CATALOG)


def list_available() -> list[dict]:
    """Return a list of available dictionaries from the catalog.

    Each entry: ``{"code": "en", "name": "English", "url": "...", "size": 12345, "installed": True/False}``
    """
    catalog = load_catalog()
    dicts_base = _dicts_base()
    result = []
    for entry in catalog.get("dictionaries", []):
        code = entry["code"]
        prefix = f"dict-{code}"
        installed = (dicts_base / prefix).is_dir()
        result.append({**entry, "installed": installed})
    return result


def list_installed() -> list[dict]:
    """Return only the installed dictionaries."""
    return [d for d in list_available() if d["installed"]]


# ---------------------------------------------------------------------------
# Download & Install
# ---------------------------------------------------------------------------

def download_and_install(code: str, progress_callback=None) -> Path:
    """Download and install a dictionary by its code.

    Args:
        code: The language code (e.g. "en", "es", "fr").
        progress_callback: Optional callable(bytes_downloaded, total_bytes).

    Returns:
        The path to the installed dictionary directory.

    Raises:
        ValueError: If the code is not found in the catalog.
        URLError: If the download fails.
    """
    catalog = load_catalog()
    entry = None
    for d in catalog.get("dictionaries", []):
        if d["code"] == code:
            entry = d
            break

    if entry is None:
        raise ValueError(f"Dictionary '{code}' not found in catalog")

    url = entry["url"]
    prefix = f"dict-{code}"
    dest = _dicts_base() / prefix

    # Download to temp file
    with tempfile.NamedTemporaryFile(suffix=".tar.gz", delete=False) as tmp:
        tmp_path = Path(tmp.name)
        try:
            with urlopen(url) as response:
                total = int(response.headers.get("Content-Length", 0))
                downloaded = 0
                while True:
                    chunk = response.read(8192)
                    if not chunk:
                        break
                    downloaded += len(chunk)
                    tmp.write(chunk)
                    if progress_callback:
                        progress_callback(downloaded, total)
        except URLError as e:
            tmp_path.unlink(missing_ok=True)
            raise URLError(f"Failed to download dictionary from {url}: {e}")

    # Extract
    try:
        with tarfile.open(tmp_path, "r:gz") as tar:
            # Extract only the dict-*/ directory contents
            members = []
            for m in tar.getmembers():
                if m.name.startswith(prefix + "/") or m.name.startswith("./" + prefix + "/"):
                    # Strip the prefix
                    m.name = m.name.replace(prefix + "/", "").replace("./" + prefix + "/", "")
                    members.append(m)
            tar.extractall(dest, members=members)
    except tarfile.TarError as e:
        raise RuntimeError(f"Failed to extract dictionary: {e}")
    finally:
        tmp_path.unlink(missing_ok=True)

    return dest


def uninstall(code: str) -> None:
    """Remove an installed dictionary."""
    prefix = f"dict-{code}"
    target = _dicts_base() / prefix
    if target.is_dir():
        import shutil
        shutil.rmtree(target)


# ---------------------------------------------------------------------------
# CLI / standalone usage
# ---------------------------------------------------------------------------

def main():
    """Simple CLI for managing dictionaries."""
    import argparse

    parser = argparse.ArgumentParser(description="Manage GuitarChordStudio dictionaries")
    sub = parser.add_subparsers(dest="command")

    sub.add_parser("list", help="List available dictionaries")
    sub.add_parser("installed", help="List installed dictionaries")

    install_p = sub.add_parser("install", help="Install a dictionary")
    install_p.add_argument("code", help="Language code (e.g. en, es, fr)")

    uninstall_p = sub.add_parser("uninstall", help="Remove a dictionary")
    uninstall_p.add_argument("code", help="Language code")

    args = parser.parse_args()

    if args.command == "list":
        dicts = list_available()
        for d in dicts:
            status = "INSTALLED" if d["installed"] else "available"
            print(f"  [{status}] {d['code']:6s}  {d['name']}")
    elif args.command == "installed":
        dicts = list_installed()
        if not dicts:
            print("  (no dictionaries installed)")
        for d in dicts:
            print(f"  {d['code']:6s}  {d['name']}")
    elif args.command == "install":
        def progress(downloaded, total):
            if total:
                pct = downloaded / total * 100
                print(f"\r  Downloading: {pct:.0f}%", end="", flush=True)
            else:
                print(f"\r  Downloading: {downloaded} bytes", end="", flush=True)

        print(f"  Installing dictionary '{args.code}'...")
        try:
            path = download_and_install(args.code, progress)
            print(f"\n  Installed to: {path}")
        except Exception as e:
            print(f"\n  Error: {e}")
            sys.exit(1)
    elif args.command == "uninstall":
        print(f"  Removing dictionary '{args.code}'...")
        uninstall(args.code)
        print("  Done.")
    else:
        parser.print_help()


__all__ = [
    "load_catalog",
    "list_available",
    "list_installed",
    "download_and_install",
    "uninstall",
    "_dicts_base",
]
