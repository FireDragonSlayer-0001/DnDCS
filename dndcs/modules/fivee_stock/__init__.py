"""Compatibility namespace pointing at the relocated fivee_stock ruleset."""

from __future__ import annotations

from importlib import import_module
from pathlib import Path
from typing import Any

_BASE_PATH = Path(__file__).resolve().parents[3] / "main-Core" / "rulesets" / "dndcs_rulesets" / "fivee_stock"

# Expose the new package location as the search path for submodules so that
# legacy imports (e.g. ``dndcs.modules.fivee_stock.classes``) continue to
# resolve without copying files back into ``src/dndcs``.
__path__ = [str(_BASE_PATH)]


def __getattr__(name: str) -> Any:
    """Dynamically proxy attribute access to the relocated package."""

    target = f"dndcs_rulesets.fivee_stock.{name}"
    try:
        module = import_module(target)
    except ModuleNotFoundError as exc:
        raise AttributeError(name) from exc
    return module


def __dir__() -> list[str]:
    return sorted({"__path__", "__getattr__"})
