import pytest
from dndcs.core import models

ABILITIES = ("STR", "DEX", "CON", "INT", "WIS", "CHA")


def _abilities_factory(**scores):
    return {name: models.AbilityScore(name=name, score=scores.get(name, 10)) for name in ABILITIES}


@pytest.fixture
def ability_scores():
    return _abilities_factory


CLASS_NAMES = [
    "barbarian",
    "bard",
    "cleric",
    "druid",
    "fighter",
    "monk",
    "paladin",
    "ranger",
    "rogue",
    "sorcerer",
    "warlock",
    "wizard",
]

LEVEL_TIERS = [1, 5, 11, 17]


@pytest.fixture(params=CLASS_NAMES)
def class_name(request):
    return request.param


@pytest.fixture(params=LEVEL_TIERS)
def level(request):
    return request.param


@pytest.fixture
def character(class_name, level, ability_scores):
    items = []
    if class_name == "wizard":
        items.append(
            models.Item(name="Spellbook", props={"spellbook": {"prepared": {}}})
        )
    return models.Character(
        name=f"{class_name}-{level}",
        level=level,
        module="fivee_stock",
        class_=class_name,
        abilities=ability_scores(),
        items=items,
    )
