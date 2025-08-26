import json
from fastapi.testclient import TestClient
from dndcs.ui.server import create_app


def test_ui_spell_search_by_module():
    app = create_app()
    client = TestClient(app)
    resp = client.get("/api/spells", params={"module": "fivee_stock", "name": "Aid"})
    assert resp.status_code == 200
    data = resp.json()
    assert any(sp["name"] == "Aid" for sp in data.get("spells", []))
    resp = client.get("/api/spells", params={"module": "fivee_stock", "cls": "wizard"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["spells"]
    assert all("wizard" in sp.get("classes", []) for sp in data["spells"])
