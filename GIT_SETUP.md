# Git Setup and CloudLab Transfer Guide

## What Can Be Committed to GitHub

**Yes, you can commit this directory!** Your `.gitignore` already excludes the large files:

### Excluded (Not Committed):
- ✅ `duckdb-rpt/*` - Large DuckDB source code (will clone separately on CloudLab)
- ✅ `db/*` - Database files (generated on CloudLab)
- ✅ `ssb-data/sf1/*.tbl` - Large data files (~600MB for SF=1)
- ✅ `ssb-data/ssb-dbgen` - Data generator build artifacts

### What WILL Be Committed (Small Files):
- ✅ Scripts: `runner/*.py`, `runner/*.sh`, `sql/*.sql`, `sql/*.sh`
- ✅ Documentation: `README.md`, `EXPERIMENT_GUIDE.md`
- ✅ PDFs: `pt.pdf`, `report.pdf`, `wisc-cs764-f25-paper22.pdf` (if you want)
- ✅ Configuration: `.gitignore`

**Total size:** ~1-5 MB (very manageable for GitHub)

## Recommended Approach

### Option 1: Commit Everything Except Large Files (Recommended)

This is what your `.gitignore` already does. Just commit the scripts and docs:

```bash
# Add all the important files
git add README.md EXPERIMENT_GUIDE.md
git add runner/*.py runner/*.sh
git add sql/*.sql sql/*.sh
git add .gitignore

# Optionally add PDFs (they're usually fine, but can be large)
# git add *.pdf

# Commit
git commit -m "Add experiment scripts and documentation for CloudLab"

# Push
git push origin <your-branch>
```

### Option 2: Use Git LFS for PDFs (If PDFs are Large)

If your PDFs are > 50MB, use Git LFS:

```bash
# Install git-lfs (if not installed)
# brew install git-lfs  # macOS
# apt-get install git-lfs  # Linux

# Initialize LFS
git lfs install

# Track PDFs with LFS
git lfs track "*.pdf"

# Add and commit
git add .gitattributes
git add *.pdf
git commit -m "Add PDFs with LFS"
```

## What to Do on CloudLab

### Step 1: Clone Your Repository

```bash
git clone <your-repo-url>
cd RPT-SSB-ASSESSMENT
```

### Step 2: Clone DuckDB Source (Separately)

The `duckdb-rpt` source is NOT in the repo (it's gitignored). On CloudLab:

```bash
# Clone baseline DuckDB
cd ..
git clone https://github.com/duckdb/duckdb.git duckdb-baseline

# Clone RPT DuckDB (wherever your RPT source is)
# If it's a private repo:
git clone <rpt-repo-url> duckdb-rpt
# Or if it's a fork/branch:
git clone https://github.com/duckdb/duckdb.git duckdb-rpt
cd duckdb-rpt
git checkout <rpt-branch>  # or whatever branch has RPT
```

### Step 3: Generate Data on CloudLab

```bash
cd ~/RPT-SSB-ASSESSMENT/ssb-data
git clone https://github.com/eyalroz/ssb-dbgen
cd ssb-dbgen
mkdir build && cd build
cmake ..
make -j$(nproc)
./dbgen -s 1
mv *.tbl ../../sf1/
```

## File Size Check

Before committing, check sizes:

```bash
# Check PDF sizes
ls -lh *.pdf

# Check total size of files to be committed
git add -n .
git ls-files --cached | xargs du -ch | tail -1
```

**GitHub limits:**
- Individual files: 100 MB (warning at 50 MB)
- Repository: 1 GB recommended, 100 GB hard limit
- PDFs are usually fine unless they're huge

## Quick Commit Checklist

Before pushing to GitHub:

- [ ] Check `.gitignore` is correct
- [ ] Verify large files are excluded (`duckdb-rpt`, `db`, `ssb-data/sf1/*.tbl`)
- [ ] Test that `git status` shows only small files
- [ ] Commit scripts and documentation
- [ ] Push to GitHub
- [ ] On CloudLab: clone repo + separately clone DuckDB source

## Alternative: Transfer via SCP (If GitHub is Problematic)

If you prefer not to use GitHub for some files:

```bash
# From your local machine, transfer to CloudLab
scp -r runner/ <user>@<cloudlab-node>:~/RPT-SSB-ASSESSMENT/
scp -r sql/ <user>@<cloudlab-node>:~/RPT-SSB-ASSESSMENT/
scp README.md EXPERIMENT_GUIDE.md <user>@<cloudlab-node>:~/RPT-SSB-ASSESSMENT/
```

But GitHub is usually easier and better for version control!

## Summary

**You're good to commit!** Your `.gitignore` already handles the large files. Just:

1. ✅ Commit scripts, docs, and config files
2. ✅ Push to GitHub
3. ✅ On CloudLab: clone repo + separately get DuckDB source
4. ✅ Generate data on CloudLab (don't transfer 600MB+ data files)

The repository will be small and manageable on GitHub.

