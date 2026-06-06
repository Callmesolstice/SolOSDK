"""Smoke tests: import sol and verify core module behaviour."""

import sol
from sol.http import get_session
import requests


def test_import():
    """Verify sol package imports and version is set."""
    assert sol.__version__ == "0.1.0"


def test_get_session_returns_session():
    """get_session() must return a configured requests.Session (no network)."""
    s = get_session()
    assert isinstance(s, requests.Session)


def test_remaining_stubs_still_raise():
    """Stubs not yet implemented still raise NotImplementedError."""
    import pytest
    from sol.platforms.spotify.client import get_playlists, get_tracks
    from sol.notion.core import get_notion_client

    with pytest.raises(NotImplementedError):
        get_playlists("tok")
    with pytest.raises(NotImplementedError):
        get_tracks("tok", [])
    with pytest.raises(NotImplementedError):
        get_notion_client("tok")
