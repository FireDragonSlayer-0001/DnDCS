# src/dndcs/core/registry.py
from __future__ import annotations

import os


def default_module_id() -> str:
    """Return the default module identifier.

    The value can be overridden via the ``DNDCS_DEFAULT_MODULE_ID`` environment
    variable; otherwise the built-in ``fivee_stock`` module is used.
    """
    return os.getenv("DNDCS_DEFAULT_MODULE_ID", "fivee_stock")
