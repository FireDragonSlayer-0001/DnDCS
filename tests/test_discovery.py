from pathlib import Path

from dndcs.core import discovery


def test_discover_modules_reads_manifest(tmp_path):
    mod_dir = tmp_path / "mymod"
    mod_dir.mkdir()
    (mod_dir / "manifest.yaml").write_text("id: mymod\nentry_point: module.py:Cls\n")
    mods = discovery.discover_modules(modules_dir=tmp_path)
    assert len(mods) == 1
    man = mods[0]
    assert man["id"] == "mymod"
    assert man["__manifest_dir__"] == str(mod_dir)
    assert man["__root__"] == str(tmp_path)


def test_module_search_paths_dedup(monkeypatch, tmp_path):
    monkeypatch.setenv("DNDCS_MODULE_PATH", str(tmp_path))
    paths = discovery.module_search_paths(extra=[tmp_path])
    resolved = [p.resolve() for p in paths]
    assert resolved.count(tmp_path.resolve()) == 1
