"""DnDCS core package.

This package now acts as a facade over the feature-first repository layout
introduced in ``AGENTS.md``.  Importing :mod:`dndcs` ensures that companion
packages living in ``main-Core`` and ``webui`` are available on the Python
module search path so legacy imports keep working.
"""

from __future__ import annotations

import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[1]
for rel in ("main-Core", "webui"):
    candidate = _REPO_ROOT / rel
    if candidate.exists():
        path_str = str(candidate)
        if path_str not in sys.path:
            sys.path.append(path_str)
