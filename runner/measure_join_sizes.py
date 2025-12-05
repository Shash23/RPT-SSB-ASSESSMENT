#!/usr/bin/env python3
"""
Measure intermediate join sizes for SSB queries.
Uses SQL queries with CTEs to count rows at each join step.
"""

import argparse
import subprocess
import csv
from pathlib import Path

# SSB query definitions with intermediate join measurements
QUERIES = {
    "q1.1": {
        "query": """
            SELECT sum(LO_EXTENDEDPRICE * LO_DISCOUNT) AS revenue
            FROM ssb.lineorder, ssb.date
            WHERE LO_ORDERDATE = D_DATEKEY
              AND D_YEAR = 1993
              AND LO_DISCOUNT BETWEEN 1 AND 3
              AND LO_QUANTITY < 25;
        """,
        "joins": [
            ("date_filtered", "SELECT COUNT(*) FROM ssb.date WHERE d_year = 1993"),
            ("lineorder_filtered", "SELECT COUNT(*) FROM ssb.lineorder WHERE lo_discount BETWEEN 1 AND 3 AND lo_quantity < 25"),
            ("join1", """
                SELECT COUNT(*) FROM ssb.lineorder lo, ssb.date d
                WHERE lo.lo_orderdate = d.d_datekey
                  AND d.d_year = 1993
                  AND lo.lo_discount BETWEEN 1 AND 3
                  AND lo.lo_quantity < 25
            """)
        ]
    },
    "q2.1": {
        "query": """
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
        "joins": [
            ("date_all", "SELECT COUNT(*) FROM ssb.date"),
            ("part_filtered", "SELECT COUNT(*) FROM ssb.part WHERE p_category = 'MFGR#12'"),
            ("supplier_filtered", "SELECT COUNT(*) FROM ssb.supplier WHERE s_region = 'AMERICA'"),
            ("lineorder_all", "SELECT COUNT(*) FROM ssb.lineorder"),
            ("join_date", """
                SELECT COUNT(*) FROM ssb.lineorder lo, ssb.date d
                WHERE lo.lo_orderdate = d.d_datekey
            """),
            ("join_date_part", """
                SELECT COUNT(*) FROM ssb.lineorder lo, ssb.date d, ssb.part p
                WHERE lo.lo_orderdate = d.d_datekey
                  AND lo.lo_partkey = p.p_partkey
                  AND p.p_category = 'MFGR#12'
            """),
            ("join_final", """
                SELECT COUNT(*) FROM ssb.lineorder lo, ssb.date d, ssb.part p, ssb.supplier s
                WHERE lo.lo_orderdate = d.d_datekey
                  AND lo.lo_partkey = p.p_partkey
                  AND lo.lo_suppkey = s.s_suppkey
                  AND p.p_category = 'MFGR#12'
                  AND s.s_region = 'AMERICA'
            """)
        ]
    },
    "q3.1": {
        "query": """
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
        "joins": [
            ("customer_filtered", "SELECT COUNT(*) FROM ssb.customer WHERE c_region = 'ASIA'"),
            ("supplier_filtered", "SELECT COUNT(*) FROM ssb.supplier WHERE s_region = 'ASIA'"),
            ("date_filtered", "SELECT COUNT(*) FROM ssb.date WHERE d_year BETWEEN 1992 AND 1997"),
            ("lineorder_all", "SELECT COUNT(*) FROM ssb.lineorder"),
            ("join_customer", """
                SELECT COUNT(*) FROM ssb.lineorder lo, ssb.customer c
                WHERE lo.lo_custkey = c.c_custkey AND c.c_region = 'ASIA'
            """),
            ("join_supplier", """
                SELECT COUNT(*) FROM ssb.lineorder lo, ssb.customer c, ssb.supplier s
                WHERE lo.lo_custkey = c.c_custkey AND lo.lo_suppkey = s.s_suppkey
                  AND c.c_region = 'ASIA' AND s.s_region = 'ASIA'
            """),
            ("join_final", """
                SELECT COUNT(*) FROM ssb.lineorder lo, ssb.customer c, ssb.supplier s, ssb.date d
                WHERE lo.lo_custkey = c.c_custkey 
                  AND lo.lo_suppkey = s.s_suppkey
                  AND lo.lo_orderdate = d.d_datekey
                  AND c.c_region = 'ASIA' AND s.s_region = 'ASIA'
                  AND d.d_year BETWEEN 1992 AND 1997
            """)
        ]
    },
    "q4.1": {
        "query": """
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
        "joins": [
            ("customer_filtered", "SELECT COUNT(*) FROM ssb.customer WHERE c_region = 'AMERICA'"),
            ("supplier_filtered", "SELECT COUNT(*) FROM ssb.supplier WHERE s_region = 'AMERICA'"),
            ("part_filtered", "SELECT COUNT(*) FROM ssb.part WHERE p_mfgr IN ('MFGR#1', 'MFGR#2')"),
            ("date_all", "SELECT COUNT(*) FROM ssb.date"),
            ("lineorder_all", "SELECT COUNT(*) FROM ssb.lineorder"),
            ("join_customer", """
                SELECT COUNT(*) FROM ssb.lineorder lo, ssb.customer c
                WHERE lo.lo_custkey = c.c_custkey AND c.c_region = 'AMERICA'
            """),
            ("join_supplier", """
                SELECT COUNT(*) FROM ssb.lineorder lo, ssb.customer c, ssb.supplier s
                WHERE lo.lo_custkey = c.c_custkey AND lo.lo_suppkey = s.s_suppkey
                  AND c.c_region = 'AMERICA' AND s.s_region = 'AMERICA'
            """),
            ("join_part", """
                SELECT COUNT(*) FROM ssb.lineorder lo, ssb.customer c, ssb.supplier s, ssb.part p
                WHERE lo.lo_custkey = c.c_custkey 
                  AND lo.lo_suppkey = s.s_suppkey
                  AND lo.lo_partkey = p.p_partkey
                  AND c.c_region = 'AMERICA' AND s.s_region = 'AMERICA'
                  AND p.p_mfgr IN ('MFGR#1', 'MFGR#2')
            """),
            ("join_final", """
                SELECT COUNT(*) FROM ssb.lineorder lo, ssb.customer c, ssb.supplier s, ssb.part p, ssb.date d
                WHERE lo.lo_custkey = c.c_custkey 
                  AND lo.lo_suppkey = s.s_suppkey
                  AND lo.lo_partkey = p.p_partkey
                  AND lo.lo_orderdate = d.d_datekey
                  AND c.c_region = 'AMERICA' AND s.s_region = 'AMERICA'
                  AND p.p_mfgr IN ('MFGR#1', 'MFGR#2')
            """)
        ]
    }
}


def run_count_query(bin_path, db_path, sql):
    """Run a COUNT query and return the result."""
    cmd = [bin_path, db_path, "-c", sql]
    
    try:
        result = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=60
        )
        
        if result.returncode != 0:
            print(f"  Error: {result.stderr[:200]}")
            return None
        
        # Extract number from output
        output = result.stdout.strip()
        # Look for the number in the output
        import re
        match = re.search(r'(\d+)', output)
        if match:
            return int(match.group(1))
        return None
    except Exception as e:
        print(f"  Exception: {e}")
        return None


def main():
    parser = argparse.ArgumentParser(
        description="Measure intermediate join sizes for SSB queries."
    )
    parser.add_argument("--mode", required=True,
                        help="Label for this run, e.g. baseline or rpt")
    parser.add_argument("--duckdb-bin", required=True,
                        help="Path to duckdb executable")
    parser.add_argument("--db", default="db/ssb.duckdb",
                        help="Path to DuckDB database file")
    parser.add_argument("--out", default="join_sizes.csv",
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
        writer.writerow(["mode", "query", "step", "step_name", "row_count"])

        for qname in queries_to_run:
            if qname not in QUERIES:
                print(f"Warning: Query {qname} not found, skipping")
                continue
                
            query_info = QUERIES[qname]
            print(f"\nAnalyzing {args.mode} {qname}...")
            
            for step_num, (step_name, count_sql) in enumerate(query_info["joins"], 1):
                row_count = run_count_query(bin_path, db_path, count_sql)
                if row_count is not None:
                    writer.writerow([args.mode, qname, step_num, step_name, row_count])
                    print(f"  {step_name}: {row_count:,} rows")
                else:
                    writer.writerow([args.mode, qname, step_num, step_name, -1])
                    print(f"  {step_name}: Failed to get count")
    
    print(f"\nResults saved to: {out_path}")


if __name__ == "__main__":
    main()
