"""File I/O helpers with encoding detection for ChordFlow."""

from __future__ import annotations

import os
from datetime import datetime

import chardet

from .config_manager import DEFAULT_CONFIG


def detect_encoding(file_path: str) -> dict:
    """Detect encoding and line-ending style of *file_path*.

    Returns a dict with keys ``encoding``, ``line_ending``, and ``raw``.
    """
    with open(file_path, "rb") as f:
        raw_data = f.read()

    detected = chardet.detect(raw_data)
    encoding: str = detected["encoding"] or "utf-8"

    if b"\r\n" in raw_data:
        line_ending = "Windows (CRLF)"
    elif b"\n" in raw_data:
        line_ending = "Unix (LF)"
    elif b"\r" in raw_data:
        line_ending = "Mac (CR)"
    else:
        line_ending = "Desconocido"

    return {"encoding": encoding, "line_ending": line_ending, "raw": raw_data}


def read_file(file_path: str) -> tuple[str, dict]:
    """Read *file_path* with automatic encoding detection.

    Returns ``(content, encoding_info)`` where *encoding_info* is the dict
    returned by :func:`detect_encoding`.
    """
    info = detect_encoding(file_path)
    with open(file_path, "r", encoding=info["encoding"], errors="replace") as f:
        content = f.read()
    return content, info


def normalize_line_endings(text: str, line_ending: str) -> str:
    """Convert *text* to the requested line-ending style."""
    if line_ending == "Windows (CRLF)":
        return text.replace("\n", "\r\n")
    if line_ending == "Mac (CR)":
        return text.replace("\n", "\r")
    return text


def write_file(file_path: str, content: str, encoding: str, line_ending: str) -> None:
    """Write *content* to *file_path* using the given *encoding* and line ending."""
    normalized = normalize_line_endings(content, line_ending)
    with open(file_path, "w", encoding=encoding) as f:
        f.write(normalized)


def add_to_recent_files(config: dict, file_path: str) -> dict:
    """Insert *file_path* at the front of the recent-files list in *config*.

    Returns the (potentially new) config dict for convenience.
    """
    recent = config.get("recent_files", [])
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    recent = [item for item in recent if item["path"] != file_path]
    recent.insert(0, {"path": file_path, "timestamp": timestamp})
    config["recent_files"] = recent[:9]
    return config


__all__ = [
    "detect_encoding",
    "read_file",
    "normalize_line_endings",
    "write_file",
    "add_to_recent_files",
]