#!/usr/bin/env bash
set -euo pipefail

# Get script directory and project root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Paths (absolute)
RPT_SRC_DIR="${PROJECT_ROOT}/duckdb-rpt/rpt-src"
SETTING_FILE="${RPT_SRC_DIR}/src/include/duckdb/optimizer/predicate_transfer/setting.hpp"
RPT_BIN="${RPT_SRC_DIR}/build/duckdb"
RESULTS_DIR="${PROJECT_ROOT}/results"
LOAD_SQL="${PROJECT_ROOT}/sql/load_ssb.sql"

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

# Function to load data for a scale factor
load_data() {
    local scale_factor=$1
    local db_path="${PROJECT_ROOT}/duckdb-rpt/ssb_sf${scale_factor}.db"
    local data_dir="${PROJECT_ROOT}/ssb-data/sf${scale_factor}"
    
    echo ""
    echo "=========================================="
    echo "Loading SF=${scale_factor} data..."
    echo "=========================================="
    
    # Remove old database if exists
    if [ -f "$db_path" ]; then
        echo "Removing old database: $db_path"
        rm -f "$db_path"
    fi
    
    # Check if data directory exists
    if [ ! -d "$data_dir" ]; then
        echo "Error: Data directory not found: $data_dir"
        exit 1
    fi
    
    # Create temporary load script with correct paths
    local temp_load="${PROJECT_ROOT}/sql/load_ssb_sf${scale_factor}.sql"
    sed -e "s|PROJECT_ROOT_PLACEHOLDER|${PROJECT_ROOT}|g" \
        -e "s|sf1/|sf${scale_factor}/|g" \
        "$LOAD_SQL" > "$temp_load"
    
    # Load data
    echo "Loading data from $data_dir into $db_path..."
    "$RPT_BIN" "$db_path" < "$temp_load"
    
    # Clean up temp file
    rm -f "$temp_load"
    
    echo "Data loaded successfully!"
    echo "Database: $db_path"
    echo "Size: $(du -sh "$db_path" | awk '{print $1}')"
}

# Function to run all experiments for a scale factor and mode
run_all_experiments() {
    local scale_factor=$1
    local mode=$2
    local db_path="${PROJECT_ROOT}/duckdb-rpt/ssb_sf${scale_factor}.db"
    
    echo ""
    echo "=========================================="
    echo "Running $mode experiments for SF=${scale_factor}..."
    echo "=========================================="
    
    local sf_results_dir="${RESULTS_DIR}/sf${scale_factor}"
    mkdir -p "$sf_results_dir"
    
    # 1. Performance experiments
    echo "1. Running performance experiments..."
    python3 "${SCRIPT_DIR}/run_experiments.py" \
        --mode "${mode}" \
        --duckdb-bin "$RPT_BIN" \
        --db "$db_path" \
        --reps 5 \
        --out "${sf_results_dir}/ssb_${mode}.csv"
    
    # 2. Join size measurements
    echo "2. Measuring join sizes..."
    python3 "${SCRIPT_DIR}/measure_join_sizes.py" \
        --mode "${mode}" \
        --duckdb-bin "$RPT_BIN" \
        --db "$db_path" \
        --out "${sf_results_dir}/join_sizes_${mode}.csv"
    
    # 3. Memory measurements
    echo "3. Measuring memory utilization..."
    python3 "${SCRIPT_DIR}/measure_memory.py" \
        --mode "${mode}" \
        --duckdb-bin "$RPT_BIN" \
        --db "$db_path" \
        --out "${sf_results_dir}/memory_${mode}.csv"
    
    echo "All experiments completed for SF=${scale_factor} ($mode mode)"
}

# Main execution
echo "=========================================="
echo "RPT-SSB Full Experiment Suite"
echo "Scale Factors: SF=5 and SF=10"
echo "=========================================="
echo ""

# Process each scale factor
for SCALE_FACTOR in 5 10; do
    echo ""
    echo "=========================================="
    echo "PROCESSING SCALE FACTOR ${SCALE_FACTOR}"
    echo "=========================================="
    
    # Load data
    load_data "$SCALE_FACTOR"
    
    # Run RPT experiments
    echo ""
    echo "--- RPT Mode ---"
    configure_setting "rpt"
    rebuild_duckdb "rpt"
    run_all_experiments "$SCALE_FACTOR" "rpt"
    
    # Run baseline experiments
    echo ""
    echo "--- Baseline Mode ---"
    configure_setting "baseline"
    rebuild_duckdb "baseline"
    run_all_experiments "$SCALE_FACTOR" "baseline"
    
    echo ""
    echo "=========================================="
    echo "SF=${SCALE_FACTOR} experiments completed!"
    echo "=========================================="
done

echo ""
echo "=========================================="
echo "ALL EXPERIMENTS COMPLETED!"
echo "=========================================="
echo "Results directory: $RESULTS_DIR"
echo ""
echo "SF=5 results:"
echo "  - Performance: $RESULTS_DIR/sf5/ssb_rpt.csv, ssb_baseline.csv"
echo "  - Join sizes: $RESULTS_DIR/sf5/join_sizes_rpt.csv, join_sizes_baseline.csv"
echo "  - Memory: $RESULTS_DIR/sf5/memory_rpt.csv, memory_baseline.csv"
echo ""
echo "SF=10 results:"
echo "  - Performance: $RESULTS_DIR/sf10/ssb_rpt.csv, ssb_baseline.csv"
echo "  - Join sizes: $RESULTS_DIR/sf10/join_sizes_rpt.csv, join_sizes_baseline.csv"
echo "  - Memory: $RESULTS_DIR/sf10/memory_rpt.csv, memory_baseline.csv"
echo ""

