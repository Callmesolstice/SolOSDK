"""Notion client + page upsert. Logic lands in joint #2."""

from __future__ import annotations


def get_notion_client(token: str):
    """Initialize Notion client with API token. TODO: implement."""
    raise NotImplementedError


def upsert_page(
    notion_token: str, database_id: str, properties: dict
) -> dict:
    """Create or update a Notion page by dedup key. TODO(joint-2): implement."""
    raise NotImplementedError
