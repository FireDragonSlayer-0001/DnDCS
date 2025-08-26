from __future__ import annotations

import logging
from pathlib import Path
from datetime import datetime
from typing import Optional

_LOG_FILE: Optional[Path] = None

def init_logging(log_dir: str | Path = "logs", console_level: int = logging.WARNING) -> Path:
    """Initialize application-wide logging.

    Creates a timestamped log file in ``log_dir`` and attaches handlers
    to the ``dndcs`` root logger. Further calls are ignored and simply
    return the path to the previously created log file.
    """
    global _LOG_FILE
    if _LOG_FILE is not None:
        return _LOG_FILE

    log_path = Path(log_dir)
    log_path.mkdir(parents=True, exist_ok=True)
    _LOG_FILE = log_path / f"dndcs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"

    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)

    file_handler = logging.FileHandler(_LOG_FILE, encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)
    fmt = logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s")
    file_handler.setFormatter(fmt)
    root_logger.addHandler(file_handler)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(console_level)
    console_handler.setFormatter(fmt)
    root_logger.addHandler(console_handler)

    for name in ("uvicorn", "uvicorn.error", "uvicorn.access"):
        logging.getLogger(name).handlers.clear()
        logging.getLogger(name).propagate = True

    logging.captureWarnings(True)
    return _LOG_FILE


def get_logger(name: str) -> logging.Logger:
    """Return a logger namespaced under ``dndcs``."""
    return logging.getLogger(f"dndcs.{name}")