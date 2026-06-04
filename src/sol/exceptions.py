"""SolOSDK exception hierarchy."""

from __future__ import annotations


class SolError(Exception):
    """Base exception for all SolOSDK errors."""

    pass


class DedupGuardError(SolError):
    """Raised when a dedup check finds an empty existing-key set (67-duplicate lesson)."""

    pass
