# SSB Benchmark Visualization Graphs

This directory contains visualization graphs comparing Baseline (non-RPT) vs RPT performance for the SSB benchmark.

## Generated Graphs

### 1. `performance_comparison.png`
**Execution Time Comparison**
- Shows side-by-side bar chart of execution times for each SSB query
- Baseline (blue) vs RPT (red)
- Times displayed in milliseconds
- Useful for seeing absolute performance differences

### 2. `speedup_comparison.png`
**Performance Speedup Ratio**
- Shows speedup ratio: Baseline time / RPT time
- Speedup > 1.0 means RPT is faster (green bars)
- Speedup < 1.0 means RPT is slower (red bars)
- Speedup = 1.0 means equal performance (gray bars)
- Useful for understanding relative performance improvements/degradations

### 3. `memory_comparison.png`
**Memory Utilization Comparison**
- Shows peak memory usage for each query
- Baseline (blue) vs RPT (red)
- Memory displayed in MB
- Useful for understanding memory overhead of RPT

### 4. `join_size_comparison.png`
**Intermediate Join Sizes**
- Shows final join result sizes (row counts)
- Baseline (blue) vs RPT (red)
- Useful for understanding if RPT affects intermediate result cardinalities

### 5. `summary_comparison.png`
**Combined Summary**
- Two-panel graph showing both performance and memory
- Left panel: Execution time comparison
- Right panel: Memory utilization comparison
- Useful for a quick overview of both metrics

## Key Findings

Based on the SSB benchmark results (SF=1):

1. **Performance**: RPT shows minimal performance difference (~8.9% slower on average)
2. **Memory**: RPT has negligible memory overhead (~0.03% increase)
3. **Join Sizes**: Intermediate join sizes are identical between baseline and RPT
4. **Overall**: For small datasets (SF=1), RPT overhead outweighs benefits

## Graph Details

- **Resolution**: 300 DPI (high quality for presentations)
- **Format**: PNG
- **Color Scheme**: 
  - Blue (#3498db): Baseline
  - Red (#e74c3c): RPT
  - Green (#27ae60): RPT faster (speedup > 1.0)

## Regenerating Graphs

To regenerate the graphs with updated data:

```bash
cd /home/ubuntu/RPT-SSB-ASSESSMENT/runner
python3 create_graphs.py
```

The script automatically reads from:
- `results/ssb_baseline.csv` and `results/ssb_rpt.csv` (performance)
- `results/memory_baseline.csv` and `results/memory_rpt.csv` (memory)
- `results/join_sizes_baseline.csv` and `results/join_sizes_rpt.csv` (join sizes)

