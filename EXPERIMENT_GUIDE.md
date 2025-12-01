# Complete Experiment Guide: RPT-SSB Assessment

This guide walks you through every step to run the experiments and understand the outputs.

## Table of Contents
1. [What the Experiments Output](#what-the-experiments-output)
2. [Prerequisites](#prerequisites)
3. [Complete Setup Steps](#complete-setup-steps)
4. [Running the Experiments](#running-the-experiments)
5. [Understanding the Results](#understanding-the-results)
6. [Next Steps](#next-steps)

---

## What the Experiments Output

### Output Files

The experiments generate **CSV files** with timing data:

**Location:** `results/` directory

**Files created:**
- `results/ssb_baseline.csv` - Baseline DuckDB execution times
- `results/ssb_rpt.csv` - RPT-enabled DuckDB execution times

### Output Format

Each CSV file has 4 columns:

| Column | Description | Example |
|--------|-------------|---------|
| `mode` | Which DuckDB version | `baseline` or `rpt` |
| `query` | SSB query name | `q1.1`, `q2.1`, `q3.3`, etc. |
| `rep` | Repetition number (1-5) | `1`, `2`, `3`, `4`, `5` |
| `time_seconds` | Execution time | `0.123456` |

### Example Output

```csv
mode,query,rep,time_seconds
baseline,q1.1,1,0.234567
baseline,q1.1,2,0.231234
baseline,q1.1,3,0.229876
baseline,q1.1,4,0.232145
baseline,q1.1,5,0.230987
baseline,q1.2,1,0.456789
...
rpt,q1.1,1,0.198765
rpt,q1.1,2,0.197654
...
```

### What Gets Measured

- **13 SSB queries** (q1.1, q1.2, q1.3, q2.1, q2.2, q2.3, q3.1, q3.2, q3.3, q3.4, q4.1, q4.2, q4.3)
- **5 repetitions** per query (to account for variance)
- **2 modes**: baseline vs RPT
- **Total**: 13 queries × 5 reps × 2 modes = **130 measurements**

### Console Output

While running, you'll see:
```
baseline q1.1 rep 1: 0.234s
baseline q1.1 rep 2: 0.231s
baseline q1.1 rep 3: 0.230s
...
rpt q1.1 rep 1: 0.199s
rpt q1.1 rep 2: 0.198s
...
```

---

## Prerequisites

### On CloudLab (Required for RPT)

- CloudLab account with NextGenDB project access
- x86_64 Linux node
- SSH access to your node

### Software Requirements

- Git
- CMake 3.20+
- C++ compiler (GCC/Clang) with C++17
- Python 3.6+
- Make

---

## Complete Setup Steps

### Step 1: Access CloudLab

1. Go to https://www.cloudlab.us
2. Sign in to your account
3. Create a new experiment
4. Select an x86_64 node (e.g., `d430` or `c220g5`)
5. Start the experiment
6. SSH into your node: `ssh <username>@<node-ip>`

### Step 2: Clone Your Repository

```bash
# On CloudLab node
cd ~
git clone <your-repo-url>
cd RPT-SSB-ASSESSMENT
```

**Note:** Replace `<your-repo-url>` with your actual GitHub/GitLab URL.

### Step 3: Generate SSB Data

```bash
# Navigate to data directory
cd ssb-data

# Clone SSB data generator
git clone https://github.com/eyalroz/ssb-dbgen
cd ssb-dbgen

# Build the generator
mkdir build && cd build
cmake ..
make -j$(nproc)

# Generate SF=1 data (this takes a few minutes)
./dbgen -s 1

# Move data files to the sf1 directory
mv *.tbl ../../sf1/

# Verify files were created
cd ../../sf1
ls -lh *.tbl

# Should see: customer.tbl, date.tbl, lineorder.tbl, part.tbl, supplier.tbl
cd ../..
```

**Expected output:** 5 `.tbl` files totaling ~600MB for SF=1

### Step 4: Build Baseline DuckDB

```bash
# Go to parent directory
cd ..

# Clone baseline DuckDB
git clone https://github.com/duckdb/duckdb.git duckdb-baseline
cd duckdb-baseline

# Build in Release mode
mkdir build && cd build
cmake .. -DCMAKE_BUILD_TYPE=Release
make -j$(nproc)

# Verify build succeeded
./duckdb --version

# Should output: vX.X.X
cd ../..
```

**Expected time:** 10-20 minutes depending on node

### Step 5: Build RPT-Enabled DuckDB

```bash
# Navigate to RPT DuckDB source
# (Adjust path if your RPT source is elsewhere)
cd duckdb-rpt/rpt-src

# Enable RPT optimization
# Edit the setting file
nano src/include/duckdb/optimizer/predicate_transfer/setting.hpp

# Find these lines and make sure ONLY PredicateTransfer is uncommented:
#   #define PredicateTransfer    <-- UNCOMMENT THIS
#   // #define BloomJoin         <-- LEAVE COMMENTED
#   // #define SmalltoLarge      <-- LEAVE COMMENTED

# Save and exit (Ctrl+X, Y, Enter)

# Build RPT DuckDB
mkdir -p build && cd build
cmake .. -DCMAKE_BUILD_TYPE=Release
make -j$(nproc)

# Verify build succeeded
./duckdb --version

cd ../../..
```

**Expected time:** 10-20 minutes

**Troubleshooting:**
- If you get AVX errors, your node might not support AVX2/AVX512
- Try a different CloudLab node type
- Check: `cat /proc/cpuinfo | grep avx`

### Step 6: Load SSB Data into DuckDB

```bash
# Back in project root
cd RPT-SSB-ASSESSMENT

# Make sure the helper script is executable
chmod +x sql/load_ssb.sh

# Load data (uses baseline DuckDB by default, or finds any duckdb in PATH)
./sql/load_ssb.sh

# Or specify a specific DuckDB binary:
# ./sql/load_ssb.sh db/ssb.duckdb ../duckdb-baseline/build/duckdb
```

**Expected output:**
```
Loading SSB data into /path/to/RPT-SSB-ASSESSMENT/db/ssb.duckdb
Project root: /path/to/RPT-SSB-ASSESSMENT
Done loading SSB data.
```

**Verify data loaded:**
```bash
# Check database size
ls -lh db/ssb.duckdb

# Should be ~100-200MB for SF=1

# Quick test query
../duckdb-baseline/build/duckdb db/ssb.duckdb -c "SELECT COUNT(*) FROM ssb.lineorder;"

# Should output: ~6,000,000 rows for SF=1
```

### Step 7: Update Experiment Script Paths

```bash
# Edit the experiment runner script
cd runner
nano run_all_experiments.sh
```

**Update these paths to match your setup:**
```bash
BASELINE_BIN="../duckdb-baseline/build/duckdb"    # Adjust if needed
RPT_BIN="../duckdb-rpt/rpt-src/build/duckdb"      # Adjust if needed
DB_PATH="../db/ssb.duckdb"                         # Should be correct
RESULTS_DIR="../results"                           # Should be correct
```

**Save and exit.**

**Make script executable:**
```bash
chmod +x run_all_experiments.sh
chmod +x run_experiments.py
```

---

## Running the Experiments

### Option 1: Run All Experiments (Recommended)

```bash
# From the runner directory
cd runner
./run_all_experiments.sh
```

This will:
1. Run all 13 queries × 5 reps on baseline DuckDB
2. Run all 13 queries × 5 reps on RPT DuckDB
3. Save results to `results/ssb_baseline.csv` and `results/ssb_rpt.csv`

**Expected time:** 30-60 minutes total (depends on queries and node performance)

### Option 2: Run Individual Experiments

```bash
# Run baseline only
python3 run_experiments.py \
  --mode baseline \
  --duckdb-bin ../duckdb-baseline/build/duckdb \
  --db ../db/ssb.duckdb \
  --reps 5 \
  --out ../results/ssb_baseline.csv

# Run RPT only
python3 run_experiments.py \
  --mode rpt \
  --duckdb-bin ../duckdb-rpt/rpt-src/build/duckdb \
  --db ../db/ssb.duckdb \
  --reps 5 \
  --out ../results/ssb_rpt.csv
```

### Option 3: Test with Fewer Repetitions

For quick testing:
```bash
python3 run_experiments.py \
  --mode baseline \
  --duckdb-bin ../duckdb-baseline/build/duckdb \
  --db ../db/ssb.duckdb \
  --reps 1 \
  --out ../results/test_baseline.csv
```

### Monitoring Progress

The script prints progress to console:
```
baseline q1.1 rep 1: 0.234s
baseline q1.1 rep 2: 0.231s
...
```

**To run in background and save output:**
```bash
./run_all_experiments.sh 2>&1 | tee ../results/experiment_log.txt
```

---

## Understanding the Results

### Viewing Results

```bash
# View baseline results
head -20 results/ssb_baseline.csv

# View RPT results
head -20 results/ssb_rpt.csv

# Count total measurements
wc -l results/ssb_baseline.csv  # Should be 66 lines (1 header + 65 data)
wc -l results/ssb_rpt.csv       # Should be 66 lines
```

### Analyzing Results

#### Quick Comparison (using command line)

```bash
# Average time per query for baseline
awk -F',' 'NR>1 {sum[$2]+=$4; count[$2]++} END {for(q in sum) print q, sum[q]/count[q]}' results/ssb_baseline.csv | sort

# Average time per query for RPT
awk -F',' 'NR>1 {sum[$2]+=$4; count[$2]++} END {for(q in sum) print q, sum[q]/count[q]}' results/ssb_rpt.csv | sort
```

#### Calculate Speedup

For each query, calculate:
```
Speedup = (Baseline Average Time) / (RPT Average Time)
```

If Speedup > 1.0, RPT is faster.
If Speedup < 1.0, RPT is slower.

#### Use the Provided Analysis Script

We've included an analysis script. Run it:

```bash
# From the runner directory
cd runner
python3 analyze_results.py

# Or specify custom paths
python3 analyze_results.py ../results/ssb_baseline.csv ../results/ssb_rpt.csv
```

This script will show:
- Average execution time for each query (baseline vs RPT)
- Speedup ratio (how many times faster/slower)
- Percentage improvement
- Summary statistics (total speedup, wins/losses)

### What Good Results Look Like

- **Speedup > 1.0**: RPT is faster (good!)
- **Speedup ≈ 1.0**: No significant difference
- **Speedup < 1.0**: RPT is slower (might indicate an issue)

**Expected patterns:**
- Queries with more joins (q2.x, q3.x, q4.x) may show larger speedups
- Simple queries (q1.x) may show smaller or no speedup
- Variance between repetitions should be small (< 10%)

---

## Next Steps

### 1. Download Results

```bash
# From CloudLab, copy results to your local machine
# On your local machine:
scp <username>@<cloudlab-node>:~/RPT-SSB-ASSESSMENT/results/*.csv ./
```

### 2. Create Visualizations

Create graphs showing:
- Execution time comparison (bar chart)
- Speedup per query (line chart)
- Distribution of execution times (box plots)

**Tools:**
- Python: matplotlib, pandas, seaborn
- R: ggplot2
- Excel/Google Sheets

### 3. Statistical Analysis

- Calculate confidence intervals
- Perform t-tests to verify significance
- Analyze variance and robustness

### 4. Write Your Paper

Use the results to:
- Compare baseline vs RPT performance
- Analyze which queries benefit most
- Discuss robustness to join order
- Draw conclusions about RPT effectiveness

---

## Troubleshooting

### Experiments Fail to Start

**Problem:** `duckdb: command not found`
**Solution:** Check paths in `run_all_experiments.sh` are correct

**Problem:** `Database file not found`
**Solution:** Run `./sql/load_ssb.sh` first to create the database

### Queries Take Too Long

**Problem:** Queries running for hours
**Solution:** 
- Check if data loaded correctly: `SELECT COUNT(*) FROM ssb.lineorder;`
- Try with fewer repetitions: `--reps 1`
- Check system resources: `htop` or `top`

### Results Look Wrong

**Problem:** All times are 0.000001 or very similar
**Solution:** 
- Verify you're using the correct DuckDB binaries
- Check that RPT is actually enabled (check setting.hpp)
- Rebuild DuckDB if needed

### Out of Memory

**Problem:** Process killed or out of memory errors
**Solution:**
- Use a larger CloudLab node
- Reduce scale factor (SF=0.1 for testing)
- Close other processes

---

## Quick Reference

### Essential Commands

```bash
# Build baseline
cd ~/duckdb-baseline/build && make -j$(nproc)

# Build RPT
cd ~/duckdb-rpt/rpt-src/build && make -j$(nproc)

# Load data
cd ~/RPT-SSB-ASSESSMENT && ./sql/load_ssb.sh

# Run experiments
cd ~/RPT-SSB-ASSESSMENT/runner && ./run_all_experiments.sh

# Check results
head results/ssb_baseline.csv
```

### File Locations

- **Baseline DuckDB:** `~/duckdb-baseline/build/duckdb`
- **RPT DuckDB:** `~/duckdb-rpt/rpt-src/build/duckdb`
- **Database:** `~/RPT-SSB-ASSESSMENT/db/ssb.duckdb`
- **Results:** `~/RPT-SSB-ASSESSMENT/results/`
- **SSB Data:** `~/RPT-SSB-ASSESSMENT/ssb-data/sf1/*.tbl`

---

## Summary Checklist

Before running experiments, verify:

- [ ] CloudLab node is x86_64
- [ ] SSB data generated (5 .tbl files in ssb-data/sf1/)
- [ ] Baseline DuckDB built successfully
- [ ] RPT DuckDB built with PredicateTransfer enabled
- [ ] Database loaded (db/ssb.duckdb exists and has data)
- [ ] Paths in run_all_experiments.sh are correct
- [ ] Scripts are executable (chmod +x)

**Ready to run!** 🚀

