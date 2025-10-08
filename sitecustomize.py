"""Test/development helper to expose the source packages without installation."""

from __future__ import annotations

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent
for rel in ("src", "main-Core", "webui"):
    candidate = _ROOT / rel
    if candidate.exists():
        path_str = str(candidate)
        if path_str not in sys.path:
            sys.path.insert(0, path_str)
