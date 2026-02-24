#!/usr/bin/env bash
# Shared bootstrap for ghost tools. Source this, don't execute it.

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[1]}")/../.." && pwd)"

# Load .env
if [ -f "$SCRIPT_DIR/.env" ]; then
    set -a; source "$SCRIPT_DIR/.env"; set +a
fi

: "${GHOST_URL:?GHOST_URL not set — add to .env or source ~/.env}"
: "${GHOST_ADMIN_API_KEY:?GHOST_ADMIN_API_KEY not set — add to .env or source ~/.env}"

PYTHON="python3"
CLIENT="${SCRIPT_DIR}/src/ghost_client.py"
