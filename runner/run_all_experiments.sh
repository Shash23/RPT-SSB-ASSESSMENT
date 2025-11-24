#!/usr/bin/env bash
set -euo pipefail

# Adjust these paths once you build DuckDB/RPT on CloudLab.
BASELINE_BIN="../duckdb-baseline/build/debug/duckdb"
RPT_BIN="../duckdb-rpt/build/debug/duckdb"

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
