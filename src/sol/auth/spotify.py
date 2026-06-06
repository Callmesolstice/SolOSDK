"""Spotify token refresh with injected credentials."""

from __future__ import annotations

from sol.config.spotify import TOKEN_URL
from sol.exceptions import SolError
from sol.http import get_session


def refresh_spotify_token(
    client_id: str, client_secret: str, refresh_token: str
) -> str:
    """POST to Spotify token endpoint with Basic auth; return the access_token string.

    Args are injected — never reads os.environ.
    Raises SolError on non-200.
    """
    resp = get_session().post(
        TOKEN_URL,
        data={"grant_type": "refresh_token", "refresh_token": refresh_token},
        auth=(client_id, client_secret),
    )
    if not resp.ok:
        raise SolError(f"Spotify token refresh failed {resp.status_code}: {resp.text}")
    return resp.json()["access_token"]
