from dndcs.core import loader
from dndcs.core.module_base import ModuleBase


def test_load_module_by_manifest_id(tmp_path, monkeypatch):
    mod_dir = tmp_path / "mymod"
    mod_dir.mkdir()
    (mod_dir / "manifest.yaml").write_text("id: mymod\nentry_point: module.py:MyModule\n")
    (mod_dir / "module.py").write_text(
        "from dndcs.core.module_base import ModuleBase\n"
        "class MyModule(ModuleBase):\n"
        "    pass\n"
    )
    monkeypatch.setenv("DNDCS_MODULE_PATH", str(tmp_path))
    mod = loader.load_module_by_manifest_id("mymod")
    assert mod is not None
    assert isinstance(mod, ModuleBase)
    assert mod.manifest["id"] == "mymod"
