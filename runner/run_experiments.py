#!/usr/bin/env python3
import argparse
import subprocess
import time
import csv
from pathlib import Path

# SSB query definitions (standard star-schema versions)
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
        SELECT sum(LO_REVENUE) AS sum_revenue, D_YEAR, P_BRAND
        FROM ssb.lineorder, ssb.date, ssb.part, ssb.supplier
        WHERE LO_ORDERDATE = D_DATEKEY
          AND LO_PARTKEY = P_PARTKEY
          AND LO_SUPPKEY = S_SUPPKEY
          AND P_CATEGORY = 'MFGR#12'
          AND S_REGION = 'AMERICA'
        GROUP BY D_YEAR, P_BRAND
        ORDER BY D_YEAR, P_BRAND;
    """,
    "q2.2": """
        SELECT sum(LO_REVENUE) AS sum_revenue, D_YEAR, P_BRAND
        FROM ssb.lineorder, ssb.date, ssb.part, ssb.supplier
        WHERE LO_ORDERDATE = D_DATEKEY
          AND LO_PARTKEY = P_PARTKEY
          AND LO_SUPPKEY = S_SUPPKEY
          AND P_BRAND BETWEEN 'MFGR#2221' AND 'MFGR#2228'
          AND S_REGION = 'ASIA'
        GROUP BY D_YEAR, P_BRAND
        ORDER BY D_YEAR, P_BRAND;
    """,
    "q2.3": """
        SELECT sum(LO_REVENUE) AS sum_revenue, D_YEAR, P_BRAND
        FROM ssb.lineorder, ssb.date, ssb.part, ssb.supplier
        WHERE LO_ORDERDATE = D_DATEKEY
          AND LO_PARTKEY = P_PARTKEY
          AND LO_SUPPKEY = S_SUPPKEY
          AND P_BRAND = 'MFGR#2221'
          AND S_REGION = 'EUROPE'
        GROUP BY D_YEAR, P_BRAND
        ORDER BY D_YEAR, P_BRAND;
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
        SELECT D_YEAR, S_CITY, P_BRAND,
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
        GROUP BY D_YEAR, S_CITY, P_BRAND
        ORDER BY D_YEAR, S_CITY, P_BRAND;
    """,
}


def run_query(bin_path: str, db_path: str, sql: str) -> float:
    """Run a single query via DuckDB CLI and return elapsed seconds."""
    cmd = [bin_path, db_path, "-c", sql]
    start = time.perf_counter()
    result = subprocess.run(
        cmd,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    end = time.perf_counter()
    if result.returncode != 0:
        raise RuntimeError(f"Command failed: {' '.join(cmd)}")
    return end - start


def main():
    parser = argparse.ArgumentParser(
        description="Run SSB queries against DuckDB CLI and record timings."
    )
    parser.add_argument("--mode", required=True,
                        help="Label for this run, e.g. baseline or rpt")
    parser.add_argument("--duckdb-bin", required=True,
                        help="Path to duckdb executable")
    parser.add_argument("--db", default="db/ssb.duckdb",
                        help="Path to DuckDB database file")
    parser.add_argument("--reps", type=int, default=5,
                        help="Number of repetitions per query")
    parser.add_argument("--out", default="results.csv",
                        help="Output CSV file")
    args = parser.parse_args()

    db_path = str(Path(args.db))
    bin_path = str(Path(args.duckdb-bin))

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    with out_path.open("a", newline="") as f:
        writer = csv.writer(f)
        # header only if file is empty
        if out_path.stat().st_size == 0:
            writer.writerow(["mode", "query", "rep", "time_seconds"])

        for qname, sql in QUERIES.items():
            # optional warm-up
            _ = run_query(bin_path, db_path, sql)
            for rep in range(1, args.reps + 1):
                t = run_query(bin_path, db_path, sql)
                writer.writerow([args.mode, qname, rep, f"{t:.6f}"])
                print(f"{args.mode} {qname} rep {rep}: {t:.3f}s")


if __name__ == "__main__":
    main()
