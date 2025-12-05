#!/usr/bin/env bash
# Clean up space on EC2 instance
# Removes build artifacts, old databases, and other temporary files

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

echo "=========================================="
echo "Space Cleanup Script"
echo "=========================================="
echo ""

# Check current space
echo "Current disk usage:"
df -h / | tail -1
echo ""

# Calculate space that can be freed
SPACE_TO_FREE=0

echo "Checking for cleanup opportunities..."
echo ""

# 1. Build artifacts in duckdb-rpt
if [ -d "${PROJECT_ROOT}/duckdb-rpt/rpt-src/build" ]; then
    BUILD_SIZE=$(du -sh "${PROJECT_ROOT}/duckdb-rpt/rpt-src/build" 2>/dev/null | awk '{print $1}')
    echo "  - DuckDB build directory: $BUILD_SIZE"
    echo "    (Can be rebuilt, but will take time)"
    read -p "    Remove build artifacts? (y/N) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "    Removing build artifacts (keeping duckdb binary)..."
        find "${PROJECT_ROOT}/duckdb-rpt/rpt-src/build" -type f \
            -name "*.o" -o -name "*.a" -o -name "CMakeFiles" -prune | \
            xargs rm -rf 2>/dev/null || true
        echo "    Done."
    fi
fi

# 2. Old test databases
if [ -f "${PROJECT_ROOT}/tpch.db" ]; then
    TPCH_SIZE=$(du -sh "${PROJECT_ROOT}/tpch.db" | awk '{print $1}')
    echo "  - TPC-H database: $TPCH_SIZE"
    read -p "    Remove TPC-H database? (y/N) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        rm -f "${PROJECT_ROOT}/tpch.db"
        echo "    Removed."
    fi
fi

# 3. Old SSB databases (keep current one)
if [ -d "${PROJECT_ROOT}/db" ]; then
    DB_SIZE=$(du -sh "${PROJECT_ROOT}/db" 2>/dev/null | awk '{print $1}')
    echo "  - Database directory: $DB_SIZE"
    read -p "    Remove old database files? (y/N) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        rm -f "${PROJECT_ROOT}/db"/*.duckdb 2>/dev/null || true
        echo "    Removed."
    fi
fi

# 4. SSB data generator build artifacts
if [ -d "${PROJECT_ROOT}/ssb-data/ssb-dbgen/build" ]; then
    DBGEN_BUILD_SIZE=$(du -sh "${PROJECT_ROOT}/ssb-data/ssb-dbgen/build" 2>/dev/null | awk '{print $1}')
    echo "  - SSB dbgen build: $DBGEN_BUILD_SIZE"
    read -p "    Remove dbgen build artifacts? (y/N) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        rm -rf "${PROJECT_ROOT}/ssb-data/ssb-dbgen/build"/*.o \
               "${PROJECT_ROOT}/ssb-data/ssb-dbgen/build/CMakeFiles" 2>/dev/null || true
        echo "    Removed (keeping dbgen binary)."
    fi
fi

# 5. Python cache
if [ -d "${PROJECT_ROOT}/runner/__pycache__" ]; then
    echo "  - Python cache files"
    read -p "    Remove Python cache? (y/N) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        find "${PROJECT_ROOT}" -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
        find "${PROJECT_ROOT}" -type f -name "*.pyc" -delete 2>/dev/null || true
        echo "    Removed."
    fi
fi

echo ""
echo "Final disk usage:"
df -h / | tail -1
echo ""
echo "Cleanup complete!"

