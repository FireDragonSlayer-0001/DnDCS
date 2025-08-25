from __future__ import annotations
from pathlib import Path
import threading, time, webbrowser, os
from typing import Dict, Any
from fastapi import FastAPI, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
import uvicorn

from dndcs.core import models
from dndcs.core import registry

def _static_dir() -> Path:
    return Path(__file__).resolve().parent / "static"

def _safe_join(base: Path, rel: str) -> Path:
    # prevent path traversal for assets
    p = (base / rel).resolve()
    if os.path.commonpath([p, base.resolve()]) != str(base.resolve()):
        raise HTTPException(status_code=400, detail="Invalid asset path")
    return p

def create_app() -> FastAPI:
    app = FastAPI(title="DnDCS UI", version="0.2.0")

    @app.get("/api/modules")
    def api_modules():
        mods = []
        for man in registry.discover_modules():
            entry = {
                "id": man.get("id"),
                "name": man.get("name"),
                "version": man.get("version"),
                "description": man.get("description", ""),
            }
            icon_rel = man.get("icon")
            if icon_rel:
                entry["icon"] = f"/mods/{man['id']}/assets/{icon_rel.split('assets/')[-1]}"
            mods.append(entry)
        return {"modules": mods}

    @app.get("/mods/{module_id}/assets/{path:path}")
    def serve_asset(module_id: str, path: str):
        for man in registry.discover_modules():
            if man.get("id") == module_id:
                base = Path(man["__manifest_dir__"]) / "assets"
                if not base.exists():
                    raise HTTPException(status_code=404, detail="No assets for module")
                file_path = _safe_join(base, path)
                if not file_path.exists():
                    raise HTTPException(status_code=404, detail="Asset not found")
                return FileResponse(file_path)
        raise HTTPException(status_code=404, detail="Module not found")

    @app.post("/api/new_character")
    async def api_new_character(req: Request):
        data = await req.json()
        module_id = data.get("module_id")
        if not module_id:
            raise HTTPException(status_code=400, detail="module_id required")
        mod = registry.load_module_by_manifest_id(module_id)
        if mod is None:
            raise HTTPException(status_code=404, detail=f"Module '{module_id}' not found")
        char = models.Character(
            name=data.get("name", "New Hero"),
            module=module_id,
            abilities={k: models.AbilityScore(name=k, score=v) for k, v in mod.template_abilities().items()},
            skills=[models.Skill(name=s["name"], ability=s["ability"]) for s in mod.template_skills()],
            items=[], feats=[],
        )
        return JSONResponse(char.model_dump())

    @app.post("/api/derive")
    async def api_derive(req: Request):
        payload = await req.json()
        try:
            char = models.Character.model_validate(payload)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Invalid character: {e}")
        mod = registry.load_module_by_manifest_id(char.module)
        if mod is None:
            raise HTTPException(status_code=404, detail=f"Module '{char.module}' not found")
        d = mod.derive(char)
        return JSONResponse(d.model_dump())

    @app.post("/api/validate")
    async def api_validate(req: Request):
        payload = await req.json()
        try:
            char = models.Character.model_validate(payload)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Invalid character: {e}")
        mod = registry.load_module_by_manifest_id(char.module)
        if mod is None:
            raise HTTPException(status_code=404, detail=f"Module '{char.module}' not found")
        issues = mod.validate(char)
        return {"issues": issues}

    # Mount static LAST so /api/* routes work
    app.mount("/", StaticFiles(directory=_static_dir(), html=True), name="static")
    return app
    
def serve(host: str = "127.0.0.1", port: int = 8000, open_browser: bool = True) -> None:
    app = create_app()
    if open_browser:
        def _open():
            time.sleep(0.6)
            webbrowser.open(f"http://{host}:{port}/")
        threading.Thread(target=_open, daemon=True).start()
    uvicorn.run(app, host=host, port=port, log_level="info")
