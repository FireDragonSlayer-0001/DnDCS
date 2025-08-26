from dndcs.modules.fivee_stock.module import FiveEStockModule
from dndcs.modules.fivee_stock.classes.basic import CLASSES


def test_class_features_progression(character, class_name, level):
    mod = FiveEStockModule({"id": "fivee_stock"})
    out = mod.derive(character)
    feats = out.get("class_features", [])
    expected = []
    for lvl, names in CLASSES[class_name]["features"].items():
        if lvl <= level:
            expected.extend(names)
    for feat in expected:
        assert feat in feats
