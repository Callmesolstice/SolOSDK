# SolOSDK

Shared Python SDK for Sol OS actors, workers, and agents. Provides unified interfaces for Notion I/O, Spotify API access, authentication flows, and run logging.

## Installation

```bash
pip install solosdk
```

Or from git:

```bash
pip install git+https://github.com/callmesolstice/SolOSDK.git@main
```

## Quick Start

```python
import sol

print(sol.__version__)  # 0.1.0
```

## Modules

- **sol.auth** — OAuth2 and token refresh flows
- **sol.platforms.spotify** — Spotify API client
- **sol.notion** — Notion database I/O and page management
- **sol.config** — Constants and configuration (API endpoints, DB IDs, etc.)
- **sol.runs** — Run logging and observability
- **sol.http** — Shared HTTP session with retry/backoff

## Development

Clone and install locally:

```bash
git clone https://github.com/callmesolstice/SolOSDK.git
cd SolOSDK
pip install -e ".[test]"
pytest
```

## Credentials

SDK functions take credentials as arguments—never read `os.environ` directly. See `scripts/sync.py` for how to inject shell env vars into SDK calls.

Required environment variables (for script integration):
- `solifyid` — Spotify client ID
- `solifysec` — Spotify client secret
- `resolify` — Spotify refresh token

## License

MIT
