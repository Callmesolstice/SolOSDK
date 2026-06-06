"""Throwaway — archives ALL rows in the Playlist Tracks junction DB.

Does NOT touch Songs or Playlists.

Usage:
    python scripts/reset_junction.py
"""

from __future__ import annotations

import os
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

from sol.http import get_session

JUNCTION_DB_ID = "36bd18e459784bfda9aa7c8dc00115eb"
NOTION_BASE = "https://api.notion.com/v1"
NOTION_VERSION = "2022-06-28"
WORKERS = 4


def _headers(token: str) -> dict:
    return {
        "Authorization": f"Bearer {token}",
        "Notion-Version": NOTION_VERSION,
        "Content-Type": "application/json",
    }


def collect_page_ids(token: str) -> list[str]:
    session = get_session()
    headers = _headers(token)
    url = f"{NOTION_BASE}/databases/{JUNCTION_DB_ID}/query"
    page_ids: list[str] = []
    payload: dict = {"page_size": 100}

    while True:
        resp = session.post(url, headers=headers, json=payload, timeout=60)
        resp.raise_for_status()
        body = resp.json()
        page_ids.extend(p["id"] for p in body.get("results", []))
        if not body.get("has_more"):
            break
        payload = {"page_size": 100, "start_cursor": body["next_cursor"]}
        print(f"  collected {len(page_ids)} ids...", end="\r")

    return page_ids


def archive_page(token: str, page_id: str) -> None:
    import random
    import time
    time.sleep(random.uniform(0.1, 0.4))  # jitter to spread load across rate-limit window
    session = get_session()
    resp = session.patch(
        f"{NOTION_BASE}/pages/{page_id}",
        headers=_headers(token),
        json={"archived": True},
        timeout=60,
    )
    resp.raise_for_status()


def main() -> None:
    token = os.environ.get("solinotion")
    if not token:
        sys.exit("Missing env var: solinotion")

    print("Collecting junction page IDs...")
    page_ids = collect_page_ids(token)
    total = len(page_ids)
    print(f"Found {total} rows. Archiving with {WORKERS} workers...")

    archived = 0
    errors = 0
    lock = threading.Lock()

    # Heartbeat: prints every 15s so you can tell alive vs frozen
    stop_heartbeat = threading.Event()
    def _heartbeat():
        while not stop_heartbeat.wait(15):
            with lock:
                a = archived
            print(f"  [heartbeat] archived {a}/{total} — still running {time.strftime('%H:%M:%S')}")
    threading.Thread(target=_heartbeat, daemon=True).start()

    with ThreadPoolExecutor(max_workers=WORKERS) as pool:
        futures = {pool.submit(archive_page, token, pid): pid for pid in page_ids}
        for fut in as_completed(futures):
            try:
                fut.result()
                with lock:
                    archived += 1
                    if archived % 200 == 0 or archived == total:
                        print(f"  archived {archived}/{total}")
            except Exception as exc:
                with lock:
                    errors += 1
                print(f"  ERROR {futures[fut]}: {exc}")

    stop_heartbeat.set()
    print(f"\nDone. Archived: {archived}  Errors: {errors}")


if __name__ == "__main__":
    main()
