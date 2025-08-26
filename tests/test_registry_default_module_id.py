from dndcs.core import registry


def test_default_module_id_env_var(monkeypatch):
    # When env variable set to value, return that value
    monkeypatch.setenv("DNDCS_DEFAULT_MODULE_ID", "custom_mod")
    assert registry.default_module_id() == "custom_mod"


def test_default_module_id_empty(monkeypatch):
    # Empty environment variable should fall back to default
    monkeypatch.setenv("DNDCS_DEFAULT_MODULE_ID", "")
    assert registry.default_module_id() == "fivee_stock"


def test_default_module_id_unset(monkeypatch):
    # When environment variable not set at all, default is used
    monkeypatch.delenv("DNDCS_DEFAULT_MODULE_ID", raising=False)
    assert registry.default_module_id() == "fivee_stock"

