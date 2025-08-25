import os, sys
import importlib, importlib.util
from pathlib import Path
from typing import Any, Dict, List, Optional
import yaml

def _read_manifest(manifest_path: Path) -> Dict[str, Any]:
    man = yaml.safe_load(manifest_path.read_text(encoding="utf-8")) or {}
    man["__manifest_dir__"] = str(manifest_path.parent)
    return man

def _internal_modules_root() -> Path:
    # packaged/built-in (optional)
    return Path(__file__).resolve().parents[1] / "modules"

def _repo_modules_root() -> Path:
    # repo-level modules/ next to where the program is run
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
    paths.append(_dropin_mods_root())       # ./mods (drag-and-drop)
    env = os.getenv("DNDCS_MODULE_PATH")    # e.g., "D:/DnDMods;C:/OtherMods"
    if env:
        for p in env.split(os.pathsep):
            p = p.strip()
            if p: paths.append(Path(p).expanduser())
    paths.append(_user_modules_root())      # user config dir
    paths.append(_repo_modules_root())      # repo ./modules
    paths.append(_internal_modules_root())  # packaged
    if extra: paths.extend(extra)

    uniq, seen = [], set()
    for p in paths:
        try:
            rp = p.resolve()
        except Exception:
            rp = p
        if rp not in seen:
            uniq.append(rp); seen.add(rp)
    return uniq

def discover_modules(modules_dir: Optional[Path] = None) -> List[Dict[str, Any]]:
    manifests: List[Dict[str, Any]] = []
    roots = [modules_dir] if modules_dir else module_search_paths()
    for root in roots:
        if not root.exists(): continue
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
    # prefer file-based "entry_point" like "module.py:FiveEModule"
    entry = manifest.get("entry_point") or manifest.get("file_entry")
    if not entry: return None
    if entry.endswith(".py") or "/" in entry or "\\" in entry:
        modrel, _, clsname = entry.partition(":")
        py_path = Path(manifest["__manifest_dir__"]) / modrel
        return _load_from_module_file(py_path, clsname)
    mod_path, _, clsname = entry.partition(":")
    mod = importlib.import_module(mod_path)
    return getattr(mod, clsname)

def load_module_by_manifest_id(module_id: str):
    for man in discover_modules():
        if man.get("id") == module_id:
            cls = _resolve_entry(man)
            return cls(man) if cls else None
    return None
