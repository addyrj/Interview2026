---

# Q149. tempdb Contention
# Category: Performance Tuning
# Difficulty: ⭐⭐⭐ Hard
# DB: SQL Server (PostgreSQL/MySQL have no shared tempdb equivalent). Not executed on SQL Server; behaviour per Microsoft docs.

---

## ❓ Question
Under load many sessions wait with PAGELATCH_UP/EX on tempdb allocation pages. What causes it, how do you confirm it, and what are the fixes?

---

## 💡 Quick Concept (2 lines only)
tempdb is shared by temp tables, table variables, sorts, hash joins spills, version store and internal work. Many sessions creating/dropping objects contend on allocation bitmap pages (PFS/GAM/SGAM) when there are too few data files.
हिंदी: tempdb सब sessions का साझा है। कम data files + बहुत सारे temp objects = allocation pages पर latch contention।

---

## ✅ Answer / Solution

```sql
-- ============================================
-- 1) Confirm: waiting tasks on tempdb pages (database_id 2)
--    (not executed on SQL Server; behaviour per Microsoft docs)
-- ============================================
SELECT session_id, wait_type, wait_duration_ms, resource_description
FROM sys.dm_os_waiting_tasks
WHERE wait_type LIKE N'PAGELATCH%'
  AND resource_description LIKE N'2:%';
-- resource_description is dbid:fileid:pageid. Page 1 = PFS, 2 = GAM, 3 = SGAM
-- (and +8088 multiples for PFS) are the classic allocation hot spots.

-- 2) Who uses tempdb space
SELECT session_id,
       user_objects_alloc_page_count,
       internal_objects_alloc_page_count
FROM sys.dm_db_session_space_usage
ORDER BY user_objects_alloc_page_count + internal_objects_alloc_page_count DESC;

-- 3) Fixes
-- a) Several equally sized tempdb data files (start: 1 per logical core up to 8, then tune)
ALTER DATABASE tempdb ADD FILE
  (NAME = N'tempdev2', FILENAME = N'T:\tempdb\tempdev2.ndf', SIZE = 8GB, FILEGROWTH = 0);
-- b) Pre-size files equally; avoid autogrow storms (SQL Server 2016+ has uniform growth by default)
-- c) SQL Server 2019+: memory-optimized tempdb metadata
ALTER SERVER CONFIGURATION SET MEMORY_OPTIMIZED TEMPDB_METADATA = ON;   -- needs restart
-- d) Reduce churn: fewer #temp create/drop per call, cached temp tables in procs

-- EXPECTED OUTPUT: shape only (not executed; nothing invented):
--   session_id | wait_type    | wait_duration_ms | resource_description
```

---

## 🔍 Why This Works (3 lines max)
More equally sized files spread allocations (proportional fill), so fewer sessions fight over the same PFS/GAM/SGAM pages. Memory-optimized metadata removes latch contention on system tables used by temp object DDL.
हिंदी: ज़्यादा बराबर साइज़ की files = allocation बँट जाता है। Temp object बनाना-हटाना कम करो।

---

## ⚡ Alternative Solution

```sql
-- Fix the workload: stop spills and big sorts (update stats, add indexes, right-size memory grants)
-- Use RCSI/SNAPSHOT only knowing it adds version-store load to tempdb (Q120, Q121)
-- Azure SQL Database: tempdb is managed; you tune the queries, not the files.
```

---

## ⚠️ Common Mistake

```sql
-- ❌ Adding unequal files: proportional fill sends most allocations to the largest file
-- ❌ Putting tempdb on slow shared disk; it is write-heavy
-- ❌ Shrinking tempdb regularly: it just regrows (and stalls)
-- ❌ Blaming files when the real issue is a query spilling to tempdb (hash/sort warnings)
-- ❌ Forgetting a long open transaction under RCSI keeps the version store from cleaning up
```

---

## 🎯 Interview Tip (1 line)
Say: "I confirm with PAGELATCH waits on 2:x:y pages, then add equally sized pre-grown files, consider memory-optimized tempdb metadata on 2019+, and reduce temp object churn and spills. Files are the cure for allocation contention only, not for slow queries."

---

## 🔗 Related Questions
→ Q146 (Table variables vs temp tables) | Q148 (Wait stats basics) | Q120 (RCSI) | Q155 (In-memory OLTP concepts)
