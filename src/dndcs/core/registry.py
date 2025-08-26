# src/dndcs/core/registry.py
from __future__ import annotations

import os


def default_module_id() -> str:
    """Return the default module identifier.

    The value can be overridden via the ``DNDCS_DEFAULT_MODULE_ID`` environment
    variable; otherwise the built-in ``fivee_stock`` module is used.  Empty
    values are treated the same as if the variable was unset to avoid
    returning an empty string when the environment variable is present but has
    no content.
    """
    env_val = os.getenv("DNDCS_DEFAULT_MODULE_ID")
    return env_val or "fivee_stock"
