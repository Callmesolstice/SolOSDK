"""Local entry point: reads shell env, injects creds into sol module."""

from __future__ import annotations

import os

from sol.config.spotify import (
    ENV_CLIENT_ID,
    ENV_CLIENT_SECRET,
    ENV_REFRESH_TOKEN,
)


def sync() -> None:
    """Read Spotify creds from shell env and inject into sol. TODO: implement."""
    client_id = os.environ.get(ENV_CLIENT_ID)
    client_secret = os.environ.get(ENV_CLIENT_SECRET)
    refresh_token = os.environ.get(ENV_REFRESH_TOKEN)

    if not all([client_id, client_secret, refresh_token]):
        raise ValueError("Missing Spotify creds in shell env")

    # TODO: pass creds to sol functions
    raise NotImplementedError


if __name__ == "__main__":
    sync()
