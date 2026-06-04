"""Notion database query and filter helpers."""

from __future__ import annotations


def query_database(
    notion_token: str, database_id: str, filter: dict | None = None
) -> list[dict]:
    """Query Notion database with optional filters. TODO: implement."""
    raise NotImplementedError


def get_page(notion_token: str, page_id: str) -> dict:
    """Retrieve a single Notion page by ID. TODO: implement."""
    raise NotImplementedError
