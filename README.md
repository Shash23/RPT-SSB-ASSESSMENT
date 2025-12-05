# Evaluating Robust Predicate Transfer in DuckDB

**Purpose:** Evaluate RPT's performance and robustness on the Star Schema Benchmark (SSB) to test its effectiveness under realistic data warehouse workloads.

## Objectives

- Compare RPT-enabled DuckDB against baseline (RPT disabled) on SSB queries
- Measure query runtime, intermediate join sizes, and memory utilization
- Assess RPT's robustness across different scale factors (SF=1, SF=5, SF=10)
- Evaluate performance improvements for star-schema join patterns

## Architecture

- **Database Engine:** DuckDB v1.4.0 (RPT-enabled fork from EmbryoLabs)
- **Benchmark:** Star Schema Benchmark (SSB)
- **Platform:** x86_64 Linux (CloudLab EC2 instance)
- **Join Order Strategy:** RandomLeftDeep (for robustness testing)
- **Scale Factors:** SF=1, SF=5, SF=10

## Environment

- **EC2 Instance Type:** [t3.large or similar - check EC2 console]
- **OS:** Ubuntu 22.04.5 LTS
- **DuckDB Version:** v1.4.0 (RPT-enabled)
- **Storage:** 29GB EBS volume, ext4 filesystem

*(Full environment details available in RESULTS.md)*

## Setup

### Prerequisites

- x86_64 Linux machine (RPT requires AVX2/AVX512 intrinsics)
- CMake 3.20+
- C++ compiler with C++17 support
- Python 3.6+
- Git

### Quick Setup

```bash
# Clone repository
git clone <repo-url>
cd RPT-SSB-ASSESSMENT

# Generate SSB data (if not present)
cd ssb-data/ssb-dbgen
mkdir build && cd build
cmake .. && make -j$(nproc)
./dbgen -s 5  # Generate SF=5 data
./dbgen -s 10 # Generate SF=10 data
mv *.tbl ../../sf5/ && mv *.tbl ../../sf10/

# Build DuckDB with RPT
cd ../../../duckdb-rpt/rpt-src
mkdir -p build && cd build
cmake .. -DCMAKE_BUILD_TYPE=Release
make -j$(nproc)

# Load SSB data
cd ../../..
duckdb duckdb-rpt/ssb_sf5.db < sql/load_ssb.sql
```

## How to Run

### Run Full Experiment Suite

```bash
cd runner
./run_all_scale_factors.sh
```

This script will:
1. Configure DuckDB for RPT and baseline modes
2. Rebuild DuckDB for each configuration
3. Run all SSB queries for SF=5 and SF=10
4. Measure join sizes and memory utilization
5. Generate comparison graphs

### Run Individual Experiments

```bash
# Run experiments for a specific scale factor
cd runner
./run_all_experiments.sh

# Generate graphs
python3 create_graphs_for_scale_factor.py 5
python3 create_graphs_for_scale_factor.py 10
```

### View Results

- **CSV Results:** `results/sf5/`, `results/sf10/`
- **Graphs:** `results/graphs/sf5/`, `results/graphs/sf10/`

## Results Summary

### SF=5 Results
- **Average Speedup:** 1.34x (25.4% faster)
- All 13 queries improved with RPT
- Best improvement: q4.1 at +42%

### SF=10 Results
- **Average Speedup:** 1.35x (26.0% faster)
- All 13 queries improved with RPT
- Best improvement: q4.1 at +45.9%

### Key Findings
- RPT shows significant improvements at SF=5 and SF=10 (no improvement at SF=1)
- Benefits are consistent across scale factors (~25-26% average speedup)
- Multi-join queries (q2.x, q4.x) show the largest improvements (22-46% faster)
- Small memory overhead (~2% increase) for substantial performance gains

## Project Structure

```
RPT-SSB-ASSESSMENT/
├── runner/              # Experiment execution scripts
├── scripts/             # Utility scripts
├── sql/                 # SQL loading scripts
├── results/             # Experiment results (CSV + graphs)
│   ├── sf5/            # SF=5 results
│   ├── sf10/           # SF=10 results
│   └── graphs/         # Visualization graphs
└── duckdb-rpt/         # RPT-enabled DuckDB source
```

## Documentation

- `EXPERIMENT_GUIDE.md` - Detailed experiment execution guide
- `SCALING_UP_GUIDE.md` - Guide for generating higher scale factors
- `REPOSITORY_STRUCTURE.md` - Complete repository structure documentation

## References

- Original RPT Paper: [Debunking the Myth of Join Ordering: Toward Robust SQL Analytics](https://pages.cs.wisc.edu/~yxy/cs764-f25/papers/rpt.pdf)
- Project Proposal: `wisc-cs764-f25-paper22.pdf`
