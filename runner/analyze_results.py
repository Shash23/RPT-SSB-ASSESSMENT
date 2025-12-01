#!/usr/bin/env python3
"""
Analyze and compare baseline vs RPT experiment results.
Usage: python3 analyze_results.py [baseline_csv] [rpt_csv]
"""

import csv
import sys
from collections import defaultdict
from pathlib import Path
from statistics import mean, stdev

def load_results(csv_file):
    """Load results from CSV file."""
    times = defaultdict(list)
    
    with open(csv_file, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            query = row['query']
            time = float(row['time_seconds'])
            times[query].append(time)
    
    return times

def analyze_results(baseline_file, rpt_file):
    """Compare baseline and RPT results."""
    baseline_times = load_results(baseline_file)
    rpt_times = load_results(rpt_file)
    
    # Get all queries (should be the same)
    all_queries = sorted(set(baseline_times.keys()) | set(rpt_times.keys()))
    
    print("=" * 80)
    print("RPT vs Baseline Performance Analysis")
    print("=" * 80)
    print(f"{'Query':<10} {'Baseline Avg':<15} {'RPT Avg':<15} {'Speedup':<10} {'Improvement':<12}")
    print("-" * 80)
    
    total_baseline = 0
    total_rpt = 0
    
    for query in all_queries:
        if query not in baseline_times or query not in rpt_times:
            print(f"{query:<10} {'MISSING':<15} {'MISSING':<15}")
            continue
        
        baseline_avg = mean(baseline_times[query])
        rpt_avg = mean(rpt_times[query])
        baseline_std = stdev(baseline_times[query]) if len(baseline_times[query]) > 1 else 0
        rpt_std = stdev(rpt_times[query]) if len(rpt_times[query]) > 1 else 0
        
        speedup = baseline_avg / rpt_avg if rpt_avg > 0 else 0
        improvement = ((baseline_avg - rpt_avg) / baseline_avg * 100) if baseline_avg > 0 else 0
        
        total_baseline += baseline_avg
        total_rpt += rpt_avg
        
        # Format output
        speedup_str = f"{speedup:.3f}x"
        improvement_str = f"{improvement:+.1f}%"
        
        if speedup > 1.0:
            speedup_str = f"\033[92m{speedup_str}\033[0m"  # Green
        elif speedup < 1.0:
            speedup_str = f"\033[91m{speedup_str}\033[0m"  # Red
        
        print(f"{query:<10} {baseline_avg:>12.6f}s {rpt_avg:>12.6f}s {speedup_str:>10} {improvement_str:>12}")
    
    print("-" * 80)
    overall_speedup = total_baseline / total_rpt if total_rpt > 0 else 0
    overall_improvement = ((total_baseline - total_rpt) / total_baseline * 100) if total_baseline > 0 else 0
    print(f"{'TOTAL':<10} {total_baseline:>12.6f}s {total_rpt:>12.6f}s {overall_speedup:>10.3f}x {overall_improvement:>+11.1f}%")
    print("=" * 80)
    
    # Summary statistics
    print("\nSummary Statistics:")
    print(f"  Total queries: {len(all_queries)}")
    print(f"  Overall speedup: {overall_speedup:.3f}x")
    print(f"  Overall improvement: {overall_improvement:+.1f}%")
    
    # Count wins/losses
    wins = sum(1 for q in all_queries 
               if q in baseline_times and q in rpt_times 
               and mean(baseline_times[q]) > mean(rpt_times[q]))
    losses = sum(1 for q in all_queries 
                 if q in baseline_times and q in rpt_times 
                 and mean(baseline_times[q]) < mean(rpt_times[q]))
    ties = len(all_queries) - wins - losses
    
    print(f"  Queries where RPT is faster: {wins}")
    print(f"  Queries where RPT is slower: {losses}")
    print(f"  Queries with no significant difference: {ties}")

def main():
    if len(sys.argv) < 3:
        # Default paths
        script_dir = Path(__file__).parent
        baseline_file = script_dir.parent / "results" / "ssb_baseline.csv"
        rpt_file = script_dir.parent / "results" / "ssb_rpt.csv"
    else:
        baseline_file = Path(sys.argv[1])
        rpt_file = Path(sys.argv[2])
    
    if not baseline_file.exists():
        print(f"Error: Baseline results file not found: {baseline_file}")
        sys.exit(1)
    
    if not rpt_file.exists():
        print(f"Error: RPT results file not found: {rpt_file}")
        sys.exit(1)
    
    analyze_results(baseline_file, rpt_file)

if __name__ == "__main__":
    main()

