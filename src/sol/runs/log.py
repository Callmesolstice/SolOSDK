"""Run logging — writes a row to the Agent Run Log Notion DB.

Expected Notion DB schema (Agent Run Log):
  Name          title       "{actor} | {YYYY-MM-DD HH:MM UTC}"
  Actor         rich_text   actor name string
  Status        select      "success" | "error" | "dry_run"
  Started At    date        ISO datetime
  Duration (s)  number      elapsed seconds (float)
  Stats         rich_text   JSON summary (truncated to 2000 chars)
  Error         rich_text   error message, empty on success
"""

from __future__ import annotations

import json
import logging
from datetime import datetime, timezone

from sol.config.sol_os import AGENT_RUN_LOG_DB_ID
from sol.exceptions import SolError
from sol.http import get_session
from sol.notion.core import NOTION_BASE, NOTION_VERSION, date, number, rich_text, select, title

log = logging.getLogger(__name__)

_PLACEHOLDER = "TODO_REPLACE_WITH_AGENT_RUN_LOG_DB_ID"


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

    if error:
        status = "error"
    elif dry_run:
        status = "dry_run"
    else:
        status = "success"

    name_val = f"{actor} | {started_at.strftime('%Y-%m-%d %H:%M UTC')}"
    stats_text = json.dumps(stats, default=str)[:2000] if stats else ""

    properties = {
        "Name": title(name_val),
        "Actor": rich_text(actor),
        "Status": select(status),
        "Started At": date(started_at.isoformat()),
        "Duration (s)": number(round(duration_s, 1)),
        "Stats": rich_text(stats_text),
        "Error": rich_text(error or ""),
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
    log.info("Agent Run Log row written: %s [%s] %.1fs", name_val, status, duration_s)
