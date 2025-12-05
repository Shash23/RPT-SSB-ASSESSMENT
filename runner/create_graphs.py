#!/usr/bin/env python3
"""
Create visualization graphs comparing baseline vs RPT for SSB experiments.
Generates graphs for performance, join sizes, and memory utilization.
"""

import csv
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from pathlib import Path
from collections import defaultdict
from statistics import mean
import numpy as np

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
                step_name = row['step_name']
                row_count = int(row['row_count'])
                sizes_dict[query][step_name] = row_count
    
    return baseline_sizes, rpt_sizes

def load_memory_data(baseline_file, rpt_file):
    """Load memory utilization data."""
    baseline_memory = defaultdict(list)
    rpt_memory = defaultdict(list)
    
    for filename, memory_dict in [(baseline_file, baseline_memory), (rpt_file, rpt_memory)]:
        if not Path(filename).exists():
            continue
        with open(filename, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row['status'] == 'success' and row['peak_memory_mb'] != '-1':
                    query = row['query']
                    memory_mb = float(row['peak_memory_mb'])
                    memory_dict[query].append(memory_mb)
    
    # Calculate averages
    baseline_avg = {q: mean(baseline_memory[q]) for q in baseline_memory}
    rpt_avg = {q: mean(rpt_memory[q]) for q in rpt_memory}
    
    return baseline_avg, rpt_avg

def create_performance_graph(baseline_avg, rpt_avg, output_file):
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
    ax.set_title('SSB Query Performance: Baseline vs RPT', fontsize=14, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(queries, rotation=45, ha='right')
    ax.legend(fontsize=11)
    ax.grid(True, alpha=0.3, axis='y')
    
    # Add value labels on bars
    for bars in [bars1, bars2]:
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{height:.2f}',
                   ha='center', va='bottom', fontsize=8)
    
    plt.tight_layout()
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Created performance graph: {output_file}")

def create_speedup_graph(baseline_avg, rpt_avg, output_file):
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
    colors = ['#27ae60' if s > 1.0 else '#e74c3c' if s < 1.0 else '#95a5a6' for s in speedups]
    
    fig, ax = plt.subplots(figsize=(14, 8))
    
    bars = ax.bar(x, speedups, color=colors, alpha=0.8)
    
    # Add horizontal line at 1.0
    ax.axhline(y=1.0, color='black', linestyle='--', linewidth=1, alpha=0.5)
    
    ax.set_xlabel('Query', fontsize=12, fontweight='bold')
    ax.set_ylabel('Speedup (Baseline / RPT)', fontsize=12, fontweight='bold')
    ax.set_title('Performance Speedup: Baseline vs RPT\n(Speedup > 1.0 means RPT is faster)', 
                 fontsize=14, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(queries, rotation=45, ha='right')
    ax.grid(True, alpha=0.3, axis='y')
    
    # Add value labels
    for i, (bar, speedup) in enumerate(zip(bars, speedups)):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
               f'{speedup:.3f}x',
               ha='center', va='bottom' if speedup > 1.0 else 'top', fontsize=9)
    
    # Add legend
    green_patch = mpatches.Patch(color='#27ae60', label='RPT Faster')
    red_patch = mpatches.Patch(color='#e74c3c', label='RPT Slower')
    gray_patch = mpatches.Patch(color='#95a5a6', label='Equal')
    ax.legend(handles=[green_patch, red_patch, gray_patch], fontsize=10)
    
    plt.tight_layout()
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Created speedup graph: {output_file}")

def create_memory_graph(baseline_avg, rpt_avg, output_file):
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
    ax.set_title('Memory Utilization: Baseline vs RPT', fontsize=14, fontweight='bold')
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

def create_join_size_graph(baseline_sizes, rpt_sizes, output_file):
    """Create intermediate join size comparison graph."""
    # Get queries that have join size data
    queries = sorted(set(baseline_sizes.keys()) | set(rpt_sizes.keys()))
    
    if not queries:
        print("No join size data available, skipping join size graph")
        return
    
    # For each query, get the final join size
    baseline_final = []
    rpt_final = []
    query_labels = []
    
    for q in queries:
        if q in baseline_sizes and q in rpt_sizes:
            # Get the final join step (usually "join_final" or last step)
            baseline_steps = sorted(baseline_sizes[q].items(), key=lambda x: x[0])
            rpt_steps = sorted(rpt_sizes[q].items(), key=lambda x: x[0])
            
            if baseline_steps and rpt_steps:
                baseline_final.append(baseline_steps[-1][1])
                rpt_final.append(rpt_steps[-1][1])
                query_labels.append(q)
    
    if not query_labels:
        print("No valid join size data, skipping join size graph")
        return
    
    x = np.arange(len(query_labels))
    width = 0.35
    
    fig, ax = plt.subplots(figsize=(14, 8))
    
    bars1 = ax.bar(x - width/2, baseline_final, width, label='Baseline (no RPT)', 
                    color='#3498db', alpha=0.8)
    bars2 = ax.bar(x + width/2, rpt_final, width, label='RPT', 
                    color='#e74c3c', alpha=0.8)
    
    ax.set_xlabel('Query', fontsize=12, fontweight='bold')
    ax.set_ylabel('Final Join Result Size (rows)', fontsize=12, fontweight='bold')
    ax.set_title('Intermediate Join Sizes: Baseline vs RPT\n(Final Join Result)', 
                 fontsize=14, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(query_labels, rotation=45, ha='right')
    ax.legend(fontsize=11)
    ax.grid(True, alpha=0.3, axis='y')
    
    # Add value labels
    for bars in [bars1, bars2]:
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{int(height):,}',
                   ha='center', va='bottom', fontsize=8)
    
    plt.tight_layout()
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Created join size graph: {output_file}")

def create_summary_graph(baseline_avg, rpt_avg, baseline_mem, rpt_mem, output_file):
    """Create a summary graph with performance and memory."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
    
    queries = sorted(set(baseline_avg.keys()) | set(rpt_avg.keys()))
    x = np.arange(len(queries))
    width = 0.35
    
    # Performance subplot
    baseline_perf = [baseline_avg.get(q, 0) * 1000 for q in queries]
    rpt_perf = [rpt_avg.get(q, 0) * 1000 for q in queries]
    
    ax1.bar(x - width/2, baseline_perf, width, label='Baseline', color='#3498db', alpha=0.8)
    ax1.bar(x + width/2, rpt_perf, width, label='RPT', color='#e74c3c', alpha=0.8)
    ax1.set_xlabel('Query', fontweight='bold')
    ax1.set_ylabel('Execution Time (ms)', fontweight='bold')
    ax1.set_title('Performance Comparison', fontweight='bold')
    ax1.set_xticks(x)
    ax1.set_xticklabels(queries, rotation=45, ha='right', fontsize=9)
    ax1.legend()
    ax1.grid(True, alpha=0.3, axis='y')
    
    # Memory subplot
    baseline_mem_vals = [baseline_mem.get(q, 0) for q in queries]
    rpt_mem_vals = [rpt_mem.get(q, 0) for q in queries]
    
    ax2.bar(x - width/2, baseline_mem_vals, width, label='Baseline', color='#3498db', alpha=0.8)
    ax2.bar(x + width/2, rpt_mem_vals, width, label='RPT', color='#e74c3c', alpha=0.8)
    ax2.set_xlabel('Query', fontweight='bold')
    ax2.set_ylabel('Peak Memory (MB)', fontweight='bold')
    ax2.set_title('Memory Utilization Comparison', fontweight='bold')
    ax2.set_xticks(x)
    ax2.set_xticklabels(queries, rotation=45, ha='right', fontsize=9)
    ax2.legend()
    ax2.grid(True, alpha=0.3, axis='y')
    
    plt.suptitle('SSB Benchmark: Baseline vs RPT Summary', fontsize=16, fontweight='bold', y=1.02)
    plt.tight_layout()
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Created summary graph: {output_file}")

def main():
    results_dir = Path("../results")
    graphs_dir = results_dir / "graphs"
    graphs_dir.mkdir(exist_ok=True)
    
    # Load data
    print("Loading data...")
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
                            graphs_dir / "performance_comparison.png")
    
    create_speedup_graph(baseline_perf, rpt_perf, 
                        graphs_dir / "speedup_comparison.png")
    
    if baseline_mem and rpt_mem:
        create_memory_graph(baseline_mem, rpt_mem, 
                           graphs_dir / "memory_comparison.png")
    
    if baseline_joins and rpt_joins:
        create_join_size_graph(baseline_joins, rpt_joins, 
                              graphs_dir / "join_size_comparison.png")
    
    if baseline_mem and rpt_mem:
        create_summary_graph(baseline_perf, rpt_perf, baseline_mem, rpt_mem,
                            graphs_dir / "summary_comparison.png")
    
    print(f"\nAll graphs saved to: {graphs_dir}")
    print("\nGenerated graphs:")
    print("  1. performance_comparison.png - Execution time comparison")
    print("  2. speedup_comparison.png - Speedup ratio (Baseline/RPT)")
    print("  3. memory_comparison.png - Memory utilization comparison")
    print("  4. join_size_comparison.png - Intermediate join sizes")
    print("  5. summary_comparison.png - Combined performance and memory")

if __name__ == "__main__":
    main()

