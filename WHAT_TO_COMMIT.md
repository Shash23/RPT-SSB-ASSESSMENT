# What to Commit to GitHub

## ✅ SHOULD Commit (Essential Files)

### Code & Scripts
- `runner/` - All experiment execution scripts
  - `run_all_experiments.sh`
  - `run_all_scale_factors.sh`
  - `run_experiments.py`
  - `measure_join_sizes.py`
  - `measure_memory.py`
  - `analyze_results.py`
  - `create_graphs.py`
  - `create_graphs_for_scale_factor.py`

- `scripts/` - Utility scripts
  - `generate_higher_sf.sh`
  - `cleanup_space.sh`
  - `update_for_scale_factor.sh`

- `sql/` - SQL scripts
  - `load_ssb.sql`

- `cleanup_repository.sh` - Repository cleanup script

### Documentation
- `README.md` - Main project README
- `EXPERIMENT_GUIDE.md` - Experiment execution guide
- `SCALING_UP_GUIDE.md` - Guide for scaling to higher SF
- `REPOSITORY_STRUCTURE.md` - Repository structure documentation
- `WHAT_TO_COMMIT.md` - This file

### Presentation Materials
- `presentation_outline.md`
- `presentation_script.md`
- `presentation_future_work_script.md`

### Results (Small but Important)
- `results/sf1/` - SF=1 CSV results (6 files, ~2KB total)
- `results/sf5/` - SF=5 CSV results (6 files, ~2KB total)
- `results/sf10/` - SF=10 CSV results (6 files, ~2KB total)
- `results/graphs/sf1/` - SF=1 graphs (5 PNG files, ~800KB total)
- `results/graphs/sf5/` - SF=5 graphs (5 PNG files, ~1MB total)
- `results/graphs/sf10/` - SF=10 graphs (5 PNG files, ~1MB total)

**Note:** Results are small (CSV files are KB, graphs are MB) and are the key findings of the project.

### Configuration
- `.gitignore` - Updated to exclude large files
- `CHECK_EXPERIMENT_STATUS.sh` - Status checking script

## ❌ Should NOT Commit (Large/Regeneratable Files)

### Large Data Files
- `ssb-data/sf1/`, `ssb-data/sf5/`, `ssb-data/sf10/` - Generated data (9.5GB total)
  - Can be regenerated using `scripts/generate_higher_sf.sh`
  - Keep `ssb-data/ssb-dbgen/` (source code for generator)

### Database Files
- `duckdb-rpt/ssb_sf5.db` (712MB)
- `duckdb-rpt/ssb_sf10.db` (1.4GB)
- `duckdb-rpt/ssb.db` (if exists)

### Build Artifacts
- `duckdb-rpt/rpt-src/build/` (327MB)
  - Can be regenerated with `cmake` and `make`

### Backup Directories
- `.cleanup_backup_*/` - Temporary backup directories

### DuckDB Source Code
- `duckdb-rpt/rpt-src/` - This is likely a git submodule or separate repository
  - If it's a submodule, commit the submodule reference
  - If it's a fork, handle separately

## 📝 Recommended Commit Commands

```bash
# 1. Update .gitignore (already done)
git add .gitignore

# 2. Add all essential code and scripts
git add runner/ scripts/ sql/ cleanup_repository.sh CHECK_EXPERIMENT_STATUS.sh

# 3. Add all documentation
git add README.md EXPERIMENT_GUIDE.md SCALING_UP_GUIDE.md REPOSITORY_STRUCTURE.md WHAT_TO_COMMIT.md

# 4. Add presentation materials
git add presentation_*.md

# 5. Add results (CSV and graphs)
git add results/

# 6. Remove deleted files
git rm GIT_SETUP.md sql/load_ssb.sh db/.gitkeep 2>/dev/null || true

# 7. Commit
git commit -m "Clean up repository and organize results

- Organize results by scale factor (sf1, sf5, sf10)
- Add comprehensive documentation
- Add cleanup script
- Update .gitignore to exclude large files
- Preserve all experiment results and graphs"

# 8. Push (if ready)
# git push origin <your-branch>
```

## 📊 Repository Size After Commit

Expected size after commit:
- Code & scripts: ~200KB
- Documentation: ~100KB
- Results (CSV): ~10KB
- Results (graphs): ~3MB
- **Total: ~3.5MB** (very manageable for GitHub)

Large files excluded:
- Data files: 9.5GB (regeneratable)
- Database files: 2.1GB (regeneratable)
- Build artifacts: 327MB (regeneratable)

