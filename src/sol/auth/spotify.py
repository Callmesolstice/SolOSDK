"""Spotify token refresh with injected credentials."""

from __future__ import annotations


def refresh_spotify_token(
    client_id: str, client_secret: str, refresh_token: str
) -> dict:
    """Refresh Spotify access token. Uses sol.config.spotify.TOKEN_URL and SCOPES. TODO: implement."""
    raise NotImplementedError
