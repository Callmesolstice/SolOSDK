# SolOSDK

Shared Python library for Sol OS actors and workers. Not an application — installed as a dependency by each actor so they all call the same code instead of copying it.

## What it does

Provides the core building blocks used across every Solasis Broadcasting actor:

- **Notion layer** — query, create, and update pages with full pagination and retry. Property builder helpers for every type the actors use.
- **HTTP** — shared session with exponential backoff and retry on 429/5xx.
- **Spotify client** — token refresh, playlist fetch, playlist items fetch.
- **Run logging** — writes a row to the Agent Run Log DB after each actor run.
- **Snapshot scheduling** — graduated staleness logic (slow down snapshots as posts age).
- **Exceptions** — `SolError` base class, `DedupGuardError` for the dedup guard pattern.

## How it fits

```
SolOSDK (this repo)
├── installed by → sol-spotify
├── installed by → sol-ig
└── installed by → sol-pin
```

SolOSDK is a pure library. It has no entry point, no actor scaffolding, and no credentials of its own. Actors inject config and call SDK functions.

## Module map

```
src/sol/
├── notion/
│   └── core.py        query_db, create_page, update_page, upsert_page, property builders
├── platforms/
│   └── spotify/
│       └── client.py  get_current_user_playlists, get_playlist_items
├── auth/
│   └── spotify.py     refresh_spotify_token
├── runs/
│   └── log.py         log_agent_run
├── config/
│   ├── spotify.py     env var names, Notion DB IDs for Spotify
│   └── sol_os.py      Agent Run Log DB ID
├── utils.py           should_snapshot
├── http.py            get_session
└── exceptions.py      SolError, DedupGuardError
```

## Installing in an actor

Add to the actor's `requirements.txt`:

```
git+https://github.com/callmesolstice/SolOSDK.git@main
```

Pin to a commit hash once stable:

```
git+https://github.com/callmesolstice/SolOSDK.git@<commit-hash>
```

## Key patterns

**Notion queries** — all filtered, paginated:
```python
from sol.notion.core import query_db, create_page, update_page

pages = query_db(notion_token, db_id, {"property": "Stage", "status": {"equals": "Posted"}})
page_id = create_page(notion_token, db_id, {"Title": title("My page")})
update_page(notion_token, page_id, {"Stage": status("Done")})
```

**Property builders:**
```python
from sol.notion.core import title, rich_text, number, date, select, status, url, relation, checkbox
```

**Dedup guard** — abort if a pre-fetch scan errors on an already-populated DB:
```python
from sol.exceptions import DedupGuardError

# Raises DedupGuardError instead of silently returning empty
# Prevents the 67-duplicate incident pattern (empty index → writes all as new)
```

**Run log** — called in `finally` so it fires on success or crash:
```python
from sol.runs.log import log_agent_run

log_agent_run(notion_token, actor="my-actor", started_at=started_at, dry_run=dry_run, stats=stats, error=error)
```

## Development

No build step. Edit in place. The actors install from `@main` so any pushed change is live on next actor build.

```bash
cd ~/code_projects/SolOSDK
# make changes
git add -A && git commit -m "..." && git push
# then rebuild any actors that need the change
```
