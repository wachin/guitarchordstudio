"""Tests for the shared GuitarChordStudio configuration/data layout."""

from __future__ import annotations

from pathlib import Path

import guitarchordstudio_paths as paths


def test_linux_paths_follow_xdg_and_use_lowercase(monkeypatch, tmp_path):
    monkeypatch.setattr(paths.sys, "platform", "linux")
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path / "config"))
    monkeypatch.setenv("XDG_DATA_HOME", str(tmp_path / "data"))

    assert paths.config_root() == tmp_path / "config" / "guitarchordstudio"
    assert paths.data_root() == tmp_path / "data" / "guitarchordstudio"
    assert paths.app_config_dir("ChordPages") == (
        tmp_path / "config" / "guitarchordstudio" / "chordpages"
    )
    assert paths.app_data_dir("ChordPages") == (
        tmp_path / "data" / "guitarchordstudio" / "chordpages"
    )
    assert paths.dictionaries_dir() == (
        tmp_path / "data" / "guitarchordstudio" / "dictionaries"
    )


def test_windows_paths_use_appdata_and_visible_names(monkeypatch, tmp_path):
    monkeypatch.setattr(paths.sys, "platform", "win32")
    monkeypatch.setenv("APPDATA", str(tmp_path / "appdata"))
    monkeypatch.setenv("LOCALAPPDATA", str(tmp_path / "localappdata"))

    assert paths.config_root() == tmp_path / "appdata" / "GuitarChordStudio"
    assert paths.app_config_dir("chordpages") == (
        tmp_path / "appdata" / "GuitarChordStudio" / "ChordPages"
    )
    assert paths.app_data_dir("chordflow") == (
        tmp_path / "appdata" / "GuitarChordStudio" / "ChordFlow"
    )
    assert paths.dictionaries_dir() == (
        tmp_path / "localappdata" / "GuitarChordStudio" / "dictionaries"
    )


def test_macos_paths_use_application_support(monkeypatch, tmp_path):
    monkeypatch.setattr(paths.sys, "platform", "darwin")
    monkeypatch.setattr(Path, "home", lambda: tmp_path)

    assert paths.config_root() == (
        tmp_path / "Library" / "Application Support" / "GuitarChordStudio"
    )
    assert paths.dictionaries_dir() == (
        tmp_path
        / "Library"
        / "Application Support"
        / "GuitarChordStudio"
        / "dictionaries"
    )
