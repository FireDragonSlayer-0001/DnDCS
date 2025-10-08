from __future__ import annotations
from pathlib import Path
import importlib.util
from types import ModuleType
from typing import Dict, List, Any

class ModuleBase:
    """Base class for rules modules supporting a structured layout.

    Subsystems such as ``items`` or ``spells`` can be placed in subdirectories
    next to the module's ``manifest.yaml``.  Each ``.py`` file inside those
    folders is imported automatically and made available via ``subsystems``.
    """

    def __init__(self, manifest: Dict[str, Any]) -> None:
        self.manifest = manifest
        self.subsystems: Dict[str, List[ModuleType]] = {}
        base = Path(manifest.get("__manifest_dir__", "."))
        sections: List[str] = list(manifest.get("subsystems", []) or [])
        for sect in sections:
            sect_dir = base / sect
            if not sect_dir.is_dir():
                continue
            loaded: List[ModuleType] = []
            for py in sect_dir.glob("*.py"):
                if py.name == "__init__.py":
                    continue
                spec = importlib.util.spec_from_file_location(
                    f"dndcs_mod_{manifest.get('id','mod')}_{sect}_{py.stem}", py
                )
                if spec and spec.loader:
                    mod = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(mod)  # type: ignore[attr-defined]
                    loaded.append(mod)
            if loaded:
                self.subsystems[sect] = loaded
