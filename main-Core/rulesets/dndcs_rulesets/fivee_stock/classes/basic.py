"""Basic Rules class data for the stock 5e module."""

CLASSES = {
    "barbarian": {
        "hit_die": 12,
        "saving_throws": ["STR", "CON"],
        "features": {
            1: ["Rage", "Unarmored Defense"],
            2: ["Reckless Attack", "Danger Sense"],
            3: ["Primal Path"],
        },
    },
    "bard": {
        "hit_die": 8,
        "saving_throws": ["DEX", "CHA"],
        "features": {
            1: ["Bardic Inspiration", "Spellcasting"],
            2: ["Jack of All Trades", "Song of Rest"],
            3: ["Bard College"],
        },
    },
    "cleric": {
        "hit_die": 8,
        "saving_throws": ["WIS", "CHA"],
        "features": {
            1: ["Spellcasting", "Divine Domain"],
            2: ["Channel Divinity (1/rest)"],
        },
    },
    "druid": {
        "hit_die": 8,
        "saving_throws": ["INT", "WIS"],
        "features": {
            1: ["Druidic", "Spellcasting"],
            2: ["Wild Shape"],
            3: ["Druid Circle"],
        },
    },
    "fighter": {
        "hit_die": 10,
        "saving_throws": ["STR", "CON"],
        "features": {
            1: ["Fighting Style", "Second Wind"],
            2: ["Action Surge"],
            3: ["Martial Archetype"],
            5: ["Extra Attack"],
        },
    },
    "monk": {
        "hit_die": 8,
        "saving_throws": ["STR", "DEX"],
        "features": {
            1: ["Martial Arts", "Unarmored Defense"],
            2: ["Ki", "Unarmored Movement"],
            3: ["Monastic Tradition"],
        },
    },
    "paladin": {
        "hit_die": 10,
        "saving_throws": ["WIS", "CHA"],
        "features": {
            1: ["Divine Sense", "Lay on Hands"],
            2: ["Fighting Style", "Spellcasting"],
            3: ["Divine Health", "Sacred Oath"],
        },
    },
    "ranger": {
        "hit_die": 10,
        "saving_throws": ["STR", "DEX"],
        "features": {
            1: ["Favored Enemy", "Natural Explorer"],
            2: ["Fighting Style", "Spellcasting"],
            3: ["Ranger Archetype"],
        },
    },
    "rogue": {
        "hit_die": 8,
        "saving_throws": ["DEX", "INT"],
        "features": {
            1: ["Expertise", "Sneak Attack", "Thieves' Cant"],
            2: ["Cunning Action"],
            3: ["Roguish Archetype"],
        },
    },
    "sorcerer": {
        "hit_die": 6,
        "saving_throws": ["CON", "CHA"],
        "features": {
            1: ["Spellcasting", "Sorcerous Origin"],
            2: ["Font of Magic"],
            3: ["Metamagic"],
        },
    },
    "warlock": {
        "hit_die": 8,
        "saving_throws": ["WIS", "CHA"],
        "features": {
            1: ["Otherworldly Patron", "Pact Magic"],
            2: ["Eldritch Invocations"],
            3: ["Pact Boon"],
        },
    },
    "wizard": {
        "hit_die": 6,
        "saving_throws": ["INT", "WIS"],
        "features": {
            1: ["Spellcasting", "Arcane Recovery"],
            3: ["Arcane Tradition"],
        },
    },
}
