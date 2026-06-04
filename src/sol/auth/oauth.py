"""Generic OAuth2 refresh-token flow."""

from __future__ import annotations


def refresh_access_token(
    client_id: str, client_secret: str, refresh_token: str, token_url: str
) -> dict:
    """Refresh OAuth2 access token using refresh token. TODO: implement."""
    raise NotImplementedError
