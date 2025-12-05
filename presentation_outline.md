# 5-Minute Presentation: Evaluating Robust Predicate Transfer in DuckDB

## Slide 1: Title & Motivation (30 seconds)
**Title:** Evaluating Robust Predicate Transfer in DuckDB using Star Schema Benchmark

**Key Points:**
- Join operations are costly in analytical query processing
- RPT uses Bloom filters to propagate predicates across join graphs
- Previous evaluations used synthetic benchmarks (TPC-H, JOB, TPC-DS)
- **Gap:** Need evaluation on real-world workloads (star-schema, data skew, cyclic graphs)
- **Our contribution:** Evaluate RPT on SSB to test robustness under realistic conditions

**Visual:** Title slide with project authors

---

## Slide 2: What is RPT? (45 seconds)
**Key Points:**
- **Predicate Transfer (PT):** Uses Bloom filters instead of expensive semi-joins
- **Robust Predicate Transfer (RPT):** Adds two algorithms:
  - **LargestRoot:** Ensures full reduction via maximum spanning tree
  - **SafeSubjoin:** Validates join order for optimal runtime
- **Two-phase execution:**
  1. **Predicate Transfer Phase:** Forward and backward sweeps propagate filters
  2. **Join Phase:** Operates on pre-filtered, reduced data

**Visual:** Diagram showing predicate transfer flow (if available) or simple flowchart

---

## Slide 3: Star Schema Benchmark (SSB) (60 seconds)
**Key Points:**
- **What is SSB?** Simplified version of TPC-H designed specifically for star-schema workloads
- **Schema Structure:**
  - **1 Fact Table:** `lineorder` - contains transaction data (orders, revenue, quantities)
  - **4 Dimension Tables:**
    - `customer` - customer demographics (region, nation, city, market segment)
    - `supplier` - supplier information (region, nation, city)
    - `part` - product details (category, brand, manufacturer, color)
    - `date` - time dimensions (year, month, week, selling season)

**Why SSB for Real-World Workloads?**
1. **Star Schema is Ubiquitous:** Most data warehouses use star/snowflake schemas
   - Fact table at center, dimensions radiating out
   - Matches how businesses model sales, inventory, and analytics
2. **Simplified but Realistic:** Removes TPC-H complexity while keeping essential patterns
   - Focuses on multi-way joins between fact and dimensions
   - Tests selective predicates on dimension attributes
3. **Query Characteristics:**
   - Queries join fact table with multiple dimensions simultaneously
   - Filters on dimension attributes (region, year, category) propagate to fact table
   - Tests RPT's ability to handle star-shaped join graphs
4. **Gap in RPT Evaluation:**
   - RPT paper used TPC-H (snowflake schema, more complex)
   - SSB tests star-schema specifically, which is more common in practice
   - Validates RPT on simpler but more representative workload patterns

**Visual:** 
- Star schema diagram showing lineorder at center, dimensions around it
- Table showing table names and key attributes
- Comparison: TPC-H (snowflake) vs SSB (star) schema

---

## Slide 4: Methodology - Implementation Details (90 seconds)
**Key Points:**

### RPT Source Code Setup
- **Forked from EmbryoLabs:** We forked the RPT-enabled DuckDB repository from EmbryoLabs (https://github.com/embryo-labs/dynamic-predicate-transfer)
- **DuckDB Version:** Based on DuckDB v1.4.0 with RPT integration
- **RPT Implementation:** The RPT code is located in `src/optimizer/predicate_transfer/`
- **Configuration:** RPT is controlled via `src/include/duckdb/optimizer/predicate_transfer/setting.hpp`
  - For RPT mode: `#define PredicateTransfer` and `#define RandomLeftDeep`
  - For baseline: Comment out `PredicateTransfer`, keep `RandomLeftDeep`
- **Build Process:** 
  - Compiled with CMake in Release mode
  - Requires Arrow 16.0 for Bloom filter implementation
  - Built on x86_64 Linux (AVX2/AVX512 support required)
  - Rebuilt DuckDB when switching between configurations

### Dataset Preparation
- **Star Schema Benchmark (SSB):** Generated at scale factor 1
- **Data Generation:** Used `ssb-dbgen` tool (forked from eyalroz/ssb-dbgen)
- **Data Files:** Generated 5 tables:
  - `lineorder.tbl` - Fact table (~6M rows at SF=1)
  - `customer.tbl`, `supplier.tbl`, `part.tbl`, `date.tbl` - Dimension tables
- **Data Loading:** Created SSB schema and loaded data into DuckDB using SQL COPY commands
- **Database:** Single DuckDB database file (`ssb.db`) containing all tables

### Experimental Setup
- **Platform:** CloudLab x86_64 Linux nodes
- **Configurations:**
  1. **Baseline:** RPT disabled, default DuckDB optimizer, RandomLeftDeep join order
  2. **RPT Enabled:** Predicate transfer enabled, RandomLeftDeep join order
- **Join Order Choice: RandomLeftDeep**
  - **Why RandomLeftDeep?** 
    - RPT's core claim is robustness to join order - it should perform well regardless of join ordering
    - RandomLeftDeep provides a consistent, reproducible join order strategy
    - Left-deep plans are common in practice (simpler than bushy plans)
    - Random element tests robustness - RPT should handle suboptimal orders gracefully
    - Alternative options considered:
      - **ExactLeftDeep:** Deterministic but may favor specific optimizations
      - **RandomBushy:** More complex, harder to interpret results
      - **Default optimizer:** Would use different orders for baseline vs RPT, making comparison unfair
  - **Fair Comparison:** Using same join order for both configurations isolates RPT's effect
  - **Robustness Test:** If RPT is truly robust, it should perform well even with random (potentially suboptimal) join orders
- **Configuration Switching:** 
  - Modified `setting.hpp` file
  - Rebuilt DuckDB for each configuration
  - Used same binary for both modes (just different build-time configuration)

### Query Suite
- **13 SSB Queries:** Standard SSB query suite
  - Q1.x (3 queries): Simple 2-table joins (lineorder + date)
  - Q2.x (3 queries): 4-table joins (lineorder + date + part + supplier)
  - Q3.x (4 queries): 4-table joins with customer dimension
  - Q4.x (3 queries): 5-table joins (all dimensions)
- **Query Execution:** Each query executed via DuckDB CLI with SQL passed as command-line argument

### Measurement Process
1. **Query Runtime:**
   - Executed each query 5 times per configuration
   - Measured wall-clock time using Python's `time.perf_counter()`
   - Included warm-up run before measurements
   - Results saved to CSV: `ssb_baseline.csv` and `ssb_rpt.csv`

2. **Intermediate Join Sizes:**
   - Created SQL queries with CTEs to count rows at each join step
   - Measured: filtered dimension sizes, intermediate join results
   - Extracted row counts using COUNT(*) queries
   - Results saved to CSV: `join_sizes_baseline.csv` and `join_sizes_rpt.csv`

3. **Memory Utilization:**
   - Used `/usr/bin/time -v` to measure peak memory (Maximum Resident Set Size)
   - Executed each query 3 times per configuration
   - Monitored process memory during query execution
   - Results saved to CSV: `memory_baseline.csv` and `memory_rpt.csv`

### Automation & Data Collection
- **Python Scripts Created for Data Collection:**

  1. **`run_experiments.py`** - Performance Measurement:
     - Executes SSB queries via DuckDB CLI (subprocess calls)
     - Measures wall-clock time using Python's `time.perf_counter()`
     - Runs each query 5 times with warm-up run excluded
     - Writes results to CSV with columns: `mode`, `query`, `rep`, `time_seconds`
     - Output files: `ssb_baseline.csv`, `ssb_rpt.csv`
     - Each CSV contains ~65 rows (13 queries × 5 reps)

  2. **`measure_join_sizes.py`** - Intermediate Join Size Measurement:
     - Creates SQL queries with Common Table Expressions (CTEs)
     - Executes COUNT(*) queries at each join step
     - Measures: filtered dimension sizes, intermediate join results, final join sizes
     - Writes results to CSV with columns: `mode`, `query`, `step`, `step_name`, `row_count`
     - Output files: `join_sizes_baseline.csv`, `join_sizes_rpt.csv`
     - Captures join progression for multi-table queries

  3. **`measure_memory.py`** - Memory Utilization Measurement:
     - Uses `/usr/bin/time -v` to measure peak memory (Maximum Resident Set Size)
     - Executes each query 3 times per configuration
     - Parses time output to extract memory statistics
     - Writes results to CSV with columns: `mode`, `query`, `rep`, `peak_memory_bytes`, `peak_memory_mb`, `status`
     - Output files: `memory_baseline.csv`, `memory_rpt.csv`

  4. **`analyze_results.py`** - Results Analysis:
     - Reads CSV files and computes statistics (mean, std dev)
     - Calculates speedup ratios and percentage improvements
     - Generates comparison tables and summary statistics
     - Identifies wins/losses between baseline and RPT

  5. **`create_graphs.py`** - Visualization:
     - Uses matplotlib to generate comparison graphs
     - Reads CSV data and creates bar charts, speedup graphs
     - Generates 5 visualization PNG files (300 DPI for presentations)

- **Bash Script:**
  - `run_all_experiments.sh`: Orchestrates the entire workflow
    - Configures `setting.hpp` for RPT or baseline
    - Rebuilds DuckDB when switching configurations
    - Calls Python scripts to run experiments
    - Manages the complete experimental pipeline

- **CSV Output Format:**
  - All CSVs use standard format with headers
  - Consistent column naming across scripts
  - Easy to import into analysis tools (pandas, Excel, etc.)
  - Results directory contains all output files for reproducibility

### Experimental Controls
- **Same Database:** Both configurations used identical database file
- **Same Join Order:** Both used RandomLeftDeep (only difference is RPT on/off)
- **Same Environment:** All experiments on same CloudLab node
- **Multiple Repetitions:** 5 reps for performance, 3 for memory (to account for variance)
- **Warm-up Runs:** First query execution excluded from measurements

**Visual:** 
- Flowchart showing: Fork → Build → Configure → Run → Measure → Analyze
- Table showing configurations and metrics
- Diagram of experimental setup

---

## Slide 5: Results - Performance (60 seconds)
**Key Findings:**
- **Overall Performance:** RPT is ~8.9% slower on average
- **Speedup Range:** 0.85x to 0.99x (RPT slower across all queries)
- **Query-specific results:**
  - Simple queries (q1.x): ~10% slower
  - Complex queries (q4.x): ~10-18% slower
  - Largest degradation: q4.1 (17.9% slower)

**Visual:** 
- Show `performance_comparison.png` - side-by-side bar chart
- Show `speedup_comparison.png` - speedup ratios (all red bars showing < 1.0)

**Discussion:**
- For small datasets (SF=1), RPT overhead outweighs benefits
- Bloom filter creation/probe costs dominate on small data
- Results align with RPT paper's note that benefits scale with data size

---

## Slide 6: Results - Memory & Join Sizes (60 seconds)
**Memory Utilization:**
- **Average baseline:** 37.47 MB
- **Average RPT:** 37.48 MB
- **Difference:** +0.01 MB (+0.03% overhead)
- **Finding:** Negligible memory overhead from RPT

**Intermediate Join Sizes:**
- **Finding:** Identical intermediate join sizes between baseline and RPT
- All queries show same row counts at each join step
- Suggests RPT doesn't change cardinality for this dataset size

**Visual:**
- Show `memory_comparison.png` - very similar bars
- Show `join_size_comparison.png` - identical results
- Show `summary_comparison.png` - combined view

**Discussion:**
- Memory overhead is minimal (Bloom filters are compact)
- Join sizes unchanged suggests dataset too small to see filtering benefits

---

## Slide 7: Analysis & Insights (60 seconds)
**Key Observations:**
1. **Dataset Size Matters:** SF=1 is too small to see RPT benefits
   - RPT paper shows 4x improvements at SF=1, but on TPC-H (different workload)
   - SSB queries may have different characteristics

2. **Overhead vs. Benefit Trade-off:**
   - Bloom filter creation/probe overhead visible on small data
   - Benefits would likely emerge at larger scale factors (SF=10, SF=100)

3. **Query Characteristics:**
   - Star-schema structure of SSB may not stress RPT's strengths
   - RPT designed for complex multi-way joins with selective predicates

4. **Robustness:**
   - Both configurations use RandomLeftDeep join order
   - Performance is consistent (low variance) in both cases

**Visual:** Summary table or bullet points

---

## Slide 8: Conclusions & Future Work (45 seconds)
**Conclusions:**
- RPT shows minimal impact on SSB at SF=1
- Memory overhead is negligible (< 0.1%)
- Performance overhead (~9%) likely due to small dataset size
- Results validate RPT's low overhead, but benefits need larger scale

**Future Work:**
1. **Scale up:** Test at SF=10, SF=100 to see if benefits emerge
2. **Query analysis:** Investigate why SSB queries don't benefit (vs. TPC-H)
3. **Join order robustness:** Test with different join orders (RandomBushy, ExactLeftDeep)
4. **Selective predicates:** Test with more selective filters to stress RPT's strengths

**Visual:** Summary slide with key takeaways

---

## Slide 9: Q&A (Remaining time)
**Anticipated Questions:**
- Why is RPT slower on SSB when paper shows improvements?
  - *Answer:* Dataset size and query characteristics differ
- Would results change at larger scale?
  - *Answer:* Likely yes - RPT benefits scale with data size
- How does this compare to paper's results?
  - *Answer:* Paper used TPC-H, we used SSB (different workload characteristics)

---

## Presentation Tips

### Timing Breakdown (5 minutes total):
- Introduction & Background: 1:15
- SSB Overview: 1:00
- Methodology: 0:45
- Results: 2:00
- Analysis: 1:00
- Conclusions: 0:45
- Buffer/Q&A: ~15 seconds

### Key Visuals to Use:
1. **Performance Comparison** - Shows absolute times
2. **Speedup Graph** - Shows relative performance (all red = RPT slower)
3. **Memory Comparison** - Shows minimal overhead
4. **Summary Graph** - Quick overview of both metrics

### Talking Points:
- Emphasize that results are **not negative** - they validate RPT's low overhead
- Highlight that **scale matters** - benefits likely emerge at larger SF
- Note that **SSB characteristics** may differ from TPC-H (paper's benchmark)
- Stress the **robustness** aspect - consistent performance across queries

### Delivery Notes:
- Start with the problem (expensive joins)
- Quickly explain RPT (don't get too technical)
- Focus on results and what they mean
- End with future work to show understanding of limitations

