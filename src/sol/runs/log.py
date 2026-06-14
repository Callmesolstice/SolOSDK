"""Run logging — writes a row to the ⚙️ Agent Run Log Notion DB.

Actual Notion DB schema (verified against the live DB):
  Run           title       "{actor} run — {YYYY-MM-DD} {h:mmam/pm}" (Phoenix time)
  Status        select      "Success" | "Partial" | "Failed"
  Completed at  date        ISO datetime (America/Phoenix, no DST)
  Digest        rich_text   human one-liner — never blank on a completed run
  Metrics       rich_text   JSON stats blob (truncated to 2000 chars)
  Errors        rich_text   error message, blank on success
  Pages Touched number      best-effort count of pages written this run (explicit 0)

Other columns (Trigger, Version, Notes, relations, Apollo-Money counts) are left
unset — they are optional and agent-specific.
"""

from __future__ import annotations

import json
import logging
from datetime import datetime, timedelta, timezone

from sol.config.sol_os import AGENT_RUN_LOG_DB_ID
from sol.exceptions import SolError
from sol.http import get_session
from sol.notion.core import NOTION_BASE, NOTION_VERSION, date, number, rich_text, select, title

log = logging.getLogger(__name__)

_PLACEHOLDER = "TODO_REPLACE_WITH_AGENT_RUN_LOG_DB_ID"

# America/Phoenix is UTC-7 year-round (no DST).
_PHOENIX_TZ = timezone(timedelta(hours=-7))

# Per-phase keys that represent a Notion write — summed into Pages Touched.
# Best-effort and harmless across actors (unknown keys simply don't match).
_WRITE_KEYS = frozenset({
    "renamed", "art_written", "written", "covers_set", "flagged", "coverage_hit",
    "songs_created", "songs_updated", "junction_created",
})


def _pages_touched(stats: dict | None) -> int:
    """Best-effort sum of write counts across per-phase stats sub-dicts."""
    if not stats:
        return 0
    total = 0
    for key, value in stats.items():
        if isinstance(value, dict):
            # Nested per-phase stats (sol-enrich): phase_x -> {write_key: n}
            for subkey, n in value.items():
                if subkey in _WRITE_KEYS and isinstance(n, (int, float)):
                    total += int(n)
        elif key in _WRITE_KEYS and isinstance(value, (int, float)):
            # Flat stats (sol-spotify): write_key -> n
            total += int(value)
    return total


def log_agent_run(
    notion_token: str,
    actor: str,
    started_at: datetime,
    dry_run: bool,
    stats: dict | None,
    error: str | None,
) -> None:
    """Write one row to the Agent Run Log Notion DB.

    Does NOT raise — on failure logs a warning so the caller's finally block
    can surface the original sync error unmasked.
    """
    if AGENT_RUN_LOG_DB_ID == _PLACEHOLDER:
        log.warning(
            "AGENT_RUN_LOG_DB_ID not set in sol/config/sol_os.py — skipping run log"
        )
        return

    now = datetime.now(timezone.utc)
    duration_s = (now - started_at).total_seconds()

    status = "Failed" if error else "Success"

    completed_phx = now.astimezone(_PHOENIX_TZ)
    run_title = f"{actor} run — {completed_phx.strftime('%Y-%m-%d %-I:%M%p').lower()}"
    stats_text = json.dumps(stats, default=str)[:2000] if stats else ""

    if error:
        digest = f"Run failed: {error[:300]}"
    else:
        phases = ", ".join(stats.keys()) if stats else "no phases"
        prefix = "Dry run — no writes" if dry_run else "Completed"
        digest = f"{prefix}: {phases} ({duration_s:.0f}s)"

    properties = {
        "Run": title(run_title),
        "Status": select(status),
        "Completed at": date(completed_phx.isoformat()),
        "Digest": rich_text(digest),
        "Metrics": rich_text(stats_text),
        "Errors": rich_text(error or ""),
        "Pages Touched": number(0 if dry_run else _pages_touched(stats)),
    }

    session = get_session()
    headers = {
        "Authorization": f"Bearer {notion_token}",
        "Notion-Version": NOTION_VERSION,
        "Content-Type": "application/json",
    }
    payload = {
        "parent": {"database_id": AGENT_RUN_LOG_DB_ID},
        "properties": properties,
    }
    resp = session.post(f"{NOTION_BASE}/pages", headers=headers, json=payload, timeout=30)
    if not resp.ok:
        raise SolError(f"Agent Run Log write failed {resp.status_code}: {resp.text}")
    log.info("Agent Run Log row written: %s [%s] %.1fs", run_title, status, duration_s)
