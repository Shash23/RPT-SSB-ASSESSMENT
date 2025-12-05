# Presentation Script: 5-Minute Talk

## Opening (30 seconds)

"Good [morning/afternoon]. Today I'll present our evaluation of Robust Predicate Transfer in DuckDB using the Star Schema Benchmark.

Join operations are one of the most expensive operations in analytical query processing. They can create large intermediate results that exceed memory and CPU resources. Robust Predicate Transfer, or RPT, addresses this by using Bloom filters to propagate predicates across join graphs before joins execute, reducing the data that needs to be processed.

While RPT has been evaluated on synthetic benchmarks like TPC-H, JOB, and TPC-DS, these don't capture real-world characteristics like star-schema structures and data skew. Our work evaluates RPT on the Star Schema Benchmark to test its robustness under more realistic workloads."

---

## What is RPT? (45 seconds)

"RPT builds on Predicate Transfer, which uses Bloom filters instead of expensive semi-joins to pre-filter data. RPT adds two key algorithms: LargestRoot, which ensures full reduction through a maximum spanning tree, and SafeSubjoin, which validates join order.

RPT executes in two phases. First, a predicate transfer phase performs forward and backward sweeps, propagating compact Bloom filters across the join graph. Then, the join phase operates on this pre-filtered, reduced data. This approach aims to provide robust performance even when join order would otherwise matter."

---

## Star Schema Benchmark (SSB) (60 seconds)

"Before diving into our methodology, let me explain why we chose the Star Schema Benchmark and what makes it representative of real-world workloads.

SSB is a simplified version of TPC-H, specifically designed for star-schema workloads. It has a classic star schema structure with one fact table and four dimension tables.

The fact table is `lineorder`, which contains transaction data - order details, revenue, quantities, discounts, and supply costs. This is the largest table and sits at the center of our star schema.

The four dimension tables are: `customer`, which has customer demographics like region, nation, city, and market segment; `supplier`, with supplier information including region, nation, and city; `part`, containing product details like category, brand, manufacturer, and color; and `date`, which provides time dimensions including year, month, week, and selling season.

[Show star schema diagram if available]

Now, why is SSB important for evaluating RPT? First, star schemas are ubiquitous in real-world data warehouses. Most businesses model their analytics this way - a central fact table with dimensions radiating out. This matches how companies actually structure their sales, inventory, and business intelligence systems.

Second, SSB is simplified but realistic. It removes some of TPC-H's complexity while keeping the essential patterns we need to test - multi-way joins between the fact table and dimensions, and selective predicates on dimension attributes that need to propagate to the fact table.

Third, SSB tests RPT's ability to handle star-shaped join graphs, which is exactly what RPT is designed for. The queries join the lineorder fact table with multiple dimensions simultaneously, and filters on dimension attributes like region, year, or category need to propagate to reduce the fact table before joins execute.

Finally, this addresses a gap in the RPT evaluation. The original RPT paper used TPC-H, which has a snowflake schema - more complex but less common in practice. By testing on SSB's star schema, we validate RPT on a simpler but more representative workload pattern that's actually used in production data warehouses."

---

## Methodology - Implementation Details (90 seconds)

"Let me walk you through our detailed experimental methodology.

**First, the RPT source code setup.** We forked the RPT-enabled DuckDB repository from EmbryoLabs, which maintains an implementation of Robust Predicate Transfer. This is based on DuckDB version 1.4.0 with the RPT optimization integrated. The RPT code is located in the optimizer directory, specifically in `src/optimizer/predicate_transfer/`. 

RPT is controlled through a configuration file called `setting.hpp`. To enable RPT, we uncomment `#define PredicateTransfer` and `#define RandomLeftDeep`. For the baseline, we comment out PredicateTransfer but keep RandomLeftDeep join order. Importantly, we rebuild DuckDB each time we switch configurations, since RPT is a compile-time feature.

**For dataset preparation**, we used the Star Schema Benchmark at scale factor 1. We generated the data using the `ssb-dbgen` tool, which created five tables: the lineorder fact table with approximately 6 million rows, and four dimension tables for customer, supplier, part, and date. We loaded this data into a single DuckDB database file using SQL COPY commands.

**Our experimental setup** ran on CloudLab x86_64 Linux nodes. We compared two configurations: baseline with RPT disabled using the default optimizer, and RPT enabled with predicate transfer. 

**Why RandomLeftDeep join order?** This was a deliberate choice for several reasons. First, RPT's core claim is robustness to join order - it should perform well regardless of how joins are ordered. RandomLeftDeep provides a consistent, reproducible join order strategy that tests this robustness claim. Left-deep plans are also common in practice - they're simpler than bushy plans and represent a realistic scenario.

The random element is important because it tests whether RPT can handle potentially suboptimal join orders gracefully. We considered alternatives: ExactLeftDeep would give deterministic, cost-based plans, but might favor specific optimizations. RandomBushy would be more complex but harder to interpret. Using the default optimizer would mean different join orders for baseline versus RPT, making our comparison unfair.

By using the same RandomLeftDeep join order for both configurations, we isolate RPT's effect - any performance difference comes from predicate transfer, not from different join orderings. This ensures a fair comparison while still testing RPT's robustness to join order variations.

**We tested 13 SSB queries** - the standard SSB query suite ranging from simple 2-table joins in Q1.x to complex 5-table joins in Q4.x. Each query was executed via DuckDB's command-line interface.

**For measurements**, we collected three metrics. First, query runtime - we executed each query 5 times per configuration, measuring wall-clock time using Python's high-resolution timer, and saved results to CSV files. Second, intermediate join sizes - we created SQL queries with common table expressions to count rows at each join step, measuring filtered dimension sizes and intermediate join results. Third, memory utilization - we used the system's time command to measure peak memory usage, executing each query 3 times per configuration.

**To automate this process**, we created several Python and Bash scripts. The main experiment runner automatically configures the setting file, rebuilds DuckDB, runs all queries, and collects measurements. We also created scripts to measure join sizes and memory, plus analysis and visualization tools.

**As experimental controls**, we ensured both configurations used the identical database file, the same RandomLeftDeep join order, ran on the same CloudLab node, and included multiple repetitions with warm-up runs excluded. This ensures our comparison is fair and the results are reliable."

---

## Results - Performance (60 seconds)

"Let me show you our performance results. [Show performance_comparison.png]

On average, RPT is about 8.9% slower than the baseline. Looking at the speedup graph [Show speedup_comparison.png], we see that RPT is slower across all 13 SSB queries, with speedups ranging from 0.85x to 0.99x.

The performance degradation is most pronounced on complex queries like q4.1, which is 17.9% slower with RPT. Simple queries like q1.x show around 10% degradation.

This is actually not surprising. For small datasets at scale factor 1, the overhead of creating and probing Bloom filters outweighs the benefits. The RPT paper shows 4x improvements, but on TPC-H, which has different query characteristics. Our results suggest that RPT's benefits scale with data size and may not be visible at SF=1."

---

## Results - Memory & Join Sizes (60 seconds)

"Now let's look at memory utilization. [Show memory_comparison.png]

The average baseline memory usage is 37.47 MB, while RPT uses 37.48 MB - a difference of only 0.01 MB, or 0.03%. This demonstrates that RPT has negligible memory overhead, which is important for its practical deployment.

For intermediate join sizes [Show join_size_comparison.png], we found that the row counts at each join step are identical between baseline and RPT. This suggests that for this dataset size, RPT doesn't change the cardinality of intermediate results.

The summary graph [Show summary_comparison.png] gives a quick overview of both metrics, showing that while performance is slightly worse, memory overhead is minimal."

---

## Analysis & Insights (60 seconds)

"Let me share some key insights from our analysis.

First, dataset size matters. At scale factor 1, the data is too small to see RPT's benefits. The overhead of Bloom filter operations is visible, but the filtering benefits don't materialize because the data is already small.

Second, there's a clear overhead versus benefit trade-off. Bloom filter creation and probing have costs that are visible on small data, but these would likely be amortized at larger scale factors like SF=10 or SF=100.

Third, query characteristics matter. The star-schema structure of SSB may not stress RPT's strengths. RPT is designed for complex multi-way joins with selective predicates, and SSB queries may have different patterns than TPC-H.

Finally, both configurations show consistent performance with low variance, demonstrating robustness in terms of stability, even if RPT doesn't provide speedups at this scale."

---

## Conclusions & Future Work (45 seconds)

"In conclusion, our evaluation shows that RPT has minimal impact on SSB at scale factor 1. The memory overhead is negligible at less than 0.1%, and the performance overhead of about 9% is likely due to the small dataset size. These results validate RPT's low overhead, but suggest that benefits need larger scale to emerge.

For future work, we would scale up to SF=10 and SF=100 to see if benefits emerge. We'd also investigate why SSB queries don't benefit compared to TPC-H, test with different join orders like RandomBushy, and experiment with more selective predicates to stress RPT's strengths.

Thank you. I'm happy to take questions."

---

## Quick Reference: Key Numbers

- **Performance:** 8.9% slower on average
- **Memory:** +0.03% overhead (negligible)
- **Join Sizes:** Identical between baseline and RPT
- **Queries:** 13 SSB queries tested
- **Scale Factor:** 1 (small dataset)
- **Repetitions:** 5 per query for performance, 3 for memory

## Handling Questions

**Q: Why is RPT slower when the paper shows improvements?**
A: The paper evaluated on TPC-H at SF=1 and SF=10, showing 4x improvements. We used SSB, which has different query characteristics. Also, at SF=1, the overhead of Bloom filters is visible, but benefits would likely emerge at larger scales.

**Q: Would results change at larger scale?**
A: Yes, we expect RPT benefits to emerge at SF=10 or SF=100, where the filtering benefits would outweigh the Bloom filter overhead.

**Q: Is this a negative result?**
A: Not necessarily. We validated that RPT has low overhead and consistent performance. The lack of speedup at small scale is expected and aligns with how Bloom filter optimizations work - they benefit more as data grows.

