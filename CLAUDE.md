# SolOSDK — Project Spec

## Project: SolOSDK — shared Python SDK for all Sol OS actors. import name sol, src/ layout.

## HARD CONSTRAINTS:
  * Injected creds: SDK functions take client_id / client_secret / refresh_token / notion token
    as ARGUMENTS. NEVER read os.environ inside sol. Only scripts/sync.py reads the shell env
    (solifyid / solifysec / resolify) and passes them in. (This makes local<->Worker a wrapper swap.)
  * Spotify: use /playlists/{id}/items, NOT /tracks (deprecated Feb 2026).
  * Dedup by Spotify Track URI; Notion does not enforce uniqueness. If the existing-URI set comes
    back empty, ABORT — raise DedupGuardError (the 67-duplicate lesson).
  * No live audio features (/audio-features = 403 in Dev Mode). Features come from local CSVs by URI.
  * Playlist Tracks junction — sync WRITES only: Name, Song (rel, limit 1), Playlist (rel),
    Position (number), Added Date (date). NEVER write Is Seeded, Content Pieces, or any
    af:* / Is My Song / Label / Content Count (formulas + rollups, read-only).

## MODULE MAP:
  * notion/ = Notion I/O
  * platforms/<p>/ = per-platform API clients
  * auth/ = token flows
  * runs/ = run logging
  * config/ = constants & IDs
  * http.py = shared session

## FILL ORDER (later joints):
  exceptions -> config -> http -> auth -> platforms -> notion -> runs.
