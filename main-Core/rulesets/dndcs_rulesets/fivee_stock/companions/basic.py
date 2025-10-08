"""Default companion templates for the stock 5e module.

This intentionally only covers a handful of common options used in tests.
"""

COMPANIONS = {
    # A simple owl familiar from the Find Familiar spell.
    "owl": {
        "abilities": {"STR": 3, "DEX": 15, "CON": 8, "INT": 2, "WIS": 12, "CHA": 7},
        "ac": 11,
        "hit_points": 1,
        # help_action allows the companion to use the Help action in combat.
        # shared_senses represents the familiar's ability to share senses with the
        # summoner as per the Find Familiar spell.
        "bonuses": {
            "help_action": True,
            "shared_senses": ["darkvision", "hearing", "sight"],
        },
    },
    # A basic wolf used by the ranger's Beast Master archetype.
    "wolf": {
        "abilities": {"STR": 12, "DEX": 15, "CON": 12, "INT": 3, "WIS": 12, "CHA": 6},
        "ac": 13,
        "hit_points": 11,
        "bonuses": {
            "help_action": True,
        },
    },
}
