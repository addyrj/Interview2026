---

# Q109. Statistics and Cardinality Estimation
# Category: Indexes + Execution Plans
# Difficulty: ⭐⭐⭐ Hard
# DB: SQL Server (PostgreSQL: ANALYZE + pg_stats; MySQL: ANALYZE TABLE + histograms)

---

## ❓ Question
`Orders.Status` is heavily skewed: 970 `Shipped` and only 30 `Cancelled` rows. Explain what statistics are, how the optimizer estimates rows for `WHERE Status = 'Cancelled'`, how to view and update them, and what auto-update thresholds mean for large tables.

---

## 💡 Quick Concept (2 lines only)
Statistics are a histogram (up to 200 steps) plus density info on column values; the optimizer uses them to estimate how many rows each operator returns, which drives index choice, join type and memory grants. Stale or missing statistics produce bad estimates and slow plans.
हिंदी: Statistics = column values का histogram। Optimizer इसी से अंदाज़ा लगाता है कि कितनी rows आएँगी। Stale stats = ग़लत plan।

---

## ✅ Answer / Solution

```sql
-- Not executed on SQL Server (no instance available). The GROUP BY counts were derived from the
-- same data on SQLite; DBCC output layout is per Microsoft docs and no histogram numbers are invented.
-- ============================================
-- SETUP (1000 rows: 970 Shipped, 30 Cancelled)
-- ============================================
CREATE TABLE dbo.Orders (
  OrderId INT PRIMARY KEY, Status VARCHAR(20) NOT NULL, Amount DECIMAL(10,2) NOT NULL DEFAULT 10
);
-- (loaded e.g. with a numbers/tally CTE: every 100th, 101st, 102nd... id is 'Cancelled', rest 'Shipped')
CREATE NONCLUSTERED INDEX IX_Orders_Status ON dbo.Orders (Status);   -- creates statistics on Status automatically
GO

SELECT Status, COUNT(*) AS Cnt FROM dbo.Orders GROUP BY Status ORDER BY Status;
-- Output:
-- Status    | Cnt
-- Cancelled | 30
-- Shipped   | 970

-- ============================================
-- LOOK AT THE STATISTICS
-- ============================================
DBCC SHOW_STATISTICS ('dbo.Orders', 'IX_Orders_Status');
-- Three result sets: header (Updated date, Rows, Rows Sampled, Steps),
-- density vector (All density per key prefix), histogram (RANGE_HI_KEY, EQ_ROWS, RANGE_ROWS, ...).
-- For a skewed value like 'Cancelled' the histogram step should hold an EQ_ROWS close to 30 -> optimizer estimates ~30 rows
-- => Index Seek + lookups; for 'Shipped' (~970 of 1000) it estimates most of the table => Scan.

-- When were stats last updated, and how many rows changed since?
SELECT s.name, sp.last_updated, sp.rows, sp.rows_sampled, sp.modification_counter
FROM sys.stats s
CROSS APPLY sys.dm_db_stats_properties(s.object_id, s.stats_id) sp
WHERE s.object_id = OBJECT_ID('dbo.Orders');

-- ============================================
-- UPDATE
-- ============================================
UPDATE STATISTICS dbo.Orders IX_Orders_Status WITH FULLSCAN;   -- exact histogram; expensive on big tables
UPDATE STATISTICS dbo.Orders;                                   -- default sampling
EXEC sys.sp_updatestats;                                        -- whole database (only stale ones)

-- Database options (defaults ON): AUTO_CREATE_STATISTICS, AUTO_UPDATE_STATISTICS (+ _ASYNC optional)
-- Auto-update triggers after a threshold of modifications; on older compat levels it is ~20% of rows (+500),
-- on SQL Server 2016+ with compat level 130+ it uses a smaller, dynamic threshold for big tables (per docs).
```

---

## 🔍 Why This Works (3 lines max)
The histogram records how many rows have each value, so the optimizer knows `'Cancelled'` is rare (seek) and `'Shipped'` is common (scan). Without current stats it falls back to density/guess estimates, so one wrong estimate propagates up the plan into wrong joins and undersized memory grants. Keeping stats fresh keeps the estimates, and thus the plan, honest.
हिंदी: Histogram बताता है कौन सी value कितनी बार है। Stats पुरानी हों तो अंदाज़ा ग़लत और plan भी ग़लत हो जाता है।

---

## ⚡ Alternative Solution

```sql
-- Multi-column and filtered statistics for correlated columns / hot ranges:
CREATE STATISTICS ST_Orders_Status_Amount ON dbo.Orders (Status, Amount);
CREATE STATISTICS ST_Orders_Cancelled ON dbo.Orders (Amount) WHERE Status = 'Cancelled';

-- Parameter sniffing view of the same skew: plan built for 'Cancelled' (seek) then reused for 'Shipped' (bad).
-- Options: OPTION (RECOMPILE), OPTION (OPTIMIZE FOR UNKNOWN), or Query Store plan forcing (Q114).
```

---

## ⚠️ Common Mistake

```sql
-- ❌ Wrong: nightly index REBUILD and thinking stats are stale anyway - REBUILD updates that index's stats with FULLSCAN,
--           REORGANIZE does NOT update statistics.
-- ❌ Wrong: disabling AUTO_UPDATE_STATISTICS to "save CPU" -> bad plans, much costlier
-- ❌ Wrong: always FULLSCAN on multi-billion-row tables during business hours
-- ❌ Wrong: local variables in WHERE hide the value from the histogram -> density-based guess instead of histogram
DECLARE @s VARCHAR(20) = 'Cancelled';
SELECT * FROM dbo.Orders WHERE Status = @s;   -- estimate uses average density, not the 'Cancelled' step
```

---

## 🎯 Interview Tip (5+ YOE level)
Say: "Bad plans are usually bad estimates. I compare estimated vs actual rows in the plan, check `sys.dm_db_stats_properties` for modification_counter and last_updated, then update stats (FULLSCAN if the histogram is skewed) or address sniffing. For huge tables I schedule stats maintenance rather than depending on the auto threshold, and I know the newer cardinality estimator (compat level 120+) can change plans after upgrades."

---

## 🔗 Related Questions
→ Q107 (Reading an execution plan) | Q111 (Index fragmentation) | Q114 (Parameter sniffing and fixes) | Q151 (Parameter sniffing deep-dive)
