"""Cloudflare KV token store (Worker-era)."""

from __future__ import annotations


def get_token(key: str) -> str:
    """Retrieve token from Cloudflare KV store. TODO: implement."""
    raise NotImplementedError


def set_token(key: str, value: str) -> None:
    """Store token in Cloudflare KV store. TODO: implement."""
    raise NotImplementedError
