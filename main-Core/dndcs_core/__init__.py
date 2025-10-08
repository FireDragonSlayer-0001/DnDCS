"""Core engine package for DnDCS.

This package hosts the authoritative implementations for the core domain
models and supporting services.  The public ``dndcs`` package re-exports
these modules to preserve the original import paths while allowing the
repository layout to follow the feature-first structure mandated in
``AGENTS.md``.
"""

from . import domain, services

__all__ = ["domain", "services"]
