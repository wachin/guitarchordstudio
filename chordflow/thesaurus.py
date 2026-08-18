"""Mythes thesaurus support for ChordFlow."""

from __future__ import annotations

import os
import sys
from pathlib import Path


def _bundled_resources() -> Path:
    """Return the path to the bundled resources directory.

    Search order:
    1. ``resources/`` relative to project root (for Nuitka builds)
    2. ``third-party/libreoffice-dictionaries-collection/dicts/`` (dev/submodule)
    """
    module = Path(__file__).resolve().parent  # chordflow/
    for parent in (module.parent, module.parent.parent):
        # Check for resources/ at project root
        resources = parent / "resources" / "dicts"
        if resources.is_dir():
            return resources
        # Check for third-party submodule
        third_party = (
            parent
            / "third-party"
            / "libreoffice-dictionaries-collection"
            / "dicts"
        )
        if third_party.is_dir():
            return third_party
    return Path()


class MythesThesaurus:
    def __init__(self):
        self.languages = self._find_languages()
        self.cache = {}

    def _find_languages(self):
        labels = {
            "es": "Espanol (Ecuador)",
            "de": "Aleman",
            "en": "Ingles (Estados Unidos)",
        }
        best_by_path = {}
        search_dirs = []

        if sys.platform == "win32":
            # Windows: APPDATA + bundled resources
            appdata = os.environ.get("APPDATA", "")
            if appdata:
                search_dirs.append(Path(appdata) / "guitarchs" / "mythes")
        else:
            # Linux system paths
            search_dirs.extend([
                Path("/usr/share/mythes"),
                Path("/usr/share/hunspell"),
                Path("/usr/share/myspell/dicts"),
            ])

        # Bundled resources (always checked)
        bundled = _bundled_resources()
        if bundled and bundled.is_dir():
            search_dirs.append(bundled)

        for base in search_dirs:
            if not base.is_dir():
                continue
            for name in sorted(os.listdir(base)):
                if not (name.startswith("th_") and name.endswith(".dat")):
                    continue
                dat_path = os.path.join(base, name)
                idx_path = dat_path[:-4] + ".idx"
                if not os.path.exists(idx_path):
                    continue
                code = name[3:-4]
                if code.endswith("_v2"):
                    code = code[:-3]
                key = os.path.realpath(dat_path)
                lang = code.split("_")[0]
                label = labels.get(lang, code.replace("_", "-"))
                language = {
                    "code": code,
                    "label": label,
                    "dat": dat_path,
                }
                current = best_by_path.get(key)
                if current is None or self._language_priority(code) < self._language_priority(
                    current["code"]
                ):
                    best_by_path[key] = language

        # Also scan dict-*/ subdirectories in bundled resources for th_*.dat files
        if bundled and bundled.is_dir():
            for sub in bundled.iterdir():
                if sub.is_dir() and sub.name.startswith("dict-"):
                    for name in sorted(os.listdir(sub)):
                        if not (name.startswith("th_") and name.endswith(".dat")):
                            continue
                        dat_path = os.path.join(sub, name)
                        idx_path = dat_path[:-4] + ".idx"
                        if not os.path.exists(idx_path):
                            continue
                        code = name[3:-4]
                        if code.endswith("_v2"):
                            code = code[:-3]
                        key = os.path.realpath(dat_path)
                        lang = code.split("_")[0]
                        label = labels.get(lang, code.replace("_", "-"))
                        language = {
                            "code": code,
                            "label": label,
                            "dat": dat_path,
                        }
                        current = best_by_path.get(key)
                        if current is None or self._language_priority(code) < self._language_priority(
                            current["code"]
                        ):
                            best_by_path[key] = language

        languages = list(best_by_path.values())
        languages.sort(key=lambda item: (item["code"] != "es_ES", item["label"]))
        return languages

    def _language_priority(self, code):
        if code == "es_ES":
            return 0
        if code == "es_EC":
            return 1
        if code.startswith("es_"):
            return 2
        return 3

    def _read_entries(self, language):
        dat_path = language["dat"]
        if dat_path in self.cache:
            return self.cache[dat_path]

        entries = {}
        with open(dat_path, "rb") as file:
            raw = file.read()

        first_line, _, body = raw.partition(b"\n")
        encoding = first_line.decode("ascii", errors="ignore").strip() or "ISO8859-1"
        text = body.decode(encoding, errors="replace")
        lines = iter(text.splitlines())

        for line in lines:
            if "|" not in line:
                continue
            word, count_text = line.split("|", 1)
            try:
                count = int(count_text)
            except ValueError:
                continue

            groups = []
            for _ in range(count):
                try:
                    group_line = next(lines)
                except StopIteration:
                    break
                parts = [part.strip() for part in group_line.split("|") if part.strip()]
                if parts and parts[0] == "-":
                    parts = parts[1:]
                if parts:
                    groups.append(parts)

            entries[word.casefold()] = groups

        self.cache[dat_path] = entries
        return entries

    def lookup(self, word, language_index=0):
        if not word or not self.languages:
            return []
        language = self.languages[language_index]
        entries = self._read_entries(language)
        return entries.get(word.casefold(), [])

    def language_label(self, language_index=0):
        if not self.languages:
            return "Sin diccionario Mythes"
        return self.languages[language_index]["label"]


__all__ = ["MythesThesaurus"]
