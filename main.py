"""Apify Actor entry point — Spotify→Notion playlist sync.

Reads 4 creds from Actor Input (isSecret=true, stored as Apify secrets).
All sync logic lives in scripts/sync.py::run_sync — nothing is duplicated here.
"""

from __future__ import annotations

import asyncio
import logging
import sys
from datetime import datetime, timezone
from pathlib import Path

# Make sol/ and scripts/ importable without installing in the container.
# Dockerfile also runs `pip install src/` so this is a belt-and-suspenders guard.
_root = Path(__file__).parent
sys.path.insert(0, str(_root / "src"))
sys.path.insert(0, str(_root / "scripts"))

from apify import Actor  # noqa: E402 — must follow sys.path setup

from sync import run_sync  # scripts/sync.py  # noqa: E402
from sol.exceptions import DedupGuardError, SolError  # noqa: E402
from sol.runs.log import log_agent_run  # noqa: E402

ACTOR_NAME = "solos-spotify-notion-sync"

logging.basicConfig(level=logging.INFO, format="%(levelname)s  %(message)s")
log = logging.getLogger(__name__)


async def main() -> None:
    async with Actor:
        inp = await Actor.get_input() or {}

        client_id: str | None = inp.get("solifyid")
        client_secret: str | None = inp.get("solifysec")
        refresh_token: str | None = inp.get("resolify")
        notion_token: str | None = inp.get("solinotion")

        missing = [
            name
            for name, val in [
                ("solifyid", client_id),
                ("solifysec", client_secret),
                ("resolify", refresh_token),
                ("solinotion", notion_token),
            ]
            if not val
        ]
        if missing:
            raise ValueError(f"Missing required input fields: {', '.join(missing)}")

        dry_run: bool = bool(inp.get("dry_run", True))
        update_songs: bool = bool(inp.get("update_songs", False))

        started_at = datetime.now(timezone.utc)
        stats: dict | None = None
        error: str | None = None

        try:
            stats = run_sync(
                client_id=client_id,  # type: ignore[arg-type]
                client_secret=client_secret,  # type: ignore[arg-type]
                refresh_token=refresh_token,  # type: ignore[arg-type]
                notion_token=notion_token,  # type: ignore[arg-type]
                dry_run=dry_run,
                update_songs=update_songs,
            )
            await Actor.push_data({"stats": stats, "dry_run": dry_run})
        except (DedupGuardError, SolError, Exception) as exc:
            error = str(exc)
            log.error("Sync failed: %s", exc)
            raise
        finally:
            if notion_token:
                try:
                    log_agent_run(
                        notion_token=notion_token,
                        actor=ACTOR_NAME,
                        started_at=started_at,
                        dry_run=dry_run,
                        stats=stats,
                        error=error,
                    )
                except Exception as log_exc:
                    # Log but don't mask the original sync error
                    log.error("log_agent_run failed (non-fatal): %s", log_exc)


if __name__ == "__main__":
    asyncio.run(main())
