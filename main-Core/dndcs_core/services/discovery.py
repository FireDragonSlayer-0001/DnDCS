from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml


def _read_manifest(manifest_path: Path) -> Dict[str, Any]:
    man = yaml.safe_load(manifest_path.read_text(encoding="utf-8")) or {}
    man["__manifest_dir__"] = str(manifest_path.parent)
    return man


def _internal_module_roots() -> List[Path]:
    """Return built-in module search roots shipped with the repository."""

    core_root = Path(__file__).resolve().parents[1]
    candidates = [
        core_root / "modules",  # legacy location
        core_root.parents[0] / "rulesets" / "dndcs_rulesets",
    ]
    roots: List[Path] = []
    for path in candidates:
        if path.exists():
            roots.append(path)
    return roots


def _repo_module_roots() -> List[Path]:
    """Return add-on roots that live inside the repository."""

    candidates = [
        Path.cwd() / "main-Addons",
        Path.cwd() / "modules",  # legacy layout
    ]
    return [path for path in candidates if path.exists()]


def _dropin_mods_root() -> Path:
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
    paths.append(_dropin_mods_root())
    env = os.getenv("DNDCS_MODULE_PATH")
    if env:
        for p in env.split(os.pathsep):
            p = p.strip()
            if p:
                paths.append(Path(p).expanduser())
    paths.append(_user_modules_root())
    paths.extend(_repo_module_roots())
    paths.extend(_internal_module_roots())
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
