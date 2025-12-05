#!/usr/bin/env bash
set -euo pipefail

# Get script directory and project root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Paths (absolute)
RPT_SRC_DIR="${PROJECT_ROOT}/duckdb-rpt/rpt-src"
SETTING_FILE="${RPT_SRC_DIR}/src/include/duckdb/optimizer/predicate_transfer/setting.hpp"
RPT_BIN="${RPT_SRC_DIR}/build/duckdb"
DB_PATH="${PROJECT_ROOT}/duckdb-rpt/ssb.db"
RESULTS_DIR="${PROJECT_ROOT}/results"

# Check if RPT source exists
if [ ! -d "$RPT_SRC_DIR" ]; then
    echo "Error: RPT source directory not found: $RPT_SRC_DIR"
    exit 1
fi

# Check if database exists
if [ ! -f "$DB_PATH" ]; then
    echo "Error: Database not found: $DB_PATH"
    echo "Please load the SSB data first."
    exit 1
fi

mkdir -p "$RESULTS_DIR"

# Function to configure setting.hpp
configure_setting() {
    local mode=$1
    local setting_file="$SETTING_FILE"
    
    if [ ! -f "$setting_file" ]; then
        echo "Error: Setting file not found: $setting_file"
        exit 1
    fi
    
    # Backup original (only once)
    if [ ! -f "${setting_file}.bak" ]; then
        cp "$setting_file" "${setting_file}.bak"
        echo "Backed up original setting.hpp"
    fi
    
    if [ "$mode" = "rpt" ]; then
        # RPT mode: enable PredicateTransfer and RandomLeftDeep
        cat > "$setting_file" << 'EOF'
// Exclusive
// #define BloomJoin
#define PredicateTransfer

// Exclusive
// #define ExactLeftDeep
// #define RandomBushy
#define RandomLeftDeep

// #define SmalltoLarge

// #define External
EOF
        echo "Configured setting.hpp for RPT mode (PredicateTransfer + RandomLeftDeep)"
    elif [ "$mode" = "baseline" ]; then
        # Baseline mode: disable PredicateTransfer, keep RandomLeftDeep
        cat > "$setting_file" << 'EOF'
// Exclusive
// #define BloomJoin
// #define PredicateTransfer

// Exclusive
// #define ExactLeftDeep
// #define RandomBushy
#define RandomLeftDeep

// #define SmalltoLarge

// #define External
EOF
        echo "Configured setting.hpp for baseline mode (RandomLeftDeep only, no PredicateTransfer)"
    else
        echo "Error: Unknown mode: $mode"
        exit 1
    fi
}

# Function to rebuild DuckDB
rebuild_duckdb() {
    local mode=$1
    local original_dir=$(pwd)
    echo ""
    echo "=========================================="
    echo "Rebuilding DuckDB for $mode mode..."
    echo "=========================================="
    
    cd "$RPT_SRC_DIR/build"
    
    # Rebuild
    make -j$(nproc)
    
    if [ ! -f "$RPT_BIN" ]; then
        echo "Error: Build failed, binary not found: $RPT_BIN"
        cd "$original_dir"
        exit 1
    fi
    
    echo "Build successful!"
    cd "$original_dir"
}

# Function to run experiments
run_experiments() {
    local mode=$1
    local output_file="$RESULTS_DIR/ssb_${mode}.csv"
    
    echo ""
    echo "=========================================="
    echo "Running $mode experiments..."
    echo "=========================================="
    
    python3 "${SCRIPT_DIR}/run_experiments.py" \
        --mode "$mode" \
  --duckdb-bin "$RPT_BIN" \
  --db "$DB_PATH" \
  --reps 5 \
        --out "$output_file"
    
    echo "Results saved to: $output_file"
}

# Main execution
echo "=========================================="
echo "RPT-SSB Experiment Runner"
echo "=========================================="
echo "Database: $DB_PATH"
echo "Results directory: $RESULTS_DIR"
echo ""

# Step 1: Configure and build for RPT mode
echo "Step 1: Setting up RPT mode..."
configure_setting "rpt"
rebuild_duckdb "rpt"
run_experiments "rpt"

# Step 2: Configure and build for baseline mode
echo ""
echo "Step 2: Setting up baseline mode..."
configure_setting "baseline"
rebuild_duckdb "baseline"
run_experiments "baseline"

echo ""
echo "=========================================="
echo "All experiments completed!"
echo "=========================================="
echo "Results:"
echo "  - RPT: $RESULTS_DIR/ssb_rpt.csv"
echo "  - Baseline: $RESULTS_DIR/ssb_baseline.csv"
echo ""
echo "Run analysis:"
echo "  python3 analyze_results.py"
echo ""
