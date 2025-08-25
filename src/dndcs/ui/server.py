from __future__ import annotations
from pathlib import Path
import threading, time, webbrowser
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
import uvicorn

def _static_dir() -> Path:
    return Path(__file__).resolve().parent / "static"

def create_app() -> FastAPI:
    app = FastAPI(title="DnDCS UI", version="0.1.0")
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
