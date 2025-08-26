from dndcs.core import models
from dndcs.modules.fivee_stock.module import FiveEStockModule


def test_item_ability_bonus_and_save_proficiency(ability_scores):
    mod = FiveEStockModule({"id": "fivee_stock"})
    items = [
        models.Item(
            name="Belt of Strength",
            props={
                "ability_bonuses": {"STR": 2},
                "saving_throw_proficiencies": ["STR"],
            },
        )
    ]
    char = models.Character(
        name="Hero",
        level=1,
        module="fivee_stock",
        class_="cleric",
        abilities=ability_scores(),
        items=items,
    )
    out = mod.derive(char)
    pb = out["proficiency_bonus"]
    assert out["ability_mods"]["STR"] == 1
    assert out["saving_throw_proficiencies"]["STR"]
    assert out["saving_throws"]["STR"] == 1 + pb


def test_item_all_save_bonus(ability_scores):
    mod = FiveEStockModule({"id": "fivee_stock"})
    cloak = models.Item(name="Cloak of Protection", props={"saving_throw_bonuses": {"all": 1}})
    char = models.Character(
        name="Fighter",
        level=1,
        module="fivee_stock",
        class_="fighter",
        abilities=ability_scores(),
        items=[cloak],
    )
    out = mod.derive(char)
    pb = out["proficiency_bonus"]
    assert out["saving_throws"]["STR"] == out["ability_mods"]["STR"] + pb + 1
    assert out["saving_throws"]["DEX"] == out["ability_mods"]["DEX"] + 1
    assert out["saving_throw_bonuses"]["all"] == 1
