#!/usr/bin/env bash
# Generate storage/key_value_stores/default/INPUT.json from secrets.zsh.
# Run once before `apify run`. Re-run after cred rotation.
# INPUT.json is gitignored — never committed.
set -euo pipefail

SECRETS_FILE="${HOME}/.config/zsh/secrets.zsh"
INPUT_DIR="$(dirname "$0")/../storage/key_value_stores/default"
INPUT_FILE="${INPUT_DIR}/INPUT.json"

if [[ ! -f "$SECRETS_FILE" ]]; then
  echo "ERROR: secrets file not found: $SECRETS_FILE" >&2
  exit 1
fi

# Source just the 4 vars we need
# shellcheck disable=SC1090
source "$SECRETS_FILE"

: "${solifyid:?solifyid not set in $SECRETS_FILE}"
: "${solifysec:?solifysec not set in $SECRETS_FILE}"
: "${resolify:?resolify not set in $SECRETS_FILE}"
: "${solinotion:?solinotion not set in $SECRETS_FILE}"

mkdir -p "$INPUT_DIR"

# dry_run=true by default — set to false when ready to commit writes
cat > "$INPUT_FILE" <<JSON
{
  "solifyid": "${solifyid}",
  "solifysec": "${solifysec}",
  "resolify": "${resolify}",
  "solinotion": "${solinotion}",
  "dry_run": true,
  "update_songs": false
}
JSON

echo "Written: $INPUT_FILE (dry_run=true)"
echo "Set dry_run=false in that file when ready to commit writes."
