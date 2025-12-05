#!/usr/bin/env python3
"""
Measure memory utilization for SSB queries.
Uses /usr/bin/time to track peak memory usage during query execution.
"""

import argparse
import subprocess
import csv
import re
from pathlib import Path

# SSB query definitions (same as run_experiments.py)
QUERIES = {
    "q1.1": """
        SELECT sum(LO_EXTENDEDPRICE * LO_DISCOUNT) AS revenue
        FROM ssb.lineorder, ssb.date
        WHERE LO_ORDERDATE = D_DATEKEY
          AND D_YEAR = 1993
          AND LO_DISCOUNT BETWEEN 1 AND 3
          AND LO_QUANTITY < 25;
    """,
    "q1.2": """
        SELECT sum(LO_EXTENDEDPRICE * LO_DISCOUNT) AS revenue
        FROM ssb.lineorder, ssb.date
        WHERE LO_ORDERDATE = D_DATEKEY
          AND D_YEARMONTHNUM = 199401
          AND LO_DISCOUNT BETWEEN 4 AND 6
          AND LO_QUANTITY BETWEEN 26 AND 35;
    """,
    "q1.3": """
        SELECT sum(LO_EXTENDEDPRICE * LO_DISCOUNT) AS revenue
        FROM ssb.lineorder, ssb.date
        WHERE LO_ORDERDATE = D_DATEKEY
          AND D_WEEKNUMINYEAR = 6
          AND D_YEAR = 1994
          AND LO_DISCOUNT BETWEEN 5 AND 7
          AND LO_QUANTITY BETWEEN 26 AND 35;
    """,
    "q2.1": """
        SELECT sum(LO_REVENUE) AS sum_revenue, D_YEAR, P_BRAND1
        FROM ssb.lineorder, ssb.date, ssb.part, ssb.supplier
        WHERE LO_ORDERDATE = D_DATEKEY
          AND LO_PARTKEY = P_PARTKEY
          AND LO_SUPPKEY = S_SUPPKEY
          AND P_CATEGORY = 'MFGR#12'
          AND S_REGION = 'AMERICA'
        GROUP BY D_YEAR, P_BRAND1
        ORDER BY D_YEAR, P_BRAND1;
    """,
    "q2.2": """
        SELECT sum(LO_REVENUE) AS sum_revenue, D_YEAR, P_BRAND1
        FROM ssb.lineorder, ssb.date, ssb.part, ssb.supplier
        WHERE LO_ORDERDATE = D_DATEKEY
          AND LO_PARTKEY = P_PARTKEY
          AND LO_SUPPKEY = S_SUPPKEY
          AND P_BRAND1 BETWEEN 'MFGR#2221' AND 'MFGR#2228'
          AND S_REGION = 'ASIA'
        GROUP BY D_YEAR, P_BRAND1
        ORDER BY D_YEAR, P_BRAND1;
    """,
    "q2.3": """
        SELECT sum(LO_REVENUE) AS sum_revenue, D_YEAR, P_BRAND1
        FROM ssb.lineorder, ssb.date, ssb.part, ssb.supplier
        WHERE LO_ORDERDATE = D_DATEKEY
          AND LO_PARTKEY = P_PARTKEY
          AND LO_SUPPKEY = S_SUPPKEY
          AND P_BRAND1 = 'MFGR#2221'
          AND S_REGION = 'EUROPE'
        GROUP BY D_YEAR, P_BRAND1
        ORDER BY D_YEAR, P_BRAND1;
    """,
    "q3.1": """
        SELECT C_NATION, S_NATION, D_YEAR, sum(LO_REVENUE) AS revenue
        FROM ssb.customer, ssb.lineorder, ssb.supplier, ssb.date
        WHERE LO_CUSTKEY = C_CUSTKEY
          AND LO_SUPPKEY = S_SUPPKEY
          AND LO_ORDERDATE = D_DATEKEY
          AND C_REGION = 'ASIA'
          AND S_REGION = 'ASIA'
          AND D_YEAR BETWEEN 1992 AND 1997
        GROUP BY C_NATION, S_NATION, D_YEAR
        ORDER BY D_YEAR ASC, revenue DESC;
    """,
    "q3.2": """
        SELECT C_CITY, S_CITY, D_YEAR, sum(LO_REVENUE) AS revenue
        FROM ssb.customer, ssb.lineorder, ssb.supplier, ssb.date
        WHERE LO_CUSTKEY = C_CUSTKEY
          AND LO_SUPPKEY = S_SUPPKEY
          AND LO_ORDERDATE = D_DATEKEY
          AND C_NATION = 'UNITED STATES'
          AND S_NATION = 'UNITED STATES'
          AND D_YEAR BETWEEN 1992 AND 1997
        GROUP BY C_CITY, S_CITY, D_YEAR
        ORDER BY D_YEAR ASC, revenue DESC;
    """,
    "q3.3": """
        SELECT C_CITY, S_CITY, D_YEAR, sum(LO_REVENUE) AS revenue
        FROM ssb.customer, ssb.lineorder, ssb.supplier, ssb.date
        WHERE LO_CUSTKEY = C_CUSTKEY
          AND LO_SUPPKEY = S_SUPPKEY
          AND LO_ORDERDATE = D_DATEKEY
          AND (C_CITY = 'UNITED KI1' OR C_CITY = 'UNITED KI5')
          AND (S_CITY = 'UNITED KI1' OR S_CITY = 'UNITED KI5')
          AND D_YEAR BETWEEN 1992 AND 1997
        GROUP BY C_CITY, S_CITY, D_YEAR
        ORDER BY D_YEAR ASC, revenue DESC;
    """,
    "q3.4": """
        SELECT C_CITY, S_CITY, D_YEAR, sum(LO_REVENUE) AS revenue
        FROM ssb.customer, ssb.lineorder, ssb.supplier, ssb.date
        WHERE LO_CUSTKEY = C_CUSTKEY
          AND LO_SUPPKEY = S_SUPPKEY
          AND LO_ORDERDATE = D_DATEKEY
          AND (C_CITY = 'UNITED KI1' OR C_CITY = 'UNITED KI5')
          AND (S_CITY = 'UNITED KI1' OR S_CITY = 'UNITED KI5')
          AND D_YEARMONTH = 'Dec1997'
        GROUP BY C_CITY, S_CITY, D_YEAR
        ORDER BY D_YEAR ASC, revenue DESC;
    """,
    "q4.1": """
        SELECT D_YEAR, C_NATION,
               sum(LO_REVENUE - LO_SUPPLYCOST) AS profit
        FROM ssb.date, ssb.customer, ssb.supplier, ssb.part, ssb.lineorder
        WHERE LO_CUSTKEY = C_CUSTKEY
          AND LO_SUPPKEY = S_SUPPKEY
          AND LO_PARTKEY = P_PARTKEY
          AND LO_ORDERDATE = D_DATEKEY
          AND C_REGION = 'AMERICA'
          AND S_REGION = 'AMERICA'
          AND (P_MFGR = 'MFGR#1' OR P_MFGR = 'MFGR#2')
        GROUP BY D_YEAR, C_NATION
        ORDER BY D_YEAR, C_NATION;
    """,
    "q4.2": """
        SELECT D_YEAR, S_NATION, P_CATEGORY,
               sum(LO_REVENUE - LO_SUPPLYCOST) AS profit
        FROM ssb.date, ssb.customer, ssb.supplier, ssb.part, ssb.lineorder
        WHERE LO_CUSTKEY = C_CUSTKEY
          AND LO_SUPPKEY = S_SUPPKEY
          AND LO_PARTKEY = P_PARTKEY
          AND LO_ORDERDATE = D_DATEKEY
          AND C_REGION = 'AMERICA'
          AND S_REGION = 'AMERICA'
          AND D_YEAR IN (1997, 1998)
          AND (P_MFGR = 'MFGR#1' OR P_MFGR = 'MFGR#2')
        GROUP BY D_YEAR, S_NATION, P_CATEGORY
        ORDER BY D_YEAR, S_NATION, P_CATEGORY;
    """,
    "q4.3": """
        SELECT D_YEAR, S_CITY, P_BRAND1,
               sum(LO_REVENUE - LO_SUPPLYCOST) AS profit
        FROM ssb.date, ssb.customer, ssb.supplier, ssb.part, ssb.lineorder
        WHERE LO_CUSTKEY = C_CUSTKEY
          AND LO_SUPPKEY = S_SUPPKEY
          AND LO_PARTKEY = P_PARTKEY
          AND LO_ORDERDATE = D_DATEKEY
          AND C_REGION = 'AMERICA'
          AND S_NATION = 'UNITED STATES'
          AND D_YEAR IN (1997, 1998)
          AND P_CATEGORY = 'MFGR#14'
        GROUP BY D_YEAR, S_CITY, P_BRAND1
        ORDER BY D_YEAR, S_CITY, P_BRAND1;
    """,
}


def parse_time_output(stderr_output):
    """Parse /usr/bin/time output to extract memory statistics."""
    peak_memory_kb = None
    
    # Look for "Maximum resident set size (kbytes):" line
    for line in stderr_output.split('\n'):
        if 'Maximum resident set size' in line or 'Mmaximum resident set size' in line:
            # Extract number
            match = re.search(r'(\d+)', line)
            if match:
                peak_memory_kb = int(match.group(1))
                break
    
    return peak_memory_kb


def run_query_with_memory(bin_path, db_path, sql):
    """Run a query using /usr/bin/time to measure memory."""
    cmd = ["/usr/bin/time", "-v", bin_path, db_path, "-c", sql]
    
    try:
        result = subprocess.run(
            cmd,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE,
            text=True,
            timeout=300
        )
        
        if result.returncode != 0:
            return None, f"error: {result.stderr[:200]}"
        
        peak_memory_kb = parse_time_output(result.stderr)
        if peak_memory_kb is None:
            return None, "could not parse memory stats"
        
        peak_memory_bytes = peak_memory_kb * 1024
        return peak_memory_bytes, None
        
    except subprocess.TimeoutExpired:
        return None, "timeout"
    except FileNotFoundError:
        # /usr/bin/time not available, try alternative
        return run_query_with_memory_alt(bin_path, db_path, sql)
    except Exception as e:
        return None, f"exception: {str(e)}"


def run_query_with_memory_alt(bin_path, db_path, sql):
    """Alternative method: use /proc filesystem to monitor memory."""
    import os
    import time
    
    cmd = [bin_path, db_path, "-c", sql]
    
    try:
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE,
            preexec_fn=os.setsid
        )
        
        peak_memory = 0
        pid = process.pid
        
        # Monitor /proc/pid/status for VmRSS (Resident Set Size)
        while process.poll() is None:
            try:
                with open(f'/proc/{pid}/status', 'r') as f:
                    for line in f:
                        if line.startswith('VmRSS:'):
                            # Extract KB value
                            match = re.search(r'(\d+)', line)
                            if match:
                                memory_kb = int(match.group(1))
                                memory_bytes = memory_kb * 1024
                                if memory_bytes > peak_memory:
                                    peak_memory = memory_bytes
                            break
                time.sleep(0.1)  # Check every 100ms
            except (FileNotFoundError, ProcessLookupError):
                break
        
        process.wait()
        
        if process.returncode != 0:
            error = process.stderr.read().decode('utf-8', errors='ignore')[:200]
            return None, f"error: {error}"
        
        if peak_memory == 0:
            return None, "could not measure memory"
        
        return peak_memory, None
        
    except Exception as e:
        return None, f"exception: {str(e)}"


def main():
    parser = argparse.ArgumentParser(
        description="Measure memory utilization for SSB queries."
    )
    parser.add_argument("--mode", required=True,
                        help="Label for this run, e.g. baseline or rpt")
    parser.add_argument("--duckdb-bin", required=True,
                        help="Path to duckdb executable")
    parser.add_argument("--db", default="db/ssb.duckdb",
                        help="Path to DuckDB database file")
    parser.add_argument("--reps", type=int, default=3,
                        help="Number of repetitions per query")
    parser.add_argument("--out", default="memory_usage.csv",
                        help="Output CSV file")
    parser.add_argument("--queries", nargs="+", default=None,
                        help="Specific queries to run (default: all)")
    args = parser.parse_args()

    db_path = str(Path(args.db))
    bin_path = str(Path(args.duckdb_bin))

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    queries_to_run = args.queries if args.queries else list(QUERIES.keys())

    with out_path.open("w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["mode", "query", "rep", "peak_memory_bytes", "peak_memory_mb", "status"])

        for qname in queries_to_run:
            if qname not in QUERIES:
                print(f"Warning: Query {qname} not found, skipping")
                continue
                
            sql = QUERIES[qname]
            print(f"\nMeasuring memory for {args.mode} {qname}...")
            
            for rep in range(1, args.reps + 1):
                print(f"  Rep {rep}/{args.reps}...", end=" ", flush=True)
                peak_mem, status = run_query_with_memory(
                    bin_path, db_path, sql
                )
                
                if peak_mem is not None:
                    peak_mb = peak_mem / (1024 * 1024)
                    writer.writerow([
                        args.mode, qname, rep,
                        int(peak_mem), f"{peak_mb:.2f}",
                        "success"
                    ])
                    print(f"Peak: {peak_mb:.2f} MB")
                else:
                    writer.writerow([
                        args.mode, qname, rep,
                        -1, -1, status or "failed"
                    ])
                    print(f"Failed: {status}")
    
    print(f"\nResults saved to: {out_path}")


if __name__ == "__main__":
    main()
