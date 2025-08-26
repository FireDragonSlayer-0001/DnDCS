from dndcs.core import models
from dndcs.modules.fivee_stock.module import FiveEStockModule


def test_armor_and_shield_ac(ability_scores):
    mod = FiveEStockModule({"id": "fivee_stock"})
    items = [
        models.Item(
            name="Studded Leather",
            props={"armor": {"base": 12, "category": "light", "dex_cap": None}},
        ),
        models.Item(name="Shield", props={"shield_bonus": 2}),
    ]
    char = models.Character(
        name="Rogue",
        level=1,
        module="fivee_stock",
        class_="rogue",
        abilities=ability_scores(DEX=16),
        items=items,
    )
    ac = mod.derive(char)["ac"]
    assert ac["value"] == 17
    assert ac["source"] == "armor(light)"


def test_mage_armor_ac(ability_scores):
    mod = FiveEStockModule({"id": "fivee_stock"})
    items = [models.Item(name="Mage Armor", props={"ac_base": 13})]
    char = models.Character(
        name="Sorcerer",
        level=3,
        module="fivee_stock",
        class_="sorcerer",
        abilities=ability_scores(DEX=16),
        items=items,
    )
    ac = mod.derive(char)["ac"]
    assert ac["value"] == 16
    assert ac["source"] == "mage_armor"
