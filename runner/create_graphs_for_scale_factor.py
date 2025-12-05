#!/usr/bin/env python3
"""
Create visualization graphs for a specific scale factor.
Usage: python3 create_graphs_for_scale_factor.py <scale_factor>
Example: python3 create_graphs_for_scale_factor.py 5
"""

import csv
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from pathlib import Path
from collections import defaultdict
from statistics import mean
import numpy as np
import sys

# Set style
plt.style.use('seaborn-v0_8-darkgrid' if 'seaborn-v0_8-darkgrid' in plt.style.available else 'default')
plt.rcParams['figure.figsize'] = (14, 10)
plt.rcParams['font.size'] = 10

def load_performance_data(baseline_file, rpt_file):
    """Load performance timing data."""
    baseline_times = defaultdict(list)
    rpt_times = defaultdict(list)
    
    for filename, times_dict in [(baseline_file, baseline_times), (rpt_file, rpt_times)]:
        with open(filename, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                query = row['query']
                time_val = float(row['time_seconds'])
                times_dict[query].append(time_val)
    
    # Calculate averages
    baseline_avg = {q: mean(baseline_times[q]) for q in baseline_times}
    rpt_avg = {q: mean(rpt_times[q]) for q in rpt_times}
    
    return baseline_avg, rpt_avg

def load_join_size_data(baseline_file, rpt_file):
    """Load intermediate join size data."""
    baseline_sizes = defaultdict(dict)
    rpt_sizes = defaultdict(dict)
    
    for filename, sizes_dict in [(baseline_file, baseline_sizes), (rpt_file, rpt_sizes)]:
        if not Path(filename).exists():
            continue
        with open(filename, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                query = row['query']
                step = row['step']
                size = int(row['row_count'])
                sizes_dict[query][step] = size
    
    return baseline_sizes, rpt_sizes

def load_memory_data(baseline_file, rpt_file):
    """Load memory utilization data."""
    baseline_mem = defaultdict(list)
    rpt_mem = defaultdict(list)
    
    for filename, mem_dict in [(baseline_file, baseline_mem), (rpt_file, rpt_mem)]:
        if not Path(filename).exists():
            continue
        with open(filename, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                query = row['query']
                # Handle both peak_memory_mb and peak_memory_kb
                if 'peak_memory_mb' in row:
                    mem_val = float(row['peak_memory_mb'])
                elif 'peak_memory_kb' in row:
                    mem_val = float(row['peak_memory_kb']) / 1024
                else:
                    continue
                mem_dict[query].append(mem_val)
    
    baseline_avg = {q: mean(baseline_mem[q]) for q in baseline_mem}
    rpt_avg = {q: mean(rpt_mem[q]) for q in rpt_mem}
    
    return baseline_avg, rpt_avg

def create_performance_graph(baseline_avg, rpt_avg, output_file, scale_factor):
    """Create performance comparison graph."""
    queries = sorted(set(baseline_avg.keys()) | set(rpt_avg.keys()))
    baseline_values = [baseline_avg.get(q, 0) * 1000 for q in queries]  # Convert to ms
    rpt_values = [rpt_avg.get(q, 0) * 1000 for q in queries]
    
    x = np.arange(len(queries))
    width = 0.35
    
    fig, ax = plt.subplots(figsize=(14, 8))
    
    bars1 = ax.bar(x - width/2, baseline_values, width, label='Baseline (no RPT)', 
                    color='#3498db', alpha=0.8)
    bars2 = ax.bar(x + width/2, rpt_values, width, label='RPT', 
                    color='#e74c3c', alpha=0.8)
    
    ax.set_xlabel('Query', fontsize=12, fontweight='bold')
    ax.set_ylabel('Execution Time (ms)', fontsize=12, fontweight='bold')
    ax.set_title(f'SSB Query Performance: Baseline vs RPT (SF={scale_factor})', fontsize=14, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(queries, rotation=45, ha='right')
    ax.legend(fontsize=11)
    ax.grid(True, alpha=0.3, axis='y')
    
    # Add value labels on bars
    for bars in [bars1, bars2]:
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{height:.1f}',
                   ha='center', va='bottom', fontsize=8)
    
    plt.tight_layout()
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Created performance graph: {output_file}")

def create_speedup_graph(baseline_avg, rpt_avg, output_file, scale_factor):
    """Create speedup comparison graph."""
    queries = sorted(set(baseline_avg.keys()) | set(rpt_avg.keys()))
    speedups = []
    for q in queries:
        if q in baseline_avg and q in rpt_avg and rpt_avg[q] > 0:
            speedup = baseline_avg[q] / rpt_avg[q]
            speedups.append(speedup)
        else:
            speedups.append(1.0)
    
    x = np.arange(len(queries))
    
    fig, ax = plt.subplots(figsize=(14, 8))
    
    bars = ax.bar(x, speedups, color='#2ecc71', alpha=0.8)
    
    # Add horizontal line at 1.0x
    ax.axhline(y=1.0, color='black', linestyle='--', linewidth=1, alpha=0.5)
    
    ax.set_xlabel('Query', fontsize=12, fontweight='bold')
    ax.set_ylabel('Speedup (Baseline / RPT)', fontsize=12, fontweight='bold')
    ax.set_title(f'Query Speedup: RPT vs Baseline (SF={scale_factor})', fontsize=14, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(queries, rotation=45, ha='right')
    ax.grid(True, alpha=0.3, axis='y')
    
    # Add value labels
    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
               f'{height:.2f}x',
               ha='center', va='bottom', fontsize=9, fontweight='bold')
    
    plt.tight_layout()
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Created speedup graph: {output_file}")

def create_memory_graph(baseline_avg, rpt_avg, output_file, scale_factor):
    """Create memory utilization comparison graph."""
    queries = sorted(set(baseline_avg.keys()) | set(rpt_avg.keys()))
    baseline_values = [baseline_avg.get(q, 0) for q in queries]
    rpt_values = [rpt_avg.get(q, 0) for q in queries]
    
    x = np.arange(len(queries))
    width = 0.35
    
    fig, ax = plt.subplots(figsize=(14, 8))
    
    bars1 = ax.bar(x - width/2, baseline_values, width, label='Baseline (no RPT)', 
                    color='#3498db', alpha=0.8)
    bars2 = ax.bar(x + width/2, rpt_values, width, label='RPT', 
                    color='#e74c3c', alpha=0.8)
    
    ax.set_xlabel('Query', fontsize=12, fontweight='bold')
    ax.set_ylabel('Peak Memory Usage (MB)', fontsize=12, fontweight='bold')
    ax.set_title(f'Memory Utilization: Baseline vs RPT (SF={scale_factor})', fontsize=14, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(queries, rotation=45, ha='right')
    ax.legend(fontsize=11)
    ax.grid(True, alpha=0.3, axis='y')
    
    # Add value labels
    for bars in [bars1, bars2]:
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{height:.1f}',
                   ha='center', va='bottom', fontsize=8)
    
    plt.tight_layout()
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Created memory graph: {output_file}")

def create_join_size_graph(baseline_sizes, rpt_sizes, output_file, scale_factor):
    """Create intermediate join size comparison graph."""
    # Get all queries
    all_queries = sorted(set(baseline_sizes.keys()) | set(rpt_sizes.keys()))
    
    if not all_queries:
        print("No join size data available")
        return
    
    # For each query, plot the join sizes at each step
    fig, axes = plt.subplots(len(all_queries), 1, figsize=(14, 4 * len(all_queries)))
    if len(all_queries) == 1:
        axes = [axes]
    
    for idx, query in enumerate(all_queries):
        ax = axes[idx]
        
        if query in baseline_sizes and query in rpt_sizes:
            steps = sorted(set(baseline_sizes[query].keys()) | set(rpt_sizes[query].keys()))
            baseline_vals = [baseline_sizes[query].get(s, 0) for s in steps]
            rpt_vals = [rpt_sizes[query].get(s, 0) for s in steps]
            
            x = np.arange(len(steps))
            width = 0.35
            
            bars1 = ax.bar(x - width/2, baseline_vals, width, label='Baseline', 
                          color='#3498db', alpha=0.8)
            bars2 = ax.bar(x + width/2, rpt_vals, width, label='RPT', 
                          color='#e74c3c', alpha=0.8)
            
            ax.set_ylabel('Row Count', fontsize=10)
            ax.set_title(f'{query} - Intermediate Join Sizes', fontsize=11, fontweight='bold')
            ax.set_xticks(x)
            ax.set_xticklabels([f'Step {s}' for s in steps], rotation=45, ha='right')
            ax.legend()
            ax.grid(True, alpha=0.3, axis='y')
            ax.set_yscale('log')
    
    plt.suptitle(f'Intermediate Join Size Comparison (SF={scale_factor})', 
                 fontsize=14, fontweight='bold', y=0.995)
    plt.tight_layout()
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Created join size graph: {output_file}")

def create_summary_graph(baseline_avg, rpt_avg, baseline_mem, rpt_mem, output_file, scale_factor):
    """Create combined summary graph."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
    
    queries = sorted(set(baseline_avg.keys()) | set(rpt_avg.keys()))
    x = np.arange(len(queries))
    width = 0.35
    
    # Performance subplot
    baseline_perf = [baseline_avg.get(q, 0) * 1000 for q in queries]
    rpt_perf = [rpt_avg.get(q, 0) * 1000 for q in queries]
    
    ax1.bar(x - width/2, baseline_perf, width, label='Baseline', color='#3498db', alpha=0.8)
    ax1.bar(x + width/2, rpt_perf, width, label='RPT', color='#e74c3c', alpha=0.8)
    ax1.set_xlabel('Query', fontsize=11, fontweight='bold')
    ax1.set_ylabel('Execution Time (ms)', fontsize=11, fontweight='bold')
    ax1.set_title('Performance', fontsize=12, fontweight='bold')
    ax1.set_xticks(x)
    ax1.set_xticklabels(queries, rotation=45, ha='right')
    ax1.legend()
    ax1.grid(True, alpha=0.3, axis='y')
    
    # Memory subplot
    baseline_mem_vals = [baseline_mem.get(q, 0) for q in queries]
    rpt_mem_vals = [rpt_mem.get(q, 0) for q in queries]
    
    ax2.bar(x - width/2, baseline_mem_vals, width, label='Baseline', color='#3498db', alpha=0.8)
    ax2.bar(x + width/2, rpt_mem_vals, width, label='RPT', color='#e74c3c', alpha=0.8)
    ax2.set_xlabel('Query', fontsize=11, fontweight='bold')
    ax2.set_ylabel('Peak Memory (MB)', fontsize=11, fontweight='bold')
    ax2.set_title('Memory Utilization', fontsize=12, fontweight='bold')
    ax2.set_xticks(x)
    ax2.set_xticklabels(queries, rotation=45, ha='right')
    ax2.legend()
    ax2.grid(True, alpha=0.3, axis='y')
    
    plt.suptitle(f'Performance and Memory Summary (SF={scale_factor})', 
                 fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Created summary graph: {output_file}")

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 create_graphs_for_scale_factor.py <scale_factor>")
        print("Example: python3 create_graphs_for_scale_factor.py 5")
        sys.exit(1)
    
    scale_factor = sys.argv[1]
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    results_dir = project_root / "results" / f"sf{scale_factor}"
    graphs_dir = project_root / "results" / "graphs" / f"sf{scale_factor}"
    graphs_dir.mkdir(parents=True, exist_ok=True)
    
    # Load data
    print(f"Loading data for SF={scale_factor}...")
    baseline_perf, rpt_perf = load_performance_data(
        results_dir / "ssb_baseline.csv",
        results_dir / "ssb_rpt.csv"
    )
    
    baseline_mem, rpt_mem = load_memory_data(
        results_dir / "memory_baseline.csv",
        results_dir / "memory_rpt.csv"
    )
    
    baseline_joins, rpt_joins = load_join_size_data(
        results_dir / "join_sizes_baseline.csv",
        results_dir / "join_sizes_rpt.csv"
    )
    
    print("Creating graphs...")
    
    # Create graphs
    create_performance_graph(baseline_perf, rpt_perf, 
                            graphs_dir / "performance_comparison.png", scale_factor)
    
    create_speedup_graph(baseline_perf, rpt_perf, 
                        graphs_dir / "speedup_comparison.png", scale_factor)
    
    if baseline_mem and rpt_mem:
        create_memory_graph(baseline_mem, rpt_mem, 
                           graphs_dir / "memory_comparison.png", scale_factor)
    
    if baseline_joins and rpt_joins:
        create_join_size_graph(baseline_joins, rpt_joins, 
                              graphs_dir / "join_size_comparison.png", scale_factor)
    
    if baseline_mem and rpt_mem:
        create_summary_graph(baseline_perf, rpt_perf, baseline_mem, rpt_mem,
                            graphs_dir / "summary_comparison.png", scale_factor)
    
    print(f"\nAll graphs saved to: {graphs_dir}")
    print("\nGenerated graphs:")
    print("  1. performance_comparison.png - Execution time comparison")
    print("  2. speedup_comparison.png - Speedup ratio (Baseline/RPT)")
    print("  3. memory_comparison.png - Memory utilization comparison")
    print("  4. join_size_comparison.png - Intermediate join sizes")
    print("  5. summary_comparison.png - Combined performance and memory")

if __name__ == "__main__":
    main()

