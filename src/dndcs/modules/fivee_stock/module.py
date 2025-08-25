from __future__ import annotations
from typing import Dict, Any, List, Optional
from math import floor
from dndcs.core import models
from dndcs.core.module_base import ModuleBase

ABILS = ("STR","DEX","CON","INT","WIS","CHA")
SKILLS = [
    {"name":"Athletics","ability":"STR"},
    {"name":"Acrobatics","ability":"DEX"},
    {"name":"Sleight of Hand","ability":"DEX"},
    {"name":"Stealth","ability":"DEX"},
    {"name":"Arcana","ability":"INT"},
    {"name":"History","ability":"INT"},
    {"name":"Investigation","ability":"INT"},
    {"name":"Nature","ability":"INT"},
    {"name":"Religion","ability":"INT"},
    {"name":"Animal Handling","ability":"WIS"},
    {"name":"Insight","ability":"WIS"},
    {"name":"Medicine","ability":"WIS"},
    {"name":"Perception","ability":"WIS"},
    {"name":"Survival","ability":"WIS"},
    {"name":"Deception","ability":"CHA"},
    {"name":"Intimidation","ability":"CHA"},
    {"name":"Performance","ability":"CHA"},
    {"name":"Persuasion","ability":"CHA"},
]

# Full-caster spell slot progression by level 1..20 (Wizard/Cleric/Druid)
FULL_CASTER_SLOTS: Dict[int, List[int]] = {
    1:[2,0,0,0,0,0,0,0,0], 2:[3,0,0,0,0,0,0,0,0],
    3:[4,2,0,0,0,0,0,0,0], 4:[4,3,0,0,0,0,0,0,0],
    5:[4,3,2,0,0,0,0,0,0], 6:[4,3,3,0,0,0,0,0,0],
    7:[4,3,3,1,0,0,0,0,0], 8:[4,3,3,2,0,0,0,0,0],
    9:[4,3,3,3,1,0,0,0,0], 10:[4,3,3,3,2,0,0,0,0],
    11:[4,3,3,3,2,1,0,0,0], 12:[4,3,3,3,2,1,0,0,0],
    13:[4,3,3,3,2,1,1,0,0], 14:[4,3,3,3,2,1,1,0,0],
    15:[4,3,3,3,2,1,1,1,0], 16:[4,3,3,3,2,1,1,1,0],
    17:[4,3,3,3,2,1,1,1,1], 18:[4,3,3,3,3,1,1,1,1],
    19:[4,3,3,3,3,2,1,1,1], 20:[4,3,3,3,3,2,2,1,1],
}

def ability_mod(score: int) -> int:
    return floor((score - 10) / 2)

def proficiency_bonus(level: int) -> int:
    return 2 + ((level - 1) // 4)

def _get_scores(char: models.Character) -> Dict[str, int]:
    out: Dict[str, int] = {}
    for k in ABILS:
        a = char.abilities.get(k)
        if a: out[k] = int(a.score)
    return out

def _mods(scores: Dict[str,int]) -> Dict[str,int]:
    return {k: ability_mod(v) for k,v in scores.items()}

def _compute_ac(char: models.Character, mods: Dict[str,int]) -> Dict[str, Any]:
    dex = mods.get("DEX", 0)
    best = 10 + dex
    source = "unarmored"
    shield = 0
    wearing_armor = False
    for it in (char.items or []):
        p = getattr(it, "props", {}) or {}
        # armor
        if isinstance(p, dict) and "armor" in p:
            wearing_armor = True
            armor = p["armor"] or {}
            base = int(armor.get("base", 10))
            cat = armor.get("category", "light")
            dex_cap = armor.get("dex_cap", None)
            dex_part = dex if dex_cap is None else min(dex, int(dex_cap))
            ac = base + (dex_part if cat in ("light","medium") else 0)
            if ac > best:
                best, source = ac, f"armor({cat})"
        # shield
        if isinstance(p, dict) and "shield_bonus" in p:
            shield = max(shield, int(p["shield_bonus"]))
        # mage armor (no armor worn)
        if isinstance(p, dict) and (p.get("ac_base") == 13) and not wearing_armor:
            ac = 13 + dex
            if ac > best:
                best, source = ac, "mage_armor"
    return {"value": best + shield, "breakdown": {"base": best, "shield": shield}, "source": source}

def _wizard_block(char: models.Character, mods: Dict[str,int]) -> Optional[Dict[str, Any]]:
    # enable if Spellbook item exists (name "Spellbook" or props.spellbook)
    sb = None
    for it in (char.items or []):
        name = (it.name or "").lower()
        props = getattr(it, "props", {}) or {}
        if "spellbook" in props or name == "spellbook":
            sb = props.get("spellbook", {})
            break
    if sb is None:
        return None

    level = int(char.level)
    pb = proficiency_bonus(level)
    int_mod = mods.get("INT", 0)
    slots = FULL_CASTER_SLOTS.get(level, [0]*9)
    prepared_cap = max(1, level + int_mod)

    prepared = []
    for L in range(1,10):
        for s in sb.get("prepared", {}).get(str(L), []):
            if s not in prepared:
                prepared.append(s)
    if len(prepared) > prepared_cap:
        prepared = prepared[:prepared_cap]

    return {
        "class": "wizard",
        "spellcasting_ability": "INT",
        "spell_save_dc": 8 + pb + int_mod,
        "spell_attack_mod": pb + int_mod,
        "prepared_max": prepared_cap,
        "prepared_spells": prepared,
        "slots": {str(i+1): slots[i] for i in range(9)},
    }

class FiveEStockModule(ModuleBase):
    def __init__(self, manifest: Dict[str, Any]):
        # Automatically pull in any subsystem folders declared in the manifest
        # (items, feats, spells, etc.) so the module can extend itself without
        # being a monolithic single file.
        super().__init__(manifest)

    def id(self) -> str:
        return self.manifest.get("id", "fivee_stock")

    # templates for new_character
    def template_abilities(self) -> Dict[str,int]:
        return {k: 10 for k in ABILS}

    def template_skills(self) -> List[Dict[str,str]]:
        return SKILLS

    # engine hooks
    def validate(self, char: models.Character) -> List[str]:
        issues: List[str] = []
        if not (1 <= int(char.level) <= 20):
            issues.append("Level must be 1..20 for this module.")
        for k in ABILS:
            if k not in char.abilities:
                issues.append(f"Missing ability: {k}")
        return issues

    def derive(self, char: models.Character):
        scores = _get_scores(char)
        amods = _mods(scores)
        pb = proficiency_bonus(int(char.level))
        st_prof = getattr(getattr(char, "proficiencies", None), "saving_throws", {}) or {}
        saves = {k: amods.get(k,0) + (pb if st_prof.get(k, False) else 0) for k in ABILS}
        ac = _compute_ac(char, amods)
        out: Dict[str, Any] = {
            "proficiency_bonus": pb,
            "ability_mods": amods,
            "saving_throws": saves,
            "ac": ac,
        }
        wiz = _wizard_block(char, amods)
        if wiz: out["spellcasting"] = wiz
        return out
