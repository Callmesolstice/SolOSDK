"""Smoke tests: import sol and verify stubs."""

import pytest

import sol


def test_import():
    """Verify sol package imports and version is set."""
    assert sol.__version__ == "0.1.0"


def test_notimplemented_stubs():
    """Verify stub modules raise NotImplementedError."""
    from sol.notion.core import upsert_page

    with pytest.raises(NotImplementedError):
        upsert_page("", "", {})
