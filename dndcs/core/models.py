"""Compatibility wrapper for the relocated core domain models."""

from dndcs_core.domain.models import *  # noqa: F401,F403

__all__ = [name for name in globals() if not name.startswith("_")]
