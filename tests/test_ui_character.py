import json
from pathlib import Path
from fastapi.testclient import TestClient
from dndcs.ui.server import create_app


def _load_test_character() -> dict:
    path = Path(__file__).parent / "data" / "wizard_l17.json"
    return json.loads(path.read_text())


def test_ui_can_derive_level17_wizard():
    app = create_app()
    client = TestClient(app)
    payload = _load_test_character()
    resp = client.post("/api/derive", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert "spellcasting" in data
    slots = data["spellcasting"]["slots"]
    assert slots["1"] == 4
    assert slots["9"] == 1
    block = data["spellcasting"]["classes"][0]
    assert block["class"] == "wizard"
    assert block["spell_save_dc"] == 19
    assert block["prepared_max"] == 22
    assert "wish" in block["prepared_spells"]
