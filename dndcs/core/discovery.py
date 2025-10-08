"""Compatibility wrapper for the relocated module discovery utilities."""

from dndcs_core.services.discovery import *  # noqa: F401,F403

__all__ = [name for name in globals() if not name.startswith("_")]
