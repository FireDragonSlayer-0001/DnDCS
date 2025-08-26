from __future__ import annotations

import importlib
import importlib.util
from pathlib import Path
from typing import Any, Dict

from .discovery import discover_modules


def _load_from_module_file(py_path: Path, class_name: str):
    spec = importlib.util.spec_from_file_location(f"dndcs_mod_{py_path.stem}", py_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Cannot load module from {py_path}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)  # type: ignore[attr-defined]
    return getattr(mod, class_name)


def _resolve_entry(manifest: Dict[str, Any]):
    entry = (
        manifest.get("entry_point")
        or manifest.get("file_entry")
        or manifest.get("entrypoint")
    )
    if not entry:
        raise ImportError(
            f"No entry_point in manifest for {manifest.get('id')} at {manifest.get('__manifest_dir__')}"
        )

    modrel, sep, clsname = entry.partition(":")
    if not sep or not clsname:
        raise ImportError(
            f"Bad entry_point '{entry}' (expected 'path_or_mod:ClassName') in {manifest.get('__manifest_dir__')}"
        )

    if modrel.endswith(".py") or ("/" in modrel) or ("\\" in modrel):
        py_path = Path(manifest["__manifest_dir__"]) / modrel
        if not py_path.exists():
            raise ImportError(f"entry_point points to missing file: {py_path}")
        return _load_from_module_file(py_path, clsname)

    candidate = Path(manifest["__manifest_dir__"]) / f"{modrel}.py"
    if candidate.exists():
        return _load_from_module_file(candidate, clsname)

    mod = importlib.import_module(modrel)
    return getattr(mod, clsname)


def load_module_by_manifest_id(module_id: str):
    for man in discover_modules():
        if man.get("id") == module_id:
            cls = _resolve_entry(man)
            return cls(man) if cls else None
    return None
