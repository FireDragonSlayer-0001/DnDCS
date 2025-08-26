from dndcs.core import models
from dndcs.modules.fivee_stock.module import FiveEStockModule


def _abilities(**scores):
    abils = {}
    for name in ("STR","DEX","CON","INT","WIS","CHA"):
        abils[name] = models.AbilityScore(name=name, score=scores.get(name,10))
    return abils


def test_half_caster_slots():
    mod = FiveEStockModule({"id":"fivee_stock"})
    char = models.Character(
        name="Pally", level=4, module="fivee_stock", class_="paladin",
        abilities=_abilities(CHA=14),
    )
    out = mod.derive(char)
    sc = out["spellcasting"]
    assert sc["slots"]["1"] == 3
    pal = sc["classes"][0]
    assert pal["class"] == "paladin"
    assert pal["prepared_max"] == (4//2) + 2  # half level + CHA mod


def test_multiclass_slots_merge():
    mod = FiveEStockModule({"id":"fivee_stock"})
    char = models.Character(
        name="Mix", level=5, module="fivee_stock", class_="paladin",
        abilities=_abilities(INT=16, CHA=12),
        items=[models.Item(name="Spellbook", props={"spellbook": {"prepared": {}}})],
        spellcasting={
            "classes": {"wizard":3, "paladin":2},
            "wizard": {"prepared": []},
            "paladin": {"prepared": []},
        },
    )
    out = mod.derive(char)
    sc = out["spellcasting"]
    assert sc["slots"]["1"] == 6
    assert sc["slots"]["2"] == 2
    names = {blk["class"] for blk in sc["classes"]}
    assert names == {"wizard", "paladin"}


def test_warlock_pact_slots():
    mod = FiveEStockModule({"id":"fivee_stock"})
    char = models.Character(
        name="Lock", level=5, module="fivee_stock", class_="warlock",
        abilities=_abilities(CHA=16),
        spellcasting={"classes": {"warlock":5}},
    )
    out = mod.derive(char)
    sc = out["spellcasting"]
    assert sc["pact_slots"]["3"] == 2
    war = sc["classes"][0]
    assert war["known_max"] == 6  # from WARLOCK_SPELLS_KNOWN
