# Future Work Script - Presentation Talking Points

## Future Work Section (45 seconds)

### Opening Transition

"While our results show minimal impact at scale factor 1, there are several important directions for future work that would provide deeper insights into RPT's effectiveness."

---

### Point 1: Scale Up (15 seconds)

"First, we need to scale up. Our experiments used scale factor 1, which is quite small. The RPT paper showed 4x improvements at SF=1 on TPC-H, but that's a different workload. We should test at SF=10 and SF=100 to see if RPT's benefits emerge as data size increases. The overhead of Bloom filter creation and probing should become negligible compared to the filtering benefits when we have larger fact tables and more selective predicates."

**Visual:** Show a graph or table comparing SF=1 (current) vs projected SF=10, SF=100

**Key Message:** "Scale matters - benefits likely emerge with larger datasets"

---

### Point 2: Query Analysis (10 seconds)

"Second, we should investigate why SSB queries don't show the same benefits as TPC-H. The RPT paper evaluated on TPC-H, which has different query characteristics - more complex join patterns and different selectivity profiles. We need to analyze the SSB query patterns, join graph structures, and predicate selectivity to understand why RPT doesn't provide speedups here. This would help identify which workload characteristics make RPT most effective."

**Visual:** Side-by-side comparison of TPC-H vs SSB query characteristics

**Key Message:** "Understanding workload differences helps identify when RPT is most effective"

---

### Point 3: Join Order Robustness (10 seconds)

"Third, we should test join order robustness more thoroughly. Our experiments used RandomLeftDeep join order for both configurations. The RPT paper emphasizes robustness to join order as a key benefit. We should test with RandomBushy and ExactLeftDeep join orders to see if RPT provides more consistent performance across different join orderings, even if absolute performance doesn't improve. This would validate RPT's claim of join-order robustness."

**Visual:** Table showing different join order strategies

**Key Message:** "Test RPT's core claim: robustness to join order"

---

### Point 4: Selective Predicates (10 seconds)

"Finally, we should test with more selective predicates. RPT's strength is in propagating highly selective filters across the join graph. Our SSB queries may not have selective enough predicates to see benefits. We should design experiments with varying predicate selectivity - from low selectivity where overhead dominates, to high selectivity where filtering benefits should emerge. This would help identify the selectivity threshold where RPT becomes beneficial."

**Visual:** Graph showing predicate selectivity vs expected RPT benefit

**Key Message:** "Selective predicates are key to RPT's effectiveness"

---

## Alternative Shorter Version (30 seconds)

If you need to cut time, here's a condensed version:

"Looking forward, there are four key directions for future work. First, scale up to SF=10 and SF=100 - our small dataset likely masks RPT's benefits. Second, analyze why SSB queries don't benefit like TPC-H - understanding workload differences is crucial. Third, test different join orders like RandomBushy and ExactLeftDeep to validate RPT's robustness claim. And fourth, experiment with more selective predicates - RPT's strength is in propagating highly selective filters, and our current queries may not be selective enough. These experiments would provide a complete picture of when and how RPT is most effective."

---

## Full Script with Transitions

**Complete Future Work Section (45 seconds):**

"While our results show minimal impact at scale factor 1, there are several important directions for future work.

First, we need to scale up. Our experiments used scale factor 1, which is quite small. The RPT paper showed 4x improvements at SF=1 on TPC-H, but that's a different workload. We should test at SF=10 and SF=100 to see if RPT's benefits emerge as data size increases. The overhead of Bloom filter creation should become negligible compared to filtering benefits with larger fact tables.

Second, we should investigate why SSB queries don't show the same benefits as TPC-H. The RPT paper evaluated on TPC-H, which has different query characteristics. We need to analyze SSB query patterns and predicate selectivity to understand which workload characteristics make RPT most effective.

Third, we should test join order robustness more thoroughly. Our experiments used RandomLeftDeep for both configurations. We should test with RandomBushy and ExactLeftDeep join orders to validate RPT's claim of robustness to join order, even if absolute performance doesn't improve.

Finally, we should test with more selective predicates. RPT's strength is propagating highly selective filters. Our SSB queries may not be selective enough. Experiments with varying predicate selectivity would help identify the threshold where RPT becomes beneficial.

These experiments would provide a complete picture of when and how RPT is most effective in real-world data warehouse workloads."

---

## Key Talking Points Summary

### For Each Point:

1. **Scale Up:**
   - Current: SF=1 (small)
   - Future: SF=10, SF=100
   - Why: Overhead becomes negligible, benefits emerge
   - Connection: RPT paper shows benefits scale with data size

2. **Query Analysis:**
   - Current: SSB doesn't benefit like TPC-H
   - Future: Analyze query patterns, join graphs, selectivity
   - Why: Understand workload differences
   - Connection: Different benchmarks have different characteristics

3. **Join Order Robustness:**
   - Current: Only tested RandomLeftDeep
   - Future: Test RandomBushy, ExactLeftDeep
   - Why: Validate RPT's core claim
   - Connection: RPT emphasizes robustness as key benefit

4. **Selective Predicates:**
   - Current: SSB queries may not be selective enough
   - Future: Vary predicate selectivity
   - Why: RPT's strength is in selective filters
   - Connection: Bloom filters benefit most from high selectivity

---

## Visual Suggestions

1. **Slide Layout Options:**

   **Option A: Four Quadrants**
   - Divide slide into 4 sections
   - Each section = one future work item
   - Include icon or simple diagram for each

   **Option B: Bullet Points with Icons**
   - Four main bullets
   - Sub-bullets for details
   - Icons: scale (↑), magnifying glass (🔍), network (🕸️), filter (🔽)

   **Option C: Timeline/Roadmap**
   - Show future work as steps
   - Indicate priority or sequence
   - Visual progression

2. **Supporting Visuals:**
   - Graph: Expected RPT benefit vs Scale Factor
   - Table: Comparison of TPC-H vs SSB characteristics
   - Diagram: Different join order strategies
   - Chart: Predicate selectivity spectrum

---

## Delivery Tips

1. **Pace:** Don't rush - this shows depth of understanding
2. **Emphasis:** Stress that results aren't negative, just need more investigation
3. **Connection:** Link each point back to your results
4. **Confidence:** Show you understand the limitations and next steps
5. **Time Management:** If running short on time, use the condensed version

---

## Anticipated Questions & Answers

**Q: Why didn't you test at larger scale factors initially?**
A: "We started with SF=1 to establish a baseline and validate our experimental setup. Scaling up requires more computational resources and time, so we wanted to ensure our methodology was sound first. The next step is definitely to scale up."

**Q: Do you think RPT will show benefits at larger scale?**
A: "Yes, we expect benefits to emerge at SF=10 or SF=100. The Bloom filter overhead is fixed, but the filtering benefits scale with data size. As the fact table grows, pre-filtering becomes more valuable."

**Q: Why is join order robustness important if performance doesn't improve?**
A: "Robustness means consistent performance regardless of join order. Even if RPT doesn't speed things up, if it makes performance more predictable and less sensitive to optimizer choices, that's valuable for production systems."

**Q: How would you test predicate selectivity?**
A: "We'd modify SSB queries to have varying selectivity - from broad filters that match 50% of rows to highly selective filters matching 1% or less. This would show the selectivity threshold where RPT's benefits outweigh overhead."


