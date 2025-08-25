#!/usr/bin/env python3
"""
DnDCS: tiny starter CLI (no external deps)

Subcommands:
  init                      -> create folders (characters/, profiles/, modules/)
  new-character --name ...  -> create a character JSON (abilities prefilled)
  list-characters           -> list saved character files
  show <file>               -> pretty-print a character JSON

You can evolve this into the full package later (src/ + CLI), but this gets you moving now.
"""
from __future__ import annotations
import argparse
import json
import re
from pathlib import Path
from typing import Dict

REPO = Path(".").resolve()

ABILITIES = ["STR", "DEX", "CON", "INT", "WIS", "CHA"]

def slugify(name: str) -> str:
    s = name.strip().lower()
    s = re.sub(r"[^a-z0-9]+", "_", s)
    s = re.sub(r"_+", "_", s).strip("_")
    return s or "character"

def ensure_structure() -> None:
    (REPO / "characters").mkdir(parents=True, exist_ok=True)
    (REPO / "profiles").mkdir(parents=True, exist_ok=True)
    (REPO / "modules" / "fivee").mkdir(parents=True, exist_ok=True)

    # Minimal profile (YAML-like text; no parser needed yet)
    prof = REPO / "profiles" / "default.yaml"
    if not prof.exists():
        prof.write_text("module: fivee\nsettings: {}\n", encoding="utf-8")

    # Minimal module manifest placeholder (useful later)
    man = REPO / "modules" / "fivee" / "manifest.yaml"
    if not man.exists():
        man.write_text(
            "id: fivee\nname: D&D 5e (placeholder)\nversion: 0.0.1\n", encoding="utf-8"
        )

def default_abilities(score: int = 10) -> Dict[str, Dict[str, int]]:
    return {ab: {"name": ab, "score": int(score)} for ab in ABILITIES}

def new_character(name: str, module: str = "fivee", out_path: Path | None = None) -> Path:
    ensure_structure()
    payload = {
        "name": name,
        "level": 1,
        "abilities": default_abilities(10),
        "skills": [],
        "items": [],
        "feats": [],
        "notes": "",
        "module": module,
        "version": "0.1.0",
        "proficiencies": {"saving_throws": {}},
    }

    if out_path is None:
        out_path = REPO / "characters" / f"{slugify(name)}.json"

    out_path.parent.mkdir(parents=True, exist_ok=True)
    tmp = out_path.with_suffix(out_path.suffix + ".tmp")
    tmp.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    tmp.replace(out_path)
    return out_path

def list_characters() -> None:
    ensure_structure()
    chars = sorted((REPO / "characters").glob("*.json"))
    if not chars:
        print("(no characters yet)  -> use: python first_program.py new-character --name \"Aella Storm\"")
        return
    for p in chars:
        print(p.as_posix())

def show_character(path: Path) -> None:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    print(json.dumps(data, indent=2, ensure_ascii=False))

def main():
    parser = argparse.ArgumentParser(prog="dndcs-mini", description="DnDCS minimal starter CLI")
    sub = parser.add_subparsers(dest="cmd", required=True)

    sub.add_parser("init", help="Create folders and placeholders")

    nc = sub.add_parser("new-character", help="Create a character JSON")
    nc.add_argument("--name", required=True, help="Character name")
    nc.add_argument("--module", default="fivee", help="Rules module id (default: fivee)")
    nc.add_argument("--out", type=Path, help="Output path (defaults to characters/<slug>.json)")

    sub.add_parser("list-characters", help="List saved characters")

    sh = sub.add_parser("show", help="Pretty-print a character JSON")
    sh.add_argument("file", type=Path)

    args = parser.parse_args()

    if args.cmd == "init":
        ensure_structure()
        print("Initialized: characters/, profiles/, modules/fivee/")
    elif args.cmd == "new-character":
        out = new_character(args.name, module=args.module, out_path=args.out)
        print(f"Created {out}")
    elif args.cmd == "list-characters":
        list_characters()
    elif args.cmd == "show":
        show_character(args.file)

if __name__ == "__main__":
    main()
