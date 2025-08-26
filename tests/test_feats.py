

from dndcs.core import models
from dndcs.modules.fivee_stock.module import FiveEStockModule

def _abilities(**scores):
    abils = {}
    for name in ("STR","DEX","CON","INT","WIS","CHA"):
        abils[name] = models.AbilityScore(name=name, score=scores.get(name,10))
    return abils


def test_feat_ability_bonus():
    mod = FiveEStockModule({"id": "fivee_stock"})
    char = models.Character(
        name="Test", level=1, module="fivee_stock",
        abilities=_abilities(STR=15),
        feats=[models.Feat(name="Athlete", props={"ability_bonuses": {"STR":1}})],
    )
    out = mod.derive(char)
    assert out["ability_mods"]["STR"] == 3  # 15 +1 => 16 => +3


def test_feat_skill_proficiency():
    mod = FiveEStockModule({"id": "fivee_stock"})
    char = models.Character(
        name="Skill", level=1, module="fivee_stock",
        abilities=_abilities(),
        feats=[models.Feat(name="Skilled", props={"skill_proficiencies": ["Arcana", "Athletics", "Stealth"]})],
    )
    out = mod.derive(char)
    pb = out["proficiency_bonus"]
    assert out["skills"]["Arcana"] == pb
    assert out["skills"]["Athletics"] == pb
    assert out["skills"]["Stealth"] == pb


def test_feat_prereq_validation():
    mod = FiveEStockModule({"id": "fivee_stock"})
    char = models.Character(
        name="Bad", level=1, module="fivee_stock",
        abilities=_abilities(STR=10, DEX=10),
        feats=[models.Feat(name="Athlete")],
    )
    issues = mod.validate(char)
    assert any("Athlete" in msg for msg in issues)

