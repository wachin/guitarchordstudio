"""Tests for the JSON ChordPages settings backend."""

from __future__ import annotations

from pathlib import Path

from PyQt6.QtCore import QByteArray, QSettings, QSize

from chordpages.settings import SettingsManager
from guitarchordstudio_paths import config_root


def test_json_settings_round_trip(tmp_path: Path):
    path = tmp_path / "settings.json"
    settings = SettingsManager.from_file(path)
    settings.set_language("es")
    settings.set_theme("dark")
    settings.set_recent_files([tmp_path / "song.mchord"])
    settings.set_value("test/geometry", QByteArray(b"geometry"))
    settings.set_value("test/size", QSize(640, 480))
    settings.sync()

    restored = SettingsManager.from_file(path)
    assert restored.language() == "es"
    assert restored.theme() == "dark"
    assert restored.recent_files() == [tmp_path / "song.mchord"]
    assert bytes(restored.value("test/geometry")) == b"geometry"
    assert restored.value("test/size") == QSize(640, 480)


def test_legacy_ini_is_migrated(tmp_path: Path, monkeypatch):
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path / "config"))
    app_dir = config_root() / "chordpages"
    app_dir.mkdir(parents=True)
    legacy = QSettings(str(app_dir / "settings.ini"), QSettings.Format.IniFormat)
    legacy.setValue("i18n/language", "es")
    legacy.sync()

    settings = SettingsManager()

    assert settings.language() == "es"
    assert (app_dir / "settings.json").exists()
    assert (app_dir / "settings.ini").exists()
