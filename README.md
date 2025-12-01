# RPT-SSB-ASSESSMENT

Evaluation of Robust Predicate Transfer (RPT) on the Star Schema Benchmark (SSB).

## Project Overview

This project compares baseline DuckDB against RPT-enabled DuckDB on the SSB benchmark to evaluate:
- Performance improvements from predicate transfer
- Robustness under different join order scenarios
- Join order sensitivity analysis

## Project Structure

```
RPT-SSB-ASSESSMENT/
├── duckdb-rpt/          # RPT-enabled DuckDB source (git submodule or clone)
├── ssb-data/            # SSB benchmark data
│   └── sf1/            # Scale factor 1 data files
├── sql/                 # SQL scripts
│   ├── load_ssb.sql    # Schema and data loading (uses placeholder paths)
│   └── load_ssb.sh     # Helper script to load data with correct paths
├── runner/              # Experiment automation
│   ├── run_experiments.py      # Python script to run queries and log timings
│   └── run_all_experiments.sh  # Bash script to run all experiments
├── db/                  # DuckDB database files (gitignored)
└── results/             # Benchmark results (gitignored)
```

## Prerequisites

- **x86_64 Linux machine** (required for RPT compilation - uses AVX2/AVX512 intrinsics)
- CMake 3.20+
- C++ compiler with C++17 support
- Python 3.6+
- Git

**Note:** RPT cannot be compiled on ARM (M1 Mac). Use CloudLab or another x86 machine.

## CloudLab Setup

### 1. Get CloudLab Access

1. Sign up at: https://www.cloudlab.us/signup.php?pid=NextGenDB
2. Wait for project approval
3. Create an experiment with an x86_64 node

### 2. Clone Repository on CloudLab

```bash
# On your CloudLab node
git clone <your-repo-url>
cd RPT-SSB-ASSESSMENT
```

### 3. Generate SSB Data (if not already present)

```bash
# If ssb-dbgen is not in the repo, clone and build it
cd ssb-data
git clone https://github.com/eyalroz/ssb-dbgen
cd ssb-dbgen
mkdir build && cd build
cmake ..
make -j$(nproc)

# Generate SF=1 data
./dbgen -s 1

# Move data files to sf1 directory
mv *.tbl ../../sf1/
cd ../../..
```

### 4. Build Baseline DuckDB

```bash
# Clone baseline DuckDB (or use your baseline version)
cd ..
git clone https://github.com/duckdb/duckdb.git duckdb-baseline
cd duckdb-baseline
mkdir build && cd build
cmake .. -DCMAKE_BUILD_TYPE=Release
make -j$(nproc)
cd ../..
```

### 5. Build RPT-Enabled DuckDB

```bash
# If duckdb-rpt is a submodule or separate clone
cd duckdb-rpt/rpt-src  # or wherever your RPT DuckDB source is

# Enable RPT by editing the setting file
# Edit: src/include/duckdb/optimizer/predicate_transfer/setting.hpp
# Uncomment: #define PredicateTransfer
# Leave BloomJoin and SmalltoLarge commented for true RPT

# Build
mkdir -p build && cd build
cmake .. -DCMAKE_BUILD_TYPE=Release
make -j$(nproc)
cd ../../..
```

### 6. Load SSB Data

```bash
# Use the helper script (automatically detects project root)
./sql/load_ssb.sh

# Or manually with duckdb CLI
# First, update PROJECT_ROOT_PLACEHOLDER in sql/load_ssb.sql with your path
# Then:
duckdb db/ssb.duckdb < sql/load_ssb.sql
```

### 7. Run Experiments

```bash
cd runner

# Update paths in run_all_experiments.sh to point to your DuckDB binaries
# Then run:
./run_all_experiments.sh

# Results will be in ../results/
```

## Local Development (macOS)

You can prepare scripts and test data generation locally, but **cannot build RPT DuckDB** on ARM.

### Local Setup

```bash
# Generate SSB data
cd ssb-data
git clone https://github.com/eyalroz/ssb-dbgen
cd ssb-dbgen
mkdir build && cd build
cmake ..
make -j4
./dbgen -s 1
mv *.tbl ../../sf1/
cd ../../..

# Load data (requires regular DuckDB installed)
./sql/load_ssb.sh
```

## Experiment Workflow

1. **Build both DuckDB versions** (baseline and RPT) on CloudLab
2. **Load SSB data** using `sql/load_ssb.sh`
3. **Run experiments** using `runner/run_all_experiments.sh`
4. **Analyze results** from `results/` directory
5. **Generate graphs and paper**

## Results Format

Results are saved as CSV files with columns:
- `mode`: "baseline" or "rpt"
- `query`: Query name (e.g., "q1.1", "q2.1")
- `rep`: Repetition number
- `time_seconds`: Execution time in seconds

## Troubleshooting

### Path Issues
- If `load_ssb.sh` fails, ensure you're running from the project root
- DuckDB COPY requires absolute paths - the helper script handles this

### Build Issues
- RPT requires x86_64 - cannot build on ARM
- Ensure AVX2/AVX512 support is available on your CloudLab node
- Check that `PredicateTransfer` is defined in the setting.hpp file

### Data Loading Issues
- Ensure `.tbl` files exist in `ssb-data/sf1/`
- Check file permissions
- Verify DuckDB binary path is correct

## Git Workflow

- **Main branch**: Stable, production-ready code
- **Working branch**: Development (e.g., `shashwat`)

Large files (data, databases) are gitignored. Only code and scripts are tracked.

## References

- Original RPT paper: `pt.pdf`
- Project proposal: `wisc-cs764-f25-paper22.pdf`
- Report template: `report.pdf`
