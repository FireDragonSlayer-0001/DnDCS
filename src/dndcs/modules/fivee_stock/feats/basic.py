"""Basic Rules feats data for the stock module."""

FEATS = [
    {
        "name": "Actor",
        "description": "Skilled at mimicry and dramatics.",
        "prerequisites": {"ability_scores": {"CHA": 13}},
        "props": {"ability_bonuses": {"CHA": 1}},
    },
    {
        "name": "Athlete",
        "description": "You have undergone extensive physical training.",
        "prerequisites": {"ability_scores_any": {"STR": 13, "DEX": 13}},
        "props": {"ability_choices": {"abilities": ["STR", "DEX"], "amount": 1}},
    },
    {
        "name": "Heavily Armored",
        "description": "Gain proficiency with heavy armor.",
        "prerequisites": {"proficiencies": {"armor": ["medium"]}},
        "props": {"ability_bonuses": {"STR": 1}, "armor_proficiencies": ["heavy"]},
    },
    {
        "name": "Keen Mind",
        "description": "A mind that can track time, direction, and detail with uncanny precision.",
        "props": {"ability_bonuses": {"INT": 1}},
    },
    {
        "name": "Lightly Armored",
        "description": "Train to master the use of light armor.",
        "props": {"ability_choices": {"abilities": ["STR", "DEX"], "amount": 1}, "armor_proficiencies": ["light"]},
    },
    {
        "name": "Moderately Armored",
        "description": "Gain proficiency with medium armor and shields.",
        "prerequisites": {"proficiencies": {"armor": ["light"]}},
        "props": {
            "ability_choices": {"abilities": ["STR", "DEX"], "amount": 1},
            "armor_proficiencies": ["medium"],
            "shield_proficiency": True,
        },
    },
    {
        "name": "Resilient",
        "description": "Increase one ability score and gain proficiency in its saving throws.",
        "props": {
            "ability_choices": {"abilities": ["STR", "DEX", "CON", "INT", "WIS", "CHA"], "amount": 1},
            "saving_throw_choice": ["STR", "DEX", "CON", "INT", "WIS", "CHA"],
        },
    },
    {
        "name": "Skilled",
        "description": "Gain proficiency in any three skills of your choice.",
        "props": {"skill_choice_count": 3},
    },
    {
        "name": "Tough",
        "description": "Your hit point maximum increases by 2 per level.",
        "props": {"hp_per_level": 2},
    },
    {
        "name": "Weapon Master",
        "description": "Extensive training with a variety of weapons.",
        "props": {
            "ability_choices": {"abilities": ["STR", "DEX"], "amount": 1},
            "weapon_proficiency_count": 4,
        },
    },
]

