"""ReccoBeats audio-features client.

Source of audio features now that live Spotify /audio-features = 403 in Dev Mode.
No auth required. get_session() already handles 429 + Retry-After via urllib3.

NOTE on the endpoint: the per-track route GET /v1/track/{id}/audio-features requires
a ReccoBeats UUID and 404s on a Spotify ID. The BATCH route
GET /v1/audio-features?ids={spotify_ids} accepts Spotify IDs directly (max 40 per
call) and returns each result with an `href` (https://open.spotify.com/track/{id})
that maps back to the Spotify ID. We use the batch route.
"""

from __future__ import annotations

import time

from sol.http import get_session

RECCOBEATS_BASE = "https://api.reccobeats.com/v1"

# ReccoBeats accepts at most 40 ids per audio-features request (41+ → HTTP 400).
RECCOBEATS_BATCH = 40
# Undocumented rate limit — pause between batch calls.
RECCOBEATS_SLEEP = 0.5

# Maps ReccoBeats response keys → Notion af: property names
AF_MAP = {
    "acousticness":     "af: Acousticness",
    "danceability":     "af: Danceability",
    "energy":           "af: Energy",
    "instrumentalness": "af: Instrumentalness",
    "liveness":         "af: Liveness",
    "loudness":         "af: Loudness",
    "speechiness":      "af: Speechiness",
    "tempo":            "af: Tempo",
    "valence":          "af: Valence",
}
# af: Key and af: Mode are NOT mapped here — ReccoBeats returns key/mode but the
# Notion schema models them differently (Mode is a select); leave those fields untouched.


def _spotify_id_from_href(href: str | None) -> str | None:
    if not href or "/track/" not in href:
        return None
    return href.rsplit("/track/", 1)[-1]


def get_audio_features(spotify_ids: list[str]) -> dict[str, dict]:
    """Batch-fetch audio features by Spotify track ID.

    Returns {spotify_id: feature_dict}. IDs not in ReccoBeats' catalog are simply
    absent from the result. Chunks of 40, with a 0.5s pause between calls.
    Raises on non-200.
    """
    session = get_session()
    out: dict[str, dict] = {}
    for start in range(0, len(spotify_ids), RECCOBEATS_BATCH):
        chunk = spotify_ids[start : start + RECCOBEATS_BATCH]
        resp = session.get(
            f"{RECCOBEATS_BASE}/audio-features",
            params={"ids": ",".join(chunk)},
            timeout=20,
        )
        resp.raise_for_status()
        for feat in resp.json().get("content") or []:
            sid = _spotify_id_from_href(feat.get("href"))
            if sid:
                out[sid] = feat
        time.sleep(RECCOBEATS_SLEEP)
    return out
