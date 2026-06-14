"""Spotify API client (playlists, items, tracks). Logic = joint-2.

Sync write-lists (reminder):
  Songs: Track Name, Artist(s), Album, Duration (ms), Popularity,
         Spotify Track URI (dedup key), Release Date.
  Playlists: Playlist Name, Spotify Playlist ID (dedup key), Description,
             Follower Count, Last Synced.
  Playlist Tracks: Name, Song (rel), Playlist (rel), Position, Added Date.
"""

from __future__ import annotations

import logging

from sol.config.spotify import API_BASE
from sol.http import get_session

log = logging.getLogger(__name__)


def get_current_user_playlists(access_token: str) -> list[dict]:
    """GET /me/playlists — paginate via offset until next is None. Return all playlist dicts."""
    session = get_session()
    headers = {"Authorization": f"Bearer {access_token}"}
    items: list[dict] = []
    url = f"{API_BASE}/me/playlists"
    params: dict = {"limit": 50, "offset": 0}

    while url:
        resp = session.get(url, headers=headers, params=params)
        resp.raise_for_status()
        body = resp.json()
        items.extend(body.get("items") or [])
        url = body.get("next")  # Spotify returns full next URL or null
        params = {}             # next URL already has params baked in

    return items


def get_playlist_items(access_token: str, playlist_id: str) -> list[dict]:
    """GET /playlists/{id}/items — paginate until next is None. Return all item dicts.

    Each item: {added_at, track: {...}}. On 403 (not owner/collaborator) returns [].
    Uses /items endpoint — NOT /tracks (deprecated Feb 2026).
    """
    session = get_session()
    headers = {"Authorization": f"Bearer {access_token}"}
    items: list[dict] = []
    url = f"{API_BASE}/playlists/{playlist_id}/items"
    params: dict = {"limit": 100}

    while url:
        resp = session.get(url, headers=headers, params=params)
        if resp.status_code == 403:
            log.warning("Skipping playlist %s — 403 (not owner/collaborator)", playlist_id)
            return []
        resp.raise_for_status()
        body = resp.json()
        items.extend(body.get("items") or [])
        url = body.get("next")
        params = {}

    return items


def get_playlists(spotify_token: str, limit: int = 50) -> list[dict]:
    """Retrieve user's playlists. TODO: implement."""
    raise NotImplementedError


def get_tracks(access_token: str, track_ids: list[str]) -> list[dict]:
    """GET /tracks?ids=... in chunks of 50 — return one flat list of track dicts.

    Each track dict has `uri` and `album.images` (list of {url, height, width}).
    Raises on non-200.
    """
    session = get_session()
    headers = {"Authorization": f"Bearer {access_token}"}
    tracks: list[dict] = []

    for start in range(0, len(track_ids), 50):
        chunk = track_ids[start : start + 50]
        resp = session.get(
            f"{API_BASE}/tracks", headers=headers, params={"ids": ",".join(chunk)}
        )
        resp.raise_for_status()
        tracks.extend(resp.json().get("tracks") or [])

    return tracks


def get_playlist_images(access_token: str, playlist_id: str) -> list[dict]:
    """GET /playlists/{id}?fields=images — return images list.

    On 403 (not owner/collaborator) returns []. Raises on other non-200.
    """
    session = get_session()
    headers = {"Authorization": f"Bearer {access_token}"}
    resp = session.get(
        f"{API_BASE}/playlists/{playlist_id}", headers=headers, params={"fields": "images"}
    )
    if resp.status_code == 403:
        log.warning("Skipping playlist %s images — 403 (not owner/collaborator)", playlist_id)
        return []
    resp.raise_for_status()
    return resp.json().get("images") or []
