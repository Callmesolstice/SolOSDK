"""Notion client + page upsert. Logic lands in joint #2.

Sync write-lists (reminder — never write formulas/rollups/buttons):
  Songs: Track Name, Artist(s), Album, Duration (ms), Popularity,
         Spotify Track URI (dedup key), Release Date.
  Playlists: Playlist Name, Spotify Playlist ID (dedup key), Description,
             Follower Count, Last Synced.
             NEVER: Mode, Active, Sync Policy, Eviction Rule, Curator/Owner,
                    Max Length, or any rollup.
  Playlist Tracks: Name, Song (rel, limit 1), Playlist (rel), Position, Added Date.
                   NEVER: Is Seeded, Content Pieces, af:*, Is My Song, Label,
                          Content Count.
"""

from __future__ import annotations

from sol.exceptions import SolError
from sol.http import get_session

NOTION_VERSION = "2022-06-28"
NOTION_BASE = "https://api.notion.com/v1"


def _headers(notion_token: str) -> dict:
    return {
        "Authorization": f"Bearer {notion_token}",
        "Notion-Version": NOTION_VERSION,
        "Content-Type": "application/json",
    }


# ---------------------------------------------------------------------------
# Query helpers
# ---------------------------------------------------------------------------

def query_by_property(
    notion_token: str,
    database_id: str,
    property_name: str,
    value: str,
) -> list[dict]:
    """POST /v1/databases/{id}/query filtering property_name == value. Paginates fully."""
    session = get_session()
    headers = _headers(notion_token)
    url = f"{NOTION_BASE}/databases/{database_id}/query"
    pages: list[dict] = []
    payload: dict = {
        "filter": {
            "property": property_name,
            "rich_text": {"equals": value},
        }
    }

    while True:
        resp = session.post(url, headers=headers, json=payload)
        if not resp.ok:
            raise SolError(f"Notion query failed {resp.status_code}: {resp.text}")
        body = resp.json()
        pages.extend(body.get("results") or [])
        if not body.get("has_more"):
            break
        payload["start_cursor"] = body["next_cursor"]

    return pages


# ---------------------------------------------------------------------------
# Upsert
# ---------------------------------------------------------------------------

def upsert_page(
    notion_token: str,
    database_id: str,
    properties: dict,
    dedup_property: str,
    dedup_value: str,
    cover_url: str | None = None,
    icon: str | None = None,
) -> dict:
    """Look up dedup_property == dedup_value; PATCH if found, POST if not. Returns page dict."""
    session = get_session()
    headers = _headers(notion_token)

    matches = query_by_property(notion_token, database_id, dedup_property, dedup_value)

    extras: dict = {}
    if cover_url:
        extras["cover"] = {"type": "external", "external": {"url": cover_url}}
    if icon:
        extras["icon"] = {"type": "emoji", "emoji": icon}

    if matches:
        page_id = matches[0]["id"]
        payload = {"properties": properties, **extras}
        resp = session.patch(
            f"{NOTION_BASE}/pages/{page_id}", headers=headers, json=payload
        )
    else:
        payload = {
            "parent": {"database_id": database_id},
            "properties": properties,
            **extras,
        }
        resp = session.post(f"{NOTION_BASE}/pages", headers=headers, json=payload)

    if not resp.ok:
        raise SolError(f"Notion upsert failed {resp.status_code}: {resp.text}")
    return resp.json()


# ---------------------------------------------------------------------------
# Property-value builders (plain Python → Notion JSON)
# ---------------------------------------------------------------------------

def title(text: str) -> dict:
    return {"title": [{"text": {"content": text}}]}


def rich_text(text: str) -> dict:
    return {"rich_text": [{"text": {"content": text}}]}


def number(n: float | int | None) -> dict:
    return {"number": n}


def date(iso: str | None) -> dict:
    return {"date": {"start": iso} if iso else None}


def checkbox(b: bool) -> dict:
    return {"checkbox": b}


def select(name: str | None) -> dict:
    return {"select": {"name": name} if name else None}


def relation(page_ids: list[str]) -> dict:
    return {"relation": [{"id": pid} for pid in page_ids]}


def url(u: str | None) -> dict:
    return {"url": u}


def status(name: str) -> dict:
    return {"status": {"name": name}}


# ---------------------------------------------------------------------------
# General-purpose Notion API functions
# ---------------------------------------------------------------------------

def query_db(notion_token: str, database_id: str, filter_payload: dict) -> list[dict]:
    """Full paginated query with any Notion filter dict. Raises SolError on non-200."""
    session = get_session()
    headers = _headers(notion_token)
    endpoint = f"{NOTION_BASE}/databases/{database_id}/query"
    pages: list[dict] = []
    payload: dict = {"filter": filter_payload}
    while True:
        resp = session.post(endpoint, headers=headers, json=payload)
        if not resp.ok:
            raise SolError(f"Notion query failed {resp.status_code}: {resp.text}")
        body = resp.json()
        pages.extend(body.get("results") or [])
        if not body.get("has_more"):
            break
        payload = {"filter": filter_payload, "start_cursor": body["next_cursor"]}
    return pages


def create_page(notion_token: str, database_id: str, properties: dict, cover_url: str | None = None) -> str:
    """POST a new page. Returns page ID. Raises SolError on failure."""
    session = get_session()
    headers = _headers(notion_token)
    payload: dict = {"parent": {"database_id": database_id}, "properties": properties}
    if cover_url:
        payload["cover"] = {"type": "external", "external": {"url": cover_url}}
    resp = session.post(f"{NOTION_BASE}/pages", headers=headers, json=payload)
    if not resp.ok:
        raise SolError(f"Notion create failed {resp.status_code}: {resp.text}")
    return resp.json()["id"]


def update_page(
    notion_token: str,
    page_id: str,
    properties: dict,
    cover_url: str | None = None,
) -> bool:
    """PATCH an existing page. Returns True on success. Raises SolError on failure.

    When cover_url is set, also sets the page cover to an external image alongside
    properties. Default None leaves the body unchanged — existing callers unaffected.
    """
    session = get_session()
    headers = _headers(notion_token)
    payload: dict = {"properties": properties}
    if cover_url:
        payload["cover"] = {"type": "external", "external": {"url": cover_url}}
    resp = session.patch(
        f"{NOTION_BASE}/pages/{page_id}", headers=headers, json=payload
    )
    if not resp.ok:
        raise SolError(f"Notion update failed {resp.status_code}: {resp.text}")
    return True


# ---------------------------------------------------------------------------
# Stub (not in scope for joint #2)
# ---------------------------------------------------------------------------

def get_notion_client(token: str):
    """Initialize Notion client with API token. TODO: implement."""
    raise NotImplementedError
