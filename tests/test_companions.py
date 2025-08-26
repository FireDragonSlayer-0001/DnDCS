from dndcs.core import models
from dndcs.modules.fivee_stock.module import FiveEStockModule


def _abilities(**scores):
    abils = {}
    for name in ("STR","DEX","CON","INT","WIS","CHA"):
        abils[name] = models.AbilityScore(name=name, score=scores.get(name,10))
    return abils


def test_familiar_help_and_senses():
    mod = FiveEStockModule({"id": "fivee_stock"})
    char = models.Character(
        name="Mage",
        level=1,
        module="fivee_stock",
        abilities=_abilities(),
        companions=[models.Companion(name="Owl", template="owl")],
    )
    out = mod.derive(char)
    assert out["bonuses"]["help_action"] is True
    assert "darkvision" in out["bonuses"]["shared_senses"]
    comp = out["companions"][0]
    assert comp["ability_mods"]["DEX"] == 2
