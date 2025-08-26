from dndcs.core import models
from dndcs.modules.fivee_stock.module import FiveEStockModule, FULL_CASTER_SLOTS


def test_wizard_spell_slot_progression(level, ability_scores):
    mod = FiveEStockModule({"id": "fivee_stock"})
    char = models.Character(
        name="Wiz",
        level=level,
        module="fivee_stock",
        class_="wizard",
        abilities=ability_scores(INT=16),
        items=[models.Item(name="Spellbook", props={"spellbook": {"prepared": {}}})],
    )
    out = mod.derive(char)
    slots = out["spellcasting"]["slots"]
    expected = {str(i + 1): FULL_CASTER_SLOTS[level][i] for i in range(9)}
    assert slots == expected
