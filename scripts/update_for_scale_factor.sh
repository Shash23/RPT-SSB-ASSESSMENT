#!/usr/bin/env bash
# Update scripts to use a different scale factor
# Usage: ./update_for_scale_factor.sh <scale_factor>
# Example: ./update_for_scale_factor.sh 3

set -euo pipefail

if [ $# -lt 1 ]; then
    echo "Usage: $0 <scale_factor>"
    echo "Example: $0 3"
    exit 1
fi

SCALE_FACTOR=$1
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

echo "Updating scripts for scale factor $SCALE_FACTOR..."

# Update load_ssb.sql
LOAD_SQL="${PROJECT_ROOT}/sql/load_ssb.sql"
if [ -f "$LOAD_SQL" ]; then
    # Backup original
    cp "$LOAD_SQL" "${LOAD_SQL}.bak"
    
    # Replace sf1 with sf${SCALE_FACTOR}
    sed -i "s|sf1/|sf${SCALE_FACTOR}/|g" "$LOAD_SQL"
    sed -i "s|sf1'|sf${SCALE_FACTOR}'|g" "$LOAD_SQL"
    
    echo "  ✓ Updated $LOAD_SQL"
    echo "    (Backup saved as ${LOAD_SQL}.bak)"
fi

# Update run_experiments.py if it has hardcoded paths
RUN_SCRIPT="${PROJECT_ROOT}/runner/run_experiments.py"
if [ -f "$RUN_SCRIPT" ]; then
    # Check if it references sf1
    if grep -q "sf1" "$RUN_SCRIPT" 2>/dev/null; then
        cp "$RUN_SCRIPT" "${RUN_SCRIPT}.bak"
        sed -i "s|sf1|sf${SCALE_FACTOR}|g" "$RUN_SCRIPT"
        echo "  ✓ Updated $RUN_SCRIPT"
    fi
fi

# Update run_all_experiments.sh if needed
RUN_ALL="${PROJECT_ROOT}/runner/run_all_experiments.sh"
if [ -f "$RUN_ALL" ]; then
    if grep -q "sf1\|ssb.db" "$RUN_ALL" 2>/dev/null; then
        # Check what needs updating
        echo "  ℹ Check $RUN_ALL for database paths"
    fi
fi

echo ""
echo "Update complete!"
echo ""
echo "Next steps:"
echo "  1. Verify data exists: ls -lh ssb-data/sf${SCALE_FACTOR}/*.tbl"
echo "  2. Load data: ./sql/load_ssb.sh"
echo "  3. Run experiments: cd runner && ./run_all_experiments.sh"

