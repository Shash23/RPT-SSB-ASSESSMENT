# Scaling Up SSB Experiments - Guide

## Current Situation

- **Available Disk Space:** ~655 MB (92% full)
- **Current Scale Factor:** SF=1 (~600 MB data)
- **Problem:** SF=1 is too small to see RPT benefits

## Space Requirements

| Scale Factor | Estimated Data Size | Lineorder Rows | Can Fit? |
|--------------|---------------------|----------------|----------|
| SF=1 (current) | ~600 MB | ~6M rows | ✅ Yes |
| SF=3 | ~1.8 GB | ~18M rows | ⚠️ Maybe (need cleanup) |
| SF=5 | ~3 GB | ~30M rows | ❌ No (need cleanup) |
| SF=10 | ~6 GB | ~60M rows | ❌ No (need cleanup + more space) |

## Recommended Approach

### Option 1: Clean Up and Use SF=3 or SF=5 (Recommended)

**Step 1: Clean Up Space**
```bash
cd /home/ubuntu/RPT-SSB-ASSESSMENT
./scripts/cleanup_space.sh
```

This will help you remove:
- DuckDB build artifacts (can be rebuilt)
- Old TPC-H database (if not needed)
- Old SSB databases
- Python cache files

**Step 2: Generate Higher Scale Factor Data**
```bash
# For SF=3 (recommended starting point)
./scripts/generate_higher_sf.sh 3

# Or for SF=5 (if you have space after cleanup)
./scripts/generate_higher_sf.sh 5
```

**Step 3: Update Database Path**
Update `sql/load_ssb.sql` to point to the new scale factor directory:
```sql
-- Change from:
COPY ssb.lineorder FROM 'ssb-data/sf1/lineorder.tbl' ...

-- To:
COPY ssb.lineorder FROM 'ssb-data/sf3/lineorder.tbl' ...
```

**Step 4: Load New Data**
```bash
./sql/load_ssb.sh
```

**Step 5: Update Experiment Scripts**
Update `runner/run_experiments.py` if database path changed, or use the same database file.

### Option 2: Request Larger EC2 Instance

If you need SF=10 or higher:
1. Request an EC2 instance with more storage (e.g., 20-50 GB)
2. Or use EBS volume expansion
3. Then generate SF=10 data

### Option 3: Use CloudLab (If Available)

CloudLab nodes typically have more storage:
- Request a node with 50+ GB storage
- Generate SF=10 or SF=100 data there
- Run experiments on CloudLab

## Quick Space Check

```bash
# Check current space
df -h /

# Check what's using space
du -sh /home/ubuntu/RPT-SSB-ASSESSMENT/* | sort -h

# Estimate space needed for SF=N
# Formula: ~600 MB × N
# SF=3: ~1.8 GB
# SF=5: ~3 GB
# SF=10: ~6 GB
```

## What to Clean Up

### Safe to Remove (can be regenerated):
1. **DuckDB build artifacts** (`duckdb-rpt/rpt-src/build/*.o`, `CMakeFiles/`)
   - Size: ~500 MB - 1 GB
   - Can rebuild with `make -j$(nproc)`

2. **TPC-H database** (`tpch.db`)
   - Size: ~246 MB
   - Only if not needed

3. **Old SSB databases** (`db/*.duckdb`)
   - Can regenerate from .tbl files

4. **Python cache** (`__pycache__/`, `*.pyc`)
   - Small but easy cleanup

### Keep:
- SSB data files (`.tbl` files) - needed to reload
- DuckDB binaries - needed to run experiments
- Results and graphs - your data!

## Expected Results at Higher Scale Factors

- **SF=3:** Should start seeing some RPT benefits on complex queries
- **SF=5:** More pronounced benefits, especially on multi-way joins
- **SF=10:** Should see significant benefits similar to RPT paper results

## Scripts Created

1. **`scripts/generate_higher_sf.sh`** - Generates SSB data at specified scale factor
2. **`scripts/cleanup_space.sh`** - Interactive cleanup tool

## Next Steps

1. Run cleanup script to free space
2. Generate SF=3 or SF=5 data
3. Update database loading scripts
4. Reload data
5. Re-run experiments
6. Compare results with SF=1 baseline

