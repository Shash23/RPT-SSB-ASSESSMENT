#!/usr/bin/env bash
# Generate SSB data at higher scale factors
# Usage: ./generate_higher_sf.sh <scale_factor>
# Example: ./generate_higher_sf.sh 5

set -euo pipefail

if [ $# -lt 1 ]; then
    echo "Usage: $0 <scale_factor>"
    echo "Example: $0 5"
    exit 1
fi

SCALE_FACTOR=$1
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Check available space
AVAILABLE=$(df -BG / | tail -1 | awk '{print $4}' | sed 's/G//')
ESTIMATED_SIZE=$((SCALE_FACTOR * 600))  # MB, approximate

echo "=========================================="
echo "SSB Data Generation at Scale Factor $SCALE_FACTOR"
echo "=========================================="
echo "Available space: ${AVAILABLE}GB"
echo "Estimated data size: ~$((ESTIMATED_SIZE / 1024))GB"
echo ""

if [ $ESTIMATED_SIZE -gt $((AVAILABLE * 1024 * 80 / 100)) ]; then
    echo "WARNING: Estimated size may exceed available space!"
    read -p "Continue anyway? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Navigate to ssb-dbgen
SSB_DBGEN_DIR="${PROJECT_ROOT}/ssb-data/ssb-dbgen"
if [ ! -d "$SSB_DBGEN_DIR" ]; then
    echo "Error: ssb-dbgen not found at $SSB_DBGEN_DIR"
    echo "Please clone it first:"
    echo "  cd ssb-data && git clone https://github.com/eyalroz/ssb-dbgen"
    exit 1
fi

cd "$SSB_DBGEN_DIR/build"

# Check if dbgen exists
if [ ! -f "./dbgen" ]; then
    echo "dbgen not found. Building..."
    cmake ..
    make -j$(nproc)
fi

# Create output directory
OUTPUT_DIR="${PROJECT_ROOT}/ssb-data/sf${SCALE_FACTOR}"
mkdir -p "$OUTPUT_DIR"

echo ""
echo "Generating SSB data at scale factor $SCALE_FACTOR..."
echo "This may take several minutes..."
echo ""

# Generate data
./dbgen -s "$SCALE_FACTOR" -v

# Move files to output directory
echo ""
echo "Moving generated files to $OUTPUT_DIR..."
mv *.tbl "$OUTPUT_DIR/" 2>/dev/null || true

# Verify files
echo ""
echo "Generated files:"
ls -lh "$OUTPUT_DIR"/*.tbl 2>/dev/null | awk '{print "  " $9 ": " $5}'

TOTAL_SIZE=$(du -sh "$OUTPUT_DIR" | awk '{print $1}')
echo ""
echo "Total size: $TOTAL_SIZE"
echo "Data generation complete!"
echo ""
echo "Next steps:"
echo "  1. Update load_ssb.sql to use sf${SCALE_FACTOR} directory"
echo "  2. Load data: ./sql/load_ssb.sh"
echo "  3. Update run_experiments.py to use new database path"

