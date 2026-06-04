"""Spotify API configuration and constants."""

# API endpoints
API_BASE = "https://api.spotify.com/v1"
TOKEN_URL = "https://accounts.spotify.com/api/token"

# Playlist items endpoint limit
PLAYLIST_ITEMS_LIMIT = 100

# OAuth2 scopes
SCOPES = [
    "playlist-read-private",
    "playlist-read-collaborative",
    "playlist-modify-public",
    "playlist-modify-private",
    "ugc-image-upload",
]

# Injected credentials — names of shell environment variables that scripts/sync.py reads
ENV_CLIENT_ID = "solifyid"
ENV_CLIENT_SECRET = "solifysec"
ENV_REFRESH_TOKEN = "resolify"

# Notion Database IDs
SONGS_DB_ID = "72df16fe5ba641be8bf8f6cfc81a3445"
PLAYLISTS_DB_ID = "2becc40c1bb841d58ae2a7de9001f2d7"
PLAYLIST_TRACKS_DB_ID = "36bd18e459784bfda9aa7c8dc00115eb"
PLAYLIST_SNAPSHOTS_DB_ID = "af704e57d19e478881877a84aa360caf"

# Local audio features CSV directory (no live /audio-features — 403 in Dev Mode)
AUDIO_FEATURES_CSV_DIR = "~/Documents/Quick_Access/Claude docs/sol-cowork/projects/spotify_playlists/playlist export/"
