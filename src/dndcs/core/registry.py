# src/dndcs/core/registry.py
from __future__ import annotations

import os
import sys
import importlib
import importlib.util
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml


# --- manifest helpers ---------------------------------------------------------

def _read_manifest(manifest_path: Path) -> Dict[str, Any]:
    man = yaml.safe_load(manifest_path.read_text(encoding="utf-8")) or {}
    man["__manifest_dir__"] = str(manifest_path.parent)
    return man

def default_module_id() -> str:
    # Allow override via env; otherwise stock 5e
    return os.getenv("DNDCS_DEFAULT_MODULE_ID", "fivee_stock")


# --- search roots -------------------------------------------------------------

def _internal_modules_root() -> Path:
    # packaged/built-in (optional)
    return Path(__file__).resolve().parents[1] / "modules"

def _repo_modules_root() -> Path:
    # repo-level ./modules next to cwd
    return Path.cwd() / "modules"

def _dropin_mods_root() -> Path:
    # preferred drag-and-drop location
    return Path.cwd() / "mods"

def _user_modules_root() -> Path:
    if os.name == "nt":
        base = Path(os.getenv("APPDATA", Path.home() / "AppData" / "Roaming"))
        return base / "DnDCS" / "modules"
    elif sys.platform == "darwin":
        return Path.home() / "Library" / "Application Support" / "DnDCS" / "modules"
    else:
        return Path(os.getenv("XDG_CONFIG_HOME", Path.home() / ".config")) / "dndcs" / "modules"


def module_search_paths(extra: Optional[List[Path]] = None) -> List[Path]:
    paths: List[Path] = []
    paths.append(_dropin_mods_root())  # ./mods (drag-and-drop)
    env = os.getenv("DNDCS_MODULE_PATH")
    if env:
        for p in env.split(os.pathsep):
            p = p.strip()
            if p:
                paths.append(Path(p).expanduser())
    paths.append(_user_modules_root())      # user config dir
    paths.append(_repo_modules_root())      # repo ./modules
    paths.append(_internal_modules_root())  # packaged
    if extra:
        paths.extend(extra)

    uniq, seen = [], set()
    for p in paths:
        try:
            rp = p.resolve()
        except Exception:
            rp = p
        if rp not in seen:
            uniq.append(rp)
            seen.add(rp)
    return uniq


# --- discovery & loading ------------------------------------------------------

def discover_modules(modules_dir: Optional[Path] = None) -> List[Dict[str, Any]]:
    manifests: List[Dict[str, Any]] = []
    roots = [modules_dir] if modules_dir else module_search_paths()
    for root in roots:
        if not root.exists():
            continue
        for mfile in root.glob("*/manifest.yaml"):
            man = _read_manifest(mfile)
            man["__root__"] = str(root)
            manifests.append(man)
    return manifests


def _load_from_module_file(py_path: Path, class_name: str):
    spec = importlib.util.spec_from_file_location(f"dndcs_mod_{py_path.stem}", py_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Cannot load module from {py_path}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)  # type: ignore[attr-defined]
    return getattr(mod, class_name)


def _resolve_entry(manifest: Dict[str, Any]):
    # accept common key variants
    entry = (
        manifest.get("entry_point")
        or manifest.get("file_entry")
        or manifest.get("entrypoint")
    )
    if not entry:
        raise ImportError(
            f"No entry_point in manifest for {manifest.get('id')} at {manifest.get('__manifest_dir__')}"
        )

    # IMPORTANT: split first, then inspect ONLY the left side
    modrel, sep, clsname = entry.partition(":")
    if not sep or not clsname:
        raise ImportError(
            f"Bad entry_point '{entry}' (expected 'path_or_mod:ClassName') in {manifest.get('__manifest_dir__')}"
        )

    # 1) Explicit file path (module.py:Class)
    if modrel.endswith(".py") or ("/" in modrel) or ("\\" in modrel):
        py_path = Path(manifest["__manifest_dir__"]) / modrel
        if not py_path.exists():
            raise ImportError(f"entry_point points to missing file: {py_path}")
        return _load_from_module_file(py_path, clsname)

    # 2) Tolerate short form 'module:Class' if '<dir>/module.py' exists
    candidate = Path(manifest["__manifest_dir__"]) / f"{modrel}.py"
    if candidate.exists():
        return _load_from_module_file(candidate, clsname)

    # 3) Fallback: treat as import path 'pkg.mod:Class'
    mod = importlib.import_module(modrel)
    return getattr(mod, clsname)


def load_module_by_manifest_id(module_id: str):
    for man in discover_modules():
        if man.get("id") == module_id:
            cls = _resolve_entry(man)
            return cls(man) if cls else None
    return None
