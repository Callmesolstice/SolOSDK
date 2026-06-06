"""Utility functions and helpers."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone


def should_snapshot(published_date_str: str | None, last_snapshotted_str: str | None) -> bool:
    """Graduated snapshot schedule — slows down updates as posts age.

    Returns False after 90 days. Otherwise returns True based on post age:
    - < 3 days: every run
    - 3–7 days: every 6 h
    - 7–15 days: every 12 h
    - 15–26 days: every 24 h
    - 26–90 days: every week
    """
    if not published_date_str:
        return False
    now = datetime.now(timezone.utc)

    published = datetime.fromisoformat(published_date_str.replace("Z", "+00:00"))
    if published.tzinfo is None:
        published = published.replace(tzinfo=timezone.utc)

    age = now - published

    if age >= timedelta(days=90):
        return False

    if last_snapshotted_str:
        last = datetime.fromisoformat(last_snapshotted_str.replace("Z", "+00:00"))
        if last.tzinfo is None:
            last = last.replace(tzinfo=timezone.utc)
        since_last = now - last
    else:
        since_last = None

    if age < timedelta(days=3):
        return True
    elif age < timedelta(days=7):
        return since_last is None or since_last >= timedelta(hours=6)
    elif age < timedelta(days=15):
        return since_last is None or since_last >= timedelta(hours=12)
    elif age < timedelta(days=26):
        return since_last is None or since_last >= timedelta(hours=24)
    else:
        return since_last is None or since_last >= timedelta(weeks=1)
