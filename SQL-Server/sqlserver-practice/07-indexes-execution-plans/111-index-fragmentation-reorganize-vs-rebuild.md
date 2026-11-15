---

# Q111. Index Fragmentation - REORGANIZE vs REBUILD
# Category: Indexes + Execution Plans
# Difficulty: ⭐⭐ Medium
# DB: SQL Server (PostgreSQL: REINDEX / VACUUM; MySQL: OPTIMIZE TABLE)

---

## ❓ Question
Find fragmented indexes in a database, decide between `REORGANIZE` and `REBUILD` using the usual guideline (about 5-30% vs more than 30%), explain ONLINE rebuilds, `FILLFACTOR`, and whether fragmentation still matters on SSDs and in Azure SQL.

---

## 💡 Quick Concept (2 lines only)
Fragmentation = logical page order differs from physical order (page splits) and pages are half-empty, hurting range scans and read-ahead. REORGANIZE compacts leaf pages in place (online, interruptible, no stats update); REBUILD recreates the index (new pages, stats updated with FULLSCAN, more resources).
हिंदी: Fragmentation = pages का order बिखरा और pages आधे खाली। REORGANIZE हल्का और online, REBUILD पूरा नया index बनाता है।

---

## ✅ Answer / Solution

```sql
-- Not executed on SQL Server (no instance available); no DMV numbers are shown because they
-- depend on your data. Syntax and thresholds per Microsoft docs.
-- ============================================
-- 1) FIND FRAGMENTATION
-- ============================================
SELECT OBJECT_SCHEMA_NAME(ips.object_id) AS SchemaName,
       OBJECT_NAME(ips.object_id)        AS TableName,
       i.name                            AS IndexName,
       ips.avg_fragmentation_in_percent,
       ips.page_count
FROM sys.dm_db_index_physical_stats(DB_ID(), NULL, NULL, NULL, 'LIMITED') ips
JOIN sys.indexes i ON i.object_id = ips.object_id AND i.index_id = ips.index_id
WHERE ips.index_id > 0              -- skip heaps
  AND ips.page_count >= 1000        -- ignore tiny indexes (fragmentation is meaningless there)
ORDER BY ips.avg_fragmentation_in_percent DESC;

-- ============================================
-- 2) FIX
-- ============================================
-- Rule of thumb from docs: ~5% to 30% -> REORGANIZE ; > 30% -> REBUILD
ALTER INDEX IX_Orders_Customer ON dbo.Orders REORGANIZE;
UPDATE STATISTICS dbo.Orders IX_Orders_Customer;      -- REORGANIZE does not update stats

ALTER INDEX IX_Orders_Customer ON dbo.Orders
  REBUILD WITH (ONLINE = ON, FILLFACTOR = 90, SORT_IN_TEMPDB = ON);
-- ONLINE = ON needs Enterprise edition (and Azure SQL); otherwise the index is locked during rebuild.
-- RESUMABLE = ON is available for online rebuilds on newer versions (2017+; verify for your target).

ALTER INDEX ALL ON dbo.Orders REBUILD;                -- every index on the table

-- ============================================
-- 3) FILLFACTOR: leave free space on leaf pages for future inserts into the middle of the index.
--    Lower fillfactor = fewer page splits but larger index. Use it only for indexes that really fragment fast
--    (random-key inserts); append-only (IDENTITY) keys do not need it.
-- ============================================
```

---

## 🔍 Why This Works (3 lines max)
The DMV measures how out-of-order the leaf level is; REORGANIZE swaps and compacts pages using minimal locks, so it suits light fragmentation, while REBUILD allocates fresh contiguous pages and refreshes statistics, so it suits heavy fragmentation. Filtering by page_count avoids pointless work on small indexes.
हिंदी: कम fragmentation पर REORGANIZE (हल्का), ज़्यादा पर REBUILD। छोटे indexes (1000 pages से कम) को छोड़ दो।

---

## ⚡ Alternative Solution

```sql
-- Don't write your own maintenance job if you can avoid it: Ola Hallengren's IndexOptimize is the common community standard.
-- Azure SQL Database: no SQL Agent; use Elastic Jobs, Azure Automation runbooks or a Logic App on a schedule.
-- Often better ROI: update statistics regularly (Q109) and fix the clustering key (Q102) so fragmentation does not occur.
```

---

## ⚠️ Common Mistake

```sql
-- ❌ Wrong: nightly REBUILD of every index "just in case" -> big log growth, blocking (without ONLINE), wasted I/O
-- ❌ Wrong: rebuilding a 50-page index because it shows 60% fragmentation - small indexes live in mixed extents and cannot be defragmented meaningfully
-- ❌ Wrong: running REORGANIZE and assuming statistics refreshed; it does not update them
-- ❌ Wrong: ignoring that on SSD/flash storage and with large read-ahead, logical fragmentation often matters far less than page density
--           and good statistics - measure the benefit before scheduling jobs
```

---

## 🎯 Interview Tip (5+ YOE level)
Say: "I treat the 5%/30% numbers as guidelines, not law. I only maintain indexes over about 1000 pages, prefer REORGANIZE plus UPDATE STATISTICS for light cases and ONLINE REBUILD for heavy ones, watch log and tempdb impact, and run it in a maintenance window or via a proven script. In Azure SQL I schedule it with Elastic Jobs and also fix the root cause - random GUID clustering keys, low fillfactor choices."

---

## 🔗 Related Questions
→ Q024 (GUID vs INT keys) | Q102 (Clustered vs non-clustered) | Q109 (Statistics) | Q156 (Monitoring and baselines)
