"""Test configuration for chordflow tests."""

from __future__ import annotations

import sys
from pathlib import Path


# Add the pyqt6-linguistic-tools toolkit to the Python path.
_repo_root = Path(__file__).resolve().parent.parent.parent
_toolkit_root = _repo_root / "libs" / "pyqt6-linguistic-tools"

_paths = [
    str(_toolkit_root / "src"),
    str(_toolkit_root / "libs" / "spylls"),
    str(_toolkit_root / "libs" / "pythes"),
]
for _path in _paths:
    if _path not in sys.path:
        sys.path.insert(0, _path)