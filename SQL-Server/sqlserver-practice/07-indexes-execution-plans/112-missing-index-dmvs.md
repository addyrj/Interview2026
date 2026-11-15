---

# Q112. Missing Index DMVs
# Category: Indexes + Execution Plans
# Difficulty: ⭐⭐⭐ Hard
# DB: SQL Server (PostgreSQL: pg_stat_statements + hypopg; MySQL: sys schema unused/redundant indexes)

---

## ❓ Question
SQL Server records indexes the optimizer wished it had. Write a query over the missing-index DMVs that ranks suggestions by estimated benefit, explain why you must NOT blindly create every suggestion, and show how to find unused indexes with `sys.dm_db_index_usage_stats` before adding new ones.

---

## 💡 Quick Concept (2 lines only)
Whenever the optimizer compiles a plan and sees a cheaper one with a missing index, it logs it in `sys.dm_db_missing_index_*` (and as green text in the actual plan). The data lives in memory, resets on restart, and ignores everything about your existing indexes and write cost.
हिंदी: Optimizer जब सोचता है "यहाँ index होता तो अच्छा होता" तो DMV में लिख देता है। यह सिर्फ सुझाव है, आँख बंद करके मत बनाओ।

---

## ✅ Answer / Solution

```sql
-- Not executed on SQL Server (no instance available); the DMV content depends entirely on your workload,
-- so no sample output is shown. Column names are from Microsoft docs. Needs VIEW SERVER STATE
-- (VIEW DATABASE STATE on Azure SQL Database).
-- ============================================
-- 1) Ranked missing-index suggestions
-- ============================================
SELECT TOP (20)
       DB_NAME(mid.database_id)                                  AS DatabaseName,
       OBJECT_NAME(mid.object_id, mid.database_id)               AS TableName,
       migs.user_seeks,
       migs.avg_total_user_cost,
       migs.avg_user_impact,                                     -- % improvement the optimizer estimates
       migs.avg_total_user_cost * migs.avg_user_impact * (migs.user_seeks + migs.user_scans) AS Score,
       mid.equality_columns,
       mid.inequality_columns,
       mid.included_columns
FROM sys.dm_db_missing_index_group_stats migs
JOIN sys.dm_db_missing_index_groups     mig ON mig.index_group_handle = migs.group_handle
JOIN sys.dm_db_missing_index_details    mid ON mid.index_handle       = mig.index_handle
WHERE mid.database_id = DB_ID()
ORDER BY Score DESC;

-- How to read a row (illustrative, NOT real output):
--   equality_columns = [CustomerId]   inequality_columns = [OrderDate]   included_columns = [Amount]
--   -> candidate:  CREATE INDEX IX_Orders_Cust_Date ON dbo.Orders (CustomerId, OrderDate) INCLUDE (Amount);
--   (equality columns first, then inequality; the DMV lists columns in table order, NOT recommended key order)

-- ============================================
-- 2) Before creating: is an existing index almost the same? is anything unused?
-- ============================================
SELECT OBJECT_NAME(i.object_id) AS TableName, i.name AS IndexName,
       ISNULL(s.user_seeks,0) AS user_seeks, ISNULL(s.user_scans,0) AS user_scans,
       ISNULL(s.user_lookups,0) AS user_lookups, ISNULL(s.user_updates,0) AS user_updates
FROM sys.indexes i
LEFT JOIN sys.dm_db_index_usage_stats s
       ON s.object_id = i.object_id AND s.index_id = i.index_id AND s.database_id = DB_ID()
WHERE OBJECTPROPERTY(i.object_id, 'IsUserTable') = 1 AND i.type_desc = 'NONCLUSTERED'
ORDER BY ISNULL(s.user_seeks,0) + ISNULL(s.user_scans,0) + ISNULL(s.user_lookups,0), s.user_updates DESC;
-- Indexes with zero reads but many updates are drop candidates (after a full business cycle of data, not 1 hour after restart).
```

---

## 🔍 Why This Works (3 lines max)
The three DMVs are joined by handles: details (which columns), groups (which suggestions belong together) and group_stats (how often and how costly). Multiplying cost, impact and use count gives a rough priority score. The second query balances read benefit against the write cost of maintaining indexes that nobody reads.
हिंदी: तीन DMVs handles से जुड़ती हैं। Score से priority मिलती है, और unused index query से ज़रूरत से ज़्यादा indexes पकड़ में आते हैं।

---

## ⚡ Alternative Solution

```sql
-- Query Store + the actual plan's "Missing Index" hint show the same idea per query, persisted across restarts.
-- Azure SQL Database also offers automatic tuning (CREATE INDEX / DROP INDEX recommendations, optionally auto-applied with validation).
-- Database Engine Tuning Advisor is another source - treat it as a suggestion as well.
```

---

## ⚠️ Common Mistake

```sql
-- ❌ Wrong: creating every suggested index -> dozens of near-duplicate wide indexes, slower writes, bigger backups
-- ❌ Wrong: copying columns in DMV order as the key order -> verify equality first, then range/sort (Q104)
-- ❌ Wrong: trusting the DMV after a restart or a plan-cache clear - it is memory-only and incomplete
-- ❌ Wrong: ignoring limits - suggestions do not cover filtered/columnstore indexes, and the DMV holds a limited number of entries
```

---

## 🎯 Interview Tip (5+ YOE level)
Say: "Missing-index DMVs are a lead generator, not a design. I merge suggestions into existing indexes, check key order and INCLUDE size, compare against usage stats for redundancy, test the change with STATISTICS IO, and watch write overhead after deployment. In Azure SQL I also consider automatic tuning recommendations."

---

## 🔗 Related Questions
→ Q103 (Covering index) | Q104 (Composite index column order) | Q113 (Query Store basics) | Q142 (Finding slow queries)
