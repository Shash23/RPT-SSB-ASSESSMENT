#!/usr/bin/env bash
set -euo pipefail

# Adjust these paths once you build DuckDB/RPT on CloudLab.
# Note: Change 'debug' to 'Release' if you built with -DCMAKE_BUILD_TYPE=Release
BASELINE_BIN="../duckdb-baseline/build/duckdb"
RPT_BIN="../duckdb-rpt/rpt-src/build/duckdb"

DB_PATH="../db/ssb.duckdb"
RESULTS_DIR="../results"

mkdir -p "$RESULTS_DIR"

# Baseline
python3 run_experiments.py \
  --mode baseline \
  --duckdb-bin "$BASELINE_BIN" \
  --db "$DB_PATH" \
  --reps 5 \
  --out "$RESULTS_DIR/ssb_baseline.csv"

# RPT
python3 run_experiments.py \
  --mode rpt \
  --duckdb-bin "$RPT_BIN" \
  --db "$DB_PATH" \
  --reps 5 \
  --out "$RESULTS_DIR/ssb_rpt.csv"
