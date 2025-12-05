#!/bin/bash
# Cleanup and consolidate repository - keep only essential files

set -e

PROJECT_ROOT="/home/ubuntu/RPT-SSB-ASSESSMENT"
cd "$PROJECT_ROOT"

echo "=========================================="
echo "Repository Cleanup Script"
echo "=========================================="
echo ""

# Create backup directory for files we're removing
BACKUP_DIR="${PROJECT_ROOT}/.cleanup_backup_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"
echo "Backup directory: $BACKUP_DIR"
echo ""

# 1. Remove log files
echo "1. Removing log files..."
mkdir -p "$BACKUP_DIR/logs"
mv -f experiment_run.log experiment_run_background.log "$BACKUP_DIR/logs/" 2>/dev/null || true
echo "   ✓ Removed log files"

# 2. Remove temporary files
echo "2. Removing temporary files..."
mkdir -p "$BACKUP_DIR/temp"
mv -f apache-arrow-apt-source-latest-jammy.deb "$BACKUP_DIR/temp/" 2>/dev/null || true
echo "   ✓ Removed temporary files"

# 3. Remove old/unused database files (keep only sf5 and sf10)
echo "3. Cleaning up database files..."
mkdir -p "$BACKUP_DIR/databases"
if [ -f "duckdb-rpt/ssb.db" ]; then
    mv -f duckdb-rpt/ssb.db "$BACKUP_DIR/databases/" 2>/dev/null || true
    echo "   ✓ Removed old ssb.db (keeping sf5 and sf10)"
fi

# 4. Remove backup SQL files
echo "4. Removing backup SQL files..."
mkdir -p "$BACKUP_DIR/sql_backups"
mv -f sql/load_ssb.sql.bak "$BACKUP_DIR/sql_backups/" 2>/dev/null || true
echo "   ✓ Removed backup SQL files"

# 5. Remove unused SQL files
echo "5. Removing unused SQL files..."
mv -f load_tpch.sql "$BACKUP_DIR/sql_backups/" 2>/dev/null || true
echo "   ✓ Removed unused SQL files"

# 6. Consolidate SF=1 results into results/sf1/ directory (preserve all scale factors)
echo "6. Consolidating results..."
# Create sf1 directory if it doesn't exist
mkdir -p results/sf1

# Move SF=1 results from root to sf1/ directory
if [ -f "results/ssb_baseline.csv" ]; then
    mv -f results/ssb_baseline.csv results/sf1/ 2>/dev/null || true
    echo "   ✓ Moved SF=1 ssb_baseline.csv to results/sf1/"
fi
if [ -f "results/ssb_rpt.csv" ]; then
    mv -f results/ssb_rpt.csv results/sf1/ 2>/dev/null || true
    echo "   ✓ Moved SF=1 ssb_rpt.csv to results/sf1/"
fi
if [ -f "results/memory_baseline.csv" ]; then
    mv -f results/memory_baseline.csv results/sf1/ 2>/dev/null || true
    echo "   ✓ Moved SF=1 memory_baseline.csv to results/sf1/"
fi
if [ -f "results/memory_rpt.csv" ]; then
    mv -f results/memory_rpt.csv results/sf1/ 2>/dev/null || true
    echo "   ✓ Moved SF=1 memory_rpt.csv to results/sf1/"
fi
if [ -f "results/join_sizes_baseline.csv" ]; then
    mv -f results/join_sizes_baseline.csv results/sf1/ 2>/dev/null || true
    echo "   ✓ Moved SF=1 join_sizes_baseline.csv to results/sf1/"
fi
if [ -f "results/join_sizes_rpt.csv" ]; then
    mv -f results/join_sizes_rpt.csv results/sf1/ 2>/dev/null || true
    echo "   ✓ Moved SF=1 join_sizes_rpt.csv to results/sf1/"
fi
# Move test files to backup
if [ -f "results/memory_test.csv" ]; then
    mkdir -p "$BACKUP_DIR/old_results"
    mv -f results/memory_test.csv "$BACKUP_DIR/old_results/" 2>/dev/null || true
fi

# Move SF=1 graphs to results/graphs/sf1/ directory
if [ -d "results/graphs" ] && [ ! -d "results/graphs/sf1" ]; then
    mkdir -p results/graphs/sf1
    # Only move PNG files that are not already in sf5 or sf10 subdirectories
    for png_file in results/graphs/*.png; do
        if [ -f "$png_file" ]; then
            mv -f "$png_file" results/graphs/sf1/ 2>/dev/null || true
        fi
    done
    echo "   ✓ Moved SF=1 graphs to results/graphs/sf1/"
fi

echo "   ✓ Consolidated results (preserved SF=1, SF=5, and SF=10)"

# 7. Remove unused documentation
echo "7. Removing unused documentation..."
mkdir -p "$BACKUP_DIR/docs"
mv -f CHATGPT_EC2_SUMMARY.md SF10_SPACE_REQUIREMENTS.md GIT_SETUP.md "$BACKUP_DIR/docs/" 2>/dev/null || true
echo "   ✓ Removed unused documentation"

# 8. Remove empty db directory
echo "8. Cleaning up empty directories..."
if [ -d "db" ] && [ -z "$(ls -A db 2>/dev/null | grep -v '^\.gitkeep$')" ]; then
    rm -rf db
    echo "   ✓ Removed empty db directory"
fi

# 9. Remove unused scripts
echo "9. Cleaning up unused scripts..."
mkdir -p "$BACKUP_DIR/scripts"
if [ -f "sql/load_ssb.sh" ]; then
    mv -f sql/load_ssb.sh "$BACKUP_DIR/scripts/" 2>/dev/null || true
fi
echo "   ✓ Cleaned up unused scripts"

# 10. Remove build artifacts from duckdb-rpt (can be regenerated)
echo "10. Removing build artifacts (can be regenerated)..."
if [ -d "duckdb-rpt/rpt-src/build" ]; then
    BUILD_SIZE=$(du -sh duckdb-rpt/rpt-src/build | cut -f1)
    echo "   Build directory size: $BUILD_SIZE"
    read -p "   Remove build directory? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        rm -rf duckdb-rpt/rpt-src/build
        echo "   ✓ Removed build directory"
    else
        echo "   ⏭ Skipped build directory removal"
    fi
fi

# 11. Remove Python cache files
echo "11. Removing Python cache files..."
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find . -type f -name "*.pyc" -delete 2>/dev/null || true
echo "   ✓ Removed Python cache files"

# 12. Create consolidated README
echo "12. Creating consolidated documentation..."
cat > REPOSITORY_STRUCTURE.md << 'EOF'
# Repository Structure

This repository contains the RPT (Robust Predicate Transfer) evaluation on the Star Schema Benchmark (SSB).

## Directory Structure

```
RPT-SSB-ASSESSMENT/
├── README.md                          # Main project README
├── EXPERIMENT_GUIDE.md                # Guide for running experiments
├── SCALING_UP_GUIDE.md                # Guide for scaling to higher SF
├── REPOSITORY_STRUCTURE.md            # This file
│
├── runner/                            # Experiment execution scripts
│   ├── run_all_experiments.sh         # Main experiment orchestrator
│   ├── run_all_scale_factors.sh       # Multi-SF experiment runner
│   ├── run_experiments.py             # Query execution script
│   ├── measure_join_sizes.py          # Join size measurement
│   ├── measure_memory.py              # Memory utilization measurement
│   ├── analyze_results.py             # Results analysis
│   ├── create_graphs.py               # Graph generation (SF=1)
│   └── create_graphs_for_scale_factor.py  # Graph generation (SF=5,10)
│
├── scripts/                           # Utility scripts
│   ├── generate_higher_sf.sh          # Generate SSB data for higher SF
│   ├── cleanup_space.sh               # Clean up disk space
│   └── update_for_scale_factor.sh     # Update SQL for scale factor
│
├── sql/                               # SQL scripts
│   └── load_ssb.sql                   # SSB schema and data loading
│
├── results/                           # Experiment results
│   ├── sf1/                           # SF=1 results
│   │   ├── ssb_baseline.csv
│   │   ├── ssb_rpt.csv
│   │   ├── memory_baseline.csv
│   │   ├── memory_rpt.csv
│   │   ├── join_sizes_baseline.csv
│   │   └── join_sizes_rpt.csv
│   ├── sf5/                           # SF=5 results
│   │   ├── ssb_baseline.csv
│   │   ├── ssb_rpt.csv
│   │   ├── memory_baseline.csv
│   │   ├── memory_rpt.csv
│   │   ├── join_sizes_baseline.csv
│   │   └── join_sizes_rpt.csv
│   ├── sf10/                          # SF=10 results
│   │   ├── ssb_baseline.csv
│   │   ├── ssb_rpt.csv
│   │   ├── memory_baseline.csv
│   │   ├── memory_rpt.csv
│   │   ├── join_sizes_baseline.csv
│   │   └── join_sizes_rpt.csv
│   └── graphs/                        # Visualization graphs
│       ├── sf1/                       # SF=1 graphs
│       │   ├── performance_comparison.png
│       │   ├── speedup_comparison.png
│       │   ├── memory_comparison.png
│       │   ├── join_size_comparison.png
│       │   └── summary_comparison.png
│       ├── sf5/                       # SF=5 graphs
│       │   ├── performance_comparison.png
│       │   ├── speedup_comparison.png
│       │   ├── memory_comparison.png
│       │   ├── join_size_comparison.png
│       │   └── summary_comparison.png
│       └── sf10/                      # SF=10 graphs
│           ├── performance_comparison.png
│           ├── speedup_comparison.png
│           ├── memory_comparison.png
│           ├── join_size_comparison.png
│           └── summary_comparison.png
│
├── presentation_outline.md            # Presentation outline
├── presentation_script.md             # Full presentation script
├── presentation_future_work_script.md # Future work section
│
├── duckdb-rpt/                        # RPT-enabled DuckDB fork
│   ├── rpt-src/                       # Source code (from EmbryoLabs)
│   │   ├── src/include/duckdb/optimizer/predicate_transfer/setting.hpp
│   │   └── ...                        # Full DuckDB source
│   ├── ssb_sf5.db                     # SF=5 database
│   └── ssb_sf10.db                    # SF=10 database
│
└── ssb-data/                          # SSB generated data
    ├── sf1/                           # SF=1 data (can be regenerated)
    ├── sf5/                           # SF=5 data (can be regenerated)
    ├── sf10/                          # SF=10 data (can be regenerated)
    └── ssb-dbgen/                     # SSB data generator
```

## Key Results

### SF=1 Results
- **No significant improvement** - dataset too small for RPT benefits
- Results preserved for comparison

### SF=5 Results
- **Average Speedup:** 1.34x (25.4% faster)
- **All 13 queries improved** with RPT
- **Best improvement:** q4.1 at +42%

### SF=10 Results
- **Average Speedup:** 1.35x (26.0% faster)
- **All 13 queries improved** with RPT
- **Best improvement:** q4.1 at +45.9%

## Quick Start

1. **Build DuckDB with RPT:**
   ```bash
   cd duckdb-rpt/rpt-src
   mkdir -p build && cd build
   cmake .. && make -j$(nproc)
   ```

2. **Run experiments:**
   ```bash
   cd runner
   ./run_all_scale_factors.sh
   ```

3. **View results:**
   - CSV files: `results/sf1/`, `results/sf5/`, and `results/sf10/`
   - Graphs: `results/graphs/sf1/`, `results/graphs/sf5/`, and `results/graphs/sf10/`

## Notes

- Build artifacts can be regenerated by running `cmake` and `make` in `duckdb-rpt/rpt-src/build/`
- SSB data files can be regenerated using `scripts/generate_higher_sf.sh`
- Old results and logs have been moved to `.cleanup_backup_*/` directories
EOF

echo "   ✓ Created REPOSITORY_STRUCTURE.md"

echo ""
echo "=========================================="
echo "Cleanup Summary"
echo "=========================================="
echo ""
echo "✓ Removed log files"
echo "✓ Removed temporary files"
echo "✓ Cleaned up old database files"
echo "✓ Removed backup files"
echo "✓ Consolidated results (kept sf5 and sf10)"
echo "✓ Removed unused documentation"
echo "✓ Removed Python cache files"
echo "✓ Created repository structure documentation"
echo ""
echo "Backup location: $BACKUP_DIR"
echo ""
echo "Repository size after cleanup:"
du -sh "$PROJECT_ROOT" 2>/dev/null | awk '{print "  Total: " $1}'
echo ""
echo "Essential directories:"
du -sh results runner scripts sql presentation*.md *.md duckdb-rpt/rpt-src 2>/dev/null | awk '{print "  " $2 ": " $1}'
echo ""
echo "=========================================="
echo "Cleanup complete!"
echo "=========================================="

