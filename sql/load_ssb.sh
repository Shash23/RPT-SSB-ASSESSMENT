#!/usr/bin/env bash
# Helper script to load SSB data with correct absolute paths
# Usage: ./sql/load_ssb.sh [path/to/ssb.duckdb]

set -euo pipefail

# Get the project root directory (parent of sql/)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

DB_PATH="${1:-$PROJECT_ROOT/db/ssb.duckdb}"

# Create db directory if it doesn't exist
mkdir -p "$(dirname "$DB_PATH")"

# Generate temporary SQL file with correct paths
TMP_SQL=$(mktemp)
sed "s|PROJECT_ROOT_PLACEHOLDER|$PROJECT_ROOT|g" "$SCRIPT_DIR/load_ssb.sql" > "$TMP_SQL"

echo "Loading SSB data into $DB_PATH"
echo "Project root: $PROJECT_ROOT"

# Check if duckdb is in PATH or use common locations
if command -v duckdb &> /dev/null; then
    DUCKDB_BIN="duckdb"
elif [ -f "$PROJECT_ROOT/../duckdb-baseline/build/debug/duckdb" ]; then
    DUCKDB_BIN="$PROJECT_ROOT/../duckdb-baseline/build/debug/duckdb"
elif [ -f "$PROJECT_ROOT/../duckdb-rpt/build/debug/duckdb" ]; then
    DUCKDB_BIN="$PROJECT_ROOT/../duckdb-rpt/build/debug/duckdb"
else
    echo "Error: duckdb executable not found. Please specify with DUCKDB_BIN env var."
    exit 1
fi

"$DUCKDB_BIN" "$DB_PATH" < "$TMP_SQL"

rm "$TMP_SQL"
echo "Done loading SSB data."

