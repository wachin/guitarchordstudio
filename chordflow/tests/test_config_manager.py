"""Tests for ChordFlow settings paths and migration."""

from __future__ import annotations

import json
from pathlib import Path

from chordflow.config_manager import ConfigManager
from guitarchordstudio_paths import config_root


def test_legacy_config_json_is_migrated(tmp_path: Path, monkeypatch):
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path / "config"))
    app_dir = config_root() / "chordflow"
    app_dir.mkdir(parents=True)
    legacy = app_dir / "config.json"
    legacy.write_text(json.dumps({"font_size": 13}), encoding="utf-8")

    manager = ConfigManager()

    assert manager.load()["font_size"] == 13
    new_path = app_dir / "settings.json"
    assert new_path.exists()
    assert json.loads(new_path.read_text(encoding="utf-8"))["font_size"] == 13
