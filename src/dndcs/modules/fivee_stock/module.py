from __future__ import annotations
from typing import Dict, Any, List, Optional
from pathlib import Path
from math import floor
from dndcs.core import models
from dndcs.core.module_base import ModuleBase
from dndcs.modules.fivee_stock.classes import CLASSES

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

# Half-caster spell slots (Paladin/Ranger)
HALF_CASTER_SLOTS: Dict[int, List[int]] = {1: [0]*9}
for _lvl in range(2, 21):
    HALF_CASTER_SLOTS[_lvl] = FULL_CASTER_SLOTS.get((_lvl + 1)//2, [0]*9)[:]

# Third-caster spell slots (Eldritch Knight/Arcane Trickster)
PCT_CASTER_SLOTS: Dict[int, List[int]] = {1: [0]*9, 2: [0]*9}
for _lvl in range(3, 21):
    PCT_CASTER_SLOTS[_lvl] = FULL_CASTER_SLOTS.get((_lvl + 2)//3, [0]*9)[:]

# Warlock pact magic slots
PACT_MAGIC_SLOTS: Dict[int, List[int]] = {
    1:[1,0,0,0,0,0,0,0,0], 2:[2,0,0,0,0,0,0,0,0],
    3:[0,2,0,0,0,0,0,0,0], 4:[0,2,0,0,0,0,0,0,0],
    5:[0,0,2,0,0,0,0,0,0], 6:[0,0,2,0,0,0,0,0,0],
    7:[0,0,0,2,0,0,0,0,0], 8:[0,0,0,2,0,0,0,0,0],
    9:[0,0,0,0,2,0,0,0,0], 10:[0,0,0,0,2,0,0,0,0],
    11:[0,0,0,0,3,0,0,0,0], 12:[0,0,0,0,3,0,0,0,0],
    13:[0,0,0,0,3,0,0,0,0], 14:[0,0,0,0,3,0,0,0,0],
    15:[0,0,0,0,3,0,0,0,0], 16:[0,0,0,0,3,0,0,0,0],
    17:[0,0,0,0,4,0,0,0,0], 18:[0,0,0,0,4,0,0,0,0],
    19:[0,0,0,0,4,0,0,0,0], 20:[0,0,0,0,4,0,0,0,0],
}

# Spells-known progressions
BARD_SPELLS_KNOWN = {
    1:4, 2:5, 3:6, 4:7, 5:8, 6:9, 7:10, 8:11, 9:12,
    10:14, 11:15, 12:15, 13:16, 14:18, 15:19, 16:19,
    17:20, 18:22, 19:22, 20:22,
}

SORCERER_SPELLS_KNOWN = {
    1:2, 2:3, 3:4, 4:5, 5:6, 6:7, 7:8, 8:9, 9:10,
    10:11, 11:12, 12:12, 13:13, 14:13, 15:14, 16:14,
    17:15, 18:15, 19:15, 20:15,
}

WARLOCK_SPELLS_KNOWN = {
    1:2, 2:3, 3:4, 4:5, 5:6, 6:7, 7:8, 8:9, 9:10,
    10:10, 11:11, 12:11, 13:12, 14:12, 15:13, 16:13,
    17:14, 18:14, 19:15, 20:15,
}

def ability_mod(score: int) -> int:
    return floor((score - 10) / 2)

def proficiency_bonus(level: int) -> int:
    return 2 + ((level - 1) // 4)

def _get_scores(char: models.Character) -> Dict[str, int]:
    out: Dict[str, int] = {}
    for k in ABILS:
        a = char.abilities.get(k)
        if a:
            out[k] = int(a.score)
    return out

def _mods(scores: Dict[str,int]) -> Dict[str,int]:
    return {k: ability_mod(v) for k,v in scores.items()}

def weapon_ability(weapon: Dict[str, Any], mods: Dict[str, int]) -> str:
    """Determine which ability modifier applies to a weapon."""
    props = weapon.get("properties", []) if isinstance(weapon, dict) else []
    if weapon.get("type") == "ranged":
        return "DEX"
    if "finesse" in props:
        return "DEX" if mods.get("DEX", 0) >= mods.get("STR", 0) else "STR"
    return "STR"

def weapon_attack_bonus(weapon: Dict[str, Any], mods: Dict[str, int], pb: int, proficient: bool = True) -> int:
    """Calculate total attack modifier for a weapon."""
    ability = weapon_ability(weapon, mods)
    return mods.get(ability, 0) + (pb if proficient else 0)

def weapon_damage_bonus(weapon: Dict[str, Any], mods: Dict[str, int]) -> int:
    """Calculate damage modifier for a weapon."""
    ability = weapon_ability(weapon, mods)
    return mods.get(ability, 0)

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

def _wizard_block(char: models.Character, mods: Dict[str,int], level: int, pb: int) -> Optional[Dict[str, Any]]:
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
        "slots": slots,
    }


def _cleric_block(char: models.Character, mods: Dict[str,int], level: int, pb: int) -> Dict[str, Any]:
    wis_mod = mods.get("WIS", 0)
    slots = FULL_CASTER_SLOTS.get(level, [0]*9)
    cap = max(1, level + wis_mod)
    prepared = (char.spellcasting.get("cleric", {}).get("prepared", []) if isinstance(char.spellcasting, dict) else [])[:cap]
    return {
        "class": "cleric",
        "spellcasting_ability": "WIS",
        "spell_save_dc": 8 + pb + wis_mod,
        "spell_attack_mod": pb + wis_mod,
        "prepared_max": cap,
        "prepared_spells": prepared,
        "slots": slots,
    }


def _druid_block(char: models.Character, mods: Dict[str,int], level: int, pb: int) -> Dict[str, Any]:
    wis_mod = mods.get("WIS", 0)
    slots = FULL_CASTER_SLOTS.get(level, [0]*9)
    cap = max(1, level + wis_mod)
    prepared = (char.spellcasting.get("druid", {}).get("prepared", []) if isinstance(char.spellcasting, dict) else [])[:cap]
    return {
        "class": "druid",
        "spellcasting_ability": "WIS",
        "spell_save_dc": 8 + pb + wis_mod,
        "spell_attack_mod": pb + wis_mod,
        "prepared_max": cap,
        "prepared_spells": prepared,
        "slots": slots,
    }


def _bard_block(char: models.Character, mods: Dict[str,int], level: int, pb: int) -> Dict[str, Any]:
    cha_mod = mods.get("CHA", 0)
    slots = FULL_CASTER_SLOTS.get(level, [0]*9)
    max_known = BARD_SPELLS_KNOWN.get(level, 0)
    known = (char.spellcasting.get("bard", {}).get("known", []) if isinstance(char.spellcasting, dict) else [])[:max_known]
    return {
        "class": "bard",
        "spellcasting_ability": "CHA",
        "spell_save_dc": 8 + pb + cha_mod,
        "spell_attack_mod": pb + cha_mod,
        "known_max": max_known,
        "known_spells": known,
        "slots": slots,
    }


def _sorcerer_block(char: models.Character, mods: Dict[str,int], level: int, pb: int) -> Dict[str, Any]:
    cha_mod = mods.get("CHA", 0)
    slots = FULL_CASTER_SLOTS.get(level, [0]*9)
    max_known = SORCERER_SPELLS_KNOWN.get(level, 0)
    known = (char.spellcasting.get("sorcerer", {}).get("known", []) if isinstance(char.spellcasting, dict) else [])[:max_known]
    return {
        "class": "sorcerer",
        "spellcasting_ability": "CHA",
        "spell_save_dc": 8 + pb + cha_mod,
        "spell_attack_mod": pb + cha_mod,
        "known_max": max_known,
        "known_spells": known,
        "slots": slots,
    }


def _paladin_block(char: models.Character, mods: Dict[str,int], level: int, pb: int) -> Dict[str, Any]:
    cha_mod = mods.get("CHA", 0)
    slots = HALF_CASTER_SLOTS.get(level, [0]*9)
    cap = max(1, (level // 2) + cha_mod)
    prepared = (char.spellcasting.get("paladin", {}).get("prepared", []) if isinstance(char.spellcasting, dict) else [])[:cap]
    return {
        "class": "paladin",
        "spellcasting_ability": "CHA",
        "spell_save_dc": 8 + pb + cha_mod,
        "spell_attack_mod": pb + cha_mod,
        "prepared_max": cap,
        "prepared_spells": prepared,
        "slots": slots,
    }


def _ranger_block(char: models.Character, mods: Dict[str,int], level: int, pb: int) -> Dict[str, Any]:
    wis_mod = mods.get("WIS", 0)
    slots = HALF_CASTER_SLOTS.get(level, [0]*9)
    cap = max(1, (level // 2) + wis_mod)
    prepared = (char.spellcasting.get("ranger", {}).get("prepared", []) if isinstance(char.spellcasting, dict) else [])[:cap]
    return {
        "class": "ranger",
        "spellcasting_ability": "WIS",
        "spell_save_dc": 8 + pb + wis_mod,
        "spell_attack_mod": pb + wis_mod,
        "prepared_max": cap,
        "prepared_spells": prepared,
        "slots": slots,
    }


def _warlock_block(char: models.Character, mods: Dict[str,int], level: int, pb: int) -> Dict[str, Any]:
    cha_mod = mods.get("CHA", 0)
    slots = PACT_MAGIC_SLOTS.get(level, [0]*9)
    max_known = WARLOCK_SPELLS_KNOWN.get(level, 0)
    known = (char.spellcasting.get("warlock", {}).get("known", []) if isinstance(char.spellcasting, dict) else [])[:max_known]
    return {
        "class": "warlock",
        "spellcasting_ability": "CHA",
        "spell_save_dc": 8 + pb + cha_mod,
        "spell_attack_mod": pb + cha_mod,
        "known_max": max_known,
        "known_spells": known,
        "slots": slots,
    }


SPELL_BLOCKS = {
    "bard": _bard_block,
    "cleric": _cleric_block,
    "druid": _druid_block,
    "paladin": _paladin_block,
    "ranger": _ranger_block,
    "sorcerer": _sorcerer_block,
    "warlock": _warlock_block,
    "wizard": _wizard_block,
}


def _class_block(char: models.Character, mods: Dict[str, int]) -> Optional[Dict[str, Any]]:
    cls = (char.class_ or "").lower()
    data = CLASSES.get(cls)
    if not data:
        return None
    level = int(char.level)
    con_mod = mods.get("CON", 0)
    hd = int(data.get("hit_die", 0))
    avg = (hd // 2) + 1
    hp = hd + con_mod
    if level > 1:
        hp += (level - 1) * (avg + con_mod)
    features: List[str] = []
    for L in range(1, level + 1):
        features.extend(data.get("features", {}).get(L, []))
    st_prof = {a: (a in data.get("saving_throws", [])) for a in ABILS}
    return {
        "hit_points": hp,
        "hit_dice": f"{level}d{hd}",
        "class_features": features,
        "saving_throw_proficiencies": st_prof,
    }

class FiveEStockModule(ModuleBase):
    def __init__(self, manifest: Dict[str, Any]):
        # Automatically pull in any subsystem folders declared in the manifest
        # (items, feats, spells, etc.) so the module can extend itself without
        # being a monolithic single file.
        if "__manifest_dir__" not in manifest:
            manifest["__manifest_dir__"] = Path(__file__).resolve().parent
        # Include common subsystems by default so that the module is usable
        # without loading the full manifest.  This keeps existing tests that
        # instantiate the module with only an ``id`` working while still
        # enabling companion templates.
        manifest.setdefault("subsystems", ["feats", "companions"])
        super().__init__(manifest)
        # build quick lookup tables for feats
        self.feats: Dict[str, Dict[str, Any]] = {}
        for mod in self.subsystems.get("feats", []):
            for ft in getattr(mod, "FEATS", []) or []:
                name = str(ft.get("name", "")).lower()
                if name:
                    self.feats[name] = ft

        # load companion templates if any are provided by subsystems
        self.companions: Dict[str, Dict[str, Any]] = {}
        for mod in self.subsystems.get("companions", []):
            for name, data in getattr(mod, "COMPANIONS", {}).items():
                self.companions[str(name).lower()] = data

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
        # feat prerequisites
        for ft in getattr(char, "feats", []) or []:
            data = self.feats.get(str(ft.name).lower())
            if not data:
                continue
            prereq = data.get("prerequisites", {}) or {}
            abil_req = prereq.get("ability_scores", {}) or {}
            for abil, req in abil_req.items():
                score = getattr(char.abilities.get(abil), "score", 0)
                if int(score) < int(req):
                    issues.append(f"Feat {ft.name} requires {abil} {req}")
            abil_any = prereq.get("ability_scores_any", {}) or {}
            if abil_any:
                ok = False
                for abil, req in abil_any.items():
                    score = getattr(char.abilities.get(abil), "score", 0)
                    if int(score) >= int(req):
                        ok = True
                        break
                if not ok:
                    choices = ", ".join(f"{a} {r}" for a, r in abil_any.items())
                    issues.append(f"Feat {ft.name} requires one of: {choices}")
        return issues

    def derive(self, char: models.Character):
        scores = _get_scores(char)
        # apply feat modifiers
        skill_feat_profs: set[str] = set()
        save_feat_profs: set[str] = set()
        for ft in getattr(char, "feats", []) or []:
            data = self.feats.get(str(ft.name).lower(), {})
            props: Dict[str, Any] = {}
            props.update(data.get("props", {}) or {})
            props.update(getattr(ft, "props", {}) or {})
            for abil, bonus in (props.get("ability_bonuses") or {}).items():
                scores[abil] = scores.get(abil, 10) + int(bonus)
            for sk in props.get("skill_proficiencies", []) or []:
                skill_feat_profs.add(sk)
            for st in props.get("saving_throw_proficiencies", []) or []:
                save_feat_profs.add(st)

        amods = _mods(scores)
        pb = proficiency_bonus(int(char.level))
        class_info = _class_block(char, amods)
        st_prof = class_info.get("saving_throw_proficiencies", {}) if class_info else {}
        extra = getattr(getattr(char, "proficiencies", None), "saving_throws", {}) or {}
        for k, v in extra.items():
            if v:
                st_prof[k] = True
        for st in save_feat_profs:
            st_prof[st] = True
        saves = {k: amods.get(k,0) + (pb if st_prof.get(k, False) else 0) for k in ABILS}
        ac = _compute_ac(char, amods)
        # skill modifiers
        skill_names = {sk.name for sk in getattr(char, "skills", [])}
        skill_names.update(skill_feat_profs)
        skill_map = {sk["name"]: sk["ability"] for sk in SKILLS}
        skills_out = {
            name: amods.get(ability, 0) + (pb if name in skill_names else 0)
            for name, ability in skill_map.items()
        }
        out: Dict[str, Any] = {
            "proficiency_bonus": pb,
            "ability_mods": amods,
            "saving_throws": saves,
            "ac": ac,
            "saving_throw_proficiencies": st_prof,
            "skills": skills_out,
        }
        if class_info:
            out.update({k: v for k, v in class_info.items() if k != "saving_throw_proficiencies"})
        sc_data = getattr(char, "spellcasting", {}) or {}
        class_levels = sc_data.get("classes", {}) if isinstance(sc_data, dict) else {}
        if not class_levels and char.class_:
            class_levels = {str(char.class_).lower(): int(char.level)}

        blocks: List[Dict[str, Any]] = []
        slots = [0]*9
        pact_slots = [0]*9
        for cls, lvl in class_levels.items():
            fn = SPELL_BLOCKS.get(str(cls).lower())
            if not fn:
                continue
            block = fn(char, amods, int(lvl), pb)
            sl = block.pop("slots", [0]*9)
            if str(cls).lower() == "warlock":
                pact_slots = [max(pact_slots[i], sl[i]) for i in range(9)]
            else:
                for i in range(9):
                    slots[i] += sl[i]
            blocks.append(block)

        if blocks:
            sc_out: Dict[str, Any] = {
                "classes": blocks,
                "slots": {str(i+1): slots[i] for i in range(9)},
            }
            if any(pact_slots):
                sc_out["pact_slots"] = {str(i+1): pact_slots[i] for i in range(9) if pact_slots[i]}
            out["spellcasting"] = sc_out

        # derive stats for any companions and aggregate their bonuses
        comp_out: List[Dict[str, Any]] = []
        help_bonus = False
        shared_senses: List[str] = []
        for comp in getattr(char, "companions", []) or []:
            key = (comp.template or comp.name).lower()
            tpl = self.companions.get(key, {})
            scores_c: Dict[str, int] = {}
            for abil, val in (tpl.get("abilities") or {}).items():
                scores_c[abil] = int(val)
            for abil, obj in (comp.abilities or {}).items():
                scores_c[abil] = int(getattr(obj, "score", obj))
            cmods = _mods(scores_c)
            cblock: Dict[str, Any] = {"name": comp.name}
            if cmods:
                cblock["ability_mods"] = cmods
            for k in ("ac", "hit_points"):
                if k in tpl:
                    cblock[k] = tpl[k]
            bonuses: Dict[str, Any] = {}
            bonuses.update(tpl.get("bonuses", {}) or {})
            bonuses.update(getattr(comp, "bonuses", {}) or {})
            if bonuses:
                cblock["bonuses"] = bonuses
                if bonuses.get("help_action"):
                    help_bonus = True
                if bonuses.get("shared_senses"):
                    shared_senses.extend(bonuses.get("shared_senses", []))
            comp_out.append(cblock)
        if comp_out:
            out["companions"] = comp_out
        if help_bonus or shared_senses:
            bon = out.setdefault("bonuses", {})
            if help_bonus:
                bon["help_action"] = True
            if shared_senses:
                bon["shared_senses"] = sorted(set(shared_senses))
        return out
