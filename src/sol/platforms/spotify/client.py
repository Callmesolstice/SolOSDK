"""Spotify API client (playlists, items, tracks). Logic = joint-2."""

from __future__ import annotations


def get_playlists(spotify_token: str, limit: int = 50) -> list[dict]:
    """Retrieve user's playlists. TODO: implement."""
    raise NotImplementedError


def get_playlist_items(
    spotify_token: str, playlist_id: str, limit: int = 100
) -> list[dict]:
    """Retrieve items in a playlist using GET /playlists/{id}/items (NOT /tracks). TODO: implement."""
    raise NotImplementedError


def get_tracks(spotify_token: str, track_ids: list[str]) -> list[dict]:
    """Retrieve track details by IDs. TODO: implement."""
    raise NotImplementedError
