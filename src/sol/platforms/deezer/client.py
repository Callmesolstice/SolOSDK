"""Deezer public search API — album-art fallback.

Spotify Dev Mode blocks per-track album art (/tracks = 403, and /playlists/{id}/items
returns track objects with empty album.images). Deezer's public search is free, needs
no auth, and returns high-res covers. get_session() handles 429 + Retry-After; Deezer
also signals quota via a 200 body with an `error` object, which we back off on once.
"""

from __future__ import annotations

import logging
import time

from sol.http import get_session

DEEZER_BASE = "https://api.deezer.com"

log = logging.getLogger(__name__)


def search_album_art(track_name: str, artist: str) -> str | None:
    """Return the best album cover URL for a track, or None if not found.

    Tries an exact field query (track + artist) first, then a loose query.
    """
    session = get_session()
    queries: list[str] = []
    if track_name and artist:
        queries.append(f'track:"{track_name}" artist:"{artist}"')
    if track_name:
        queries.append(f"{artist} {track_name}".strip())

    for query in queries:
        for _attempt in range(2):
            resp = session.get(
                f"{DEEZER_BASE}/search", params={"q": query, "limit": 1}, timeout=15
            )
            if not resp.ok:
                break
            body = resp.json()
            if body.get("error"):  # quota / rate signalled in a 200 body
                log.warning("Deezer error %s — backing off", body["error"])
                time.sleep(1.0)
                continue
            data = body.get("data") or []
            if data:
                album = data[0].get("album") or {}
                art = album.get("cover_xl") or album.get("cover_big") or album.get("cover_medium")
                if art:
                    return art
            break  # ok response, no match → try next query form
    return None
