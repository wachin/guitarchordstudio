"""Small JSON settings backend with Qt value compatibility."""

from __future__ import annotations

import base64
import json
import os
from pathlib import Path
import tempfile
from typing import Any

from PyQt6.QtCore import QByteArray, QSize


_FORMAT = "guitarchordstudio-settings"
_VERSION = 1


class JsonSettings:
    """Store flat settings keys in one human-readable JSON file."""

    def __init__(self, path: str | Path):
        self.path = Path(path).expanduser()
        self._values: dict[str, Any] = {}
        self._load()

    def value(self, key: str, default: Any = None) -> Any:
        if key not in self._values:
            return default
        return _decode(self._values[key])

    def setValue(self, key: str, value: Any) -> None:
        self._values[str(key)] = _encode(value)
        self._save()

    def remove(self, key: str) -> None:
        key = str(key)
        for stored_key in tuple(self._values):
            if stored_key == key or stored_key.startswith(f"{key}/"):
                del self._values[stored_key]
        self._save()

    def clear(self) -> None:
        self._values.clear()
        self._save()

    def sync(self) -> None:
        self._save()

    def _load(self) -> None:
        try:
            payload = json.loads(self.path.read_text(encoding="utf-8"))
        except (OSError, UnicodeError, json.JSONDecodeError):
            return
        if not isinstance(payload, dict):
            return
        if payload.get("format") == _FORMAT and payload.get("version") == _VERSION:
            values = payload.get("settings")
            if isinstance(values, dict):
                self._values = values
        elif all(not str(key).startswith("__") for key in payload):
            # Accept a raw flat mapping for an early manual migration.
            self._values = payload

    def _save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "format": _FORMAT,
            "version": _VERSION,
            "settings": self._values,
        }
        descriptor, temporary_name = tempfile.mkstemp(
            prefix=f".{self.path.name}.",
            suffix=".tmp",
            dir=self.path.parent,
        )
        temporary = Path(temporary_name)
        try:
            with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as output:
                json.dump(payload, output, ensure_ascii=False, indent=2)
                output.write("\n")
                output.flush()
                os.fsync(output.fileno())
            os.replace(temporary, self.path)
        except OSError:
            temporary.unlink(missing_ok=True)
            raise


def _encode(value: Any) -> Any:
    if isinstance(value, QByteArray):
        return {
            "$type": "QByteArray",
            "base64": base64.b64encode(bytes(value)).decode("ascii"),
        }
    if isinstance(value, QSize):
        return {"$type": "QSize", "width": value.width(), "height": value.height()}
    return value


def _decode(value: Any) -> Any:
    if isinstance(value, dict):
        value_type = value.get("$type")
        if value_type == "QByteArray":
            return QByteArray(base64.b64decode(str(value.get("base64", ""))))
        if value_type == "QSize":
            return QSize(int(value.get("width", 0)), int(value.get("height", 0)))
    return value


__all__ = ["JsonSettings"]
