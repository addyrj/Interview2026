---

# Q108. SET STATISTICS IO and TIME
# Category: Indexes + Execution Plans
# Difficulty: ⭐⭐ Medium
# DB: SQL Server (PostgreSQL: EXPLAIN (ANALYZE, BUFFERS); MySQL: EXPLAIN ANALYZE)

---

## ❓ Question
You added an index and the query "feels faster". How do you prove it with numbers? Use `SET STATISTICS IO ON` and `SET STATISTICS TIME ON`, explain logical vs physical reads, scan count, CPU time vs elapsed time, and why logical reads are the stable metric for comparing two versions of a query.

---

## 💡 Quick Concept (2 lines only)
`STATISTICS IO` reports pages touched per table (logical reads = 8 KB pages read from buffer cache, physical = from disk); `STATISTICS TIME` reports parse/compile and execution CPU and elapsed ms. Logical reads are deterministic for the same plan and data, while time varies with cache and load.
हिंदी: Logical reads = कितने 8KB pages पढ़े गए, यह stable number है। Time cache और load से बदलता रहता है, इसलिए दोनों देखो।

---

## ✅ Answer / Solution

```sql
-- Not executed on SQL Server (no instance available). Message FORMAT below is from Microsoft docs;
-- every number is a placeholder (N) because real values depend on your data, cache and version.
-- ============================================
-- SETUP
-- ============================================
CREATE TABLE dbo.Orders (
  OrderId INT PRIMARY KEY CLUSTERED, CustomerId INT NOT NULL, OrderDate DATE NOT NULL,
  Status VARCHAR(20) NOT NULL, Amount DECIMAL(10,2) NOT NULL
);
GO

-- ============================================
-- MEASURE
-- ============================================
SET STATISTICS IO ON;
SET STATISTICS TIME ON;

SELECT SUM(Amount) FROM dbo.Orders WHERE CustomerId = 101;     -- no index on CustomerId yet -> scan

-- Messages tab (format only; N = your numbers):
-- Table 'Orders'. Scan count 1, logical reads N, physical reads 0, page server reads 0,
--   read-ahead reads 0, ... lob logical reads 0, ...
--  SQL Server Execution Times:
--    CPU time = N ms,  elapsed time = N ms.

CREATE NONCLUSTERED INDEX IX_Orders_Customer ON dbo.Orders (CustomerId) INCLUDE (Amount);

SELECT SUM(Amount) FROM dbo.Orders WHERE CustomerId = 101;     -- same query, new plan
-- Expect: logical reads drop to a handful of pages for a selective CustomerId (verify on your data).

SET STATISTICS IO OFF;
SET STATISTICS TIME OFF;

-- ============================================
-- FAIR A/B TEST on a dev server only (never on production):
-- ============================================
CHECKPOINT;
DBCC DROPCLEANBUFFERS;   -- cold cache -> physical reads show up
-- Run the query twice: first run = cold (physical reads), second = warm. Compare logical reads, which stay the same.

-- Reading the numbers:
--   scan count     = how many times an index/heap was scanned or seeked (a nested-loop inner side can show large counts)
--   logical reads  = pages from buffer pool  -> primary tuning metric
--   physical reads = pages from disk
--   CPU time       = work done (sum across threads when parallel; can exceed elapsed)
--   elapsed time   = wall clock
```

---

## 🔍 Why This Works (3 lines max)
The same plan on the same data touches the same number of pages, so logical reads let you compare "before vs after" without noise from caching or other sessions. CPU vs elapsed shows whether you waited (blocking, I/O) or computed. Together they tell you if an index actually reduced work, not just luck.
हिंदी: Same plan = same logical reads, इसलिए before/after की fair तुलना होती है। CPU और elapsed का फर्क बताता है कि query wait कर रही थी या काम।

---

## ⚡ Alternative Solution

```sql
-- Extended Events / Query Store give the same numbers for real traffic without editing the query:
SELECT TOP (5) qs.total_logical_reads / qs.execution_count AS avg_logical_reads,
       qs.total_worker_time / qs.execution_count AS avg_cpu_microseconds,
       st.text
FROM sys.dm_exec_query_stats qs
CROSS APPLY sys.dm_exec_sql_text(qs.sql_handle) st
ORDER BY avg_logical_reads DESC;
-- Not executed here; needs VIEW SERVER STATE (VIEW DATABASE STATE on Azure SQL). Counters reset when plans leave cache.
```

---

## ⚠️ Common Mistake

```sql
-- ❌ Wrong: comparing elapsed time of the first (cold) run to the second (warm) run and calling it an improvement
-- ❌ Wrong: running DBCC DROPCLEANBUFFERS / FREEPROCCACHE on a production server - it hurts everyone
-- ❌ Wrong: ignoring "Table 'Worktable'" or high "lob logical reads" lines - they reveal spills and MAX-type columns
-- ❌ Wrong: measuring through SSMS with "Include Actual Plan" on and treating the timing as clean - plan capture adds overhead
```

---

## 🎯 Interview Tip (5+ YOE level)
Say: "My tuning loop is: capture baseline with STATISTICS IO/TIME, change one thing, re-measure logical reads and CPU, and confirm the plan shape. I use logical reads as the primary metric because it is repeatable, and I pair it with the actual plan to explain why." In Azure SQL I add Query Store / Query Performance Insight for production-side evidence.

---

## 🔗 Related Questions
→ Q103 (Covering index) | Q107 (Reading an execution plan) | Q113 (Query Store basics) | Q142 (Finding slow queries)
