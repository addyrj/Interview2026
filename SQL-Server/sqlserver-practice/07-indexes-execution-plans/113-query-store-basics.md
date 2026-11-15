---

# Q113. Query Store Basics
# Category: Indexes + Execution Plans
# Difficulty: ⭐⭐ Medium
# DB: SQL Server 2016+ / Azure SQL (MySQL has performance_schema, PostgreSQL has pg_stat_statements — no plan history built in)

---

## ❓ Question
Production got slow after last night's deployment. How do you use Query Store to find the regressed query, compare its old and new plans, and force the good plan? Enable it and write the query that lists the top 5 queries by average duration.

---

## 💡 Quick Concept (2 lines only)
Query Store is a per-database flight recorder: it persists query text, every plan and runtime stats (duration, CPU, reads, executions) per time interval, so history survives restarts and plan-cache eviction. You can force a known good plan with `sp_query_store_force_plan`.
हिंदी: Query Store = database का black box recorder। Query, plans, runtime stats सब save रहते हैं। Regression आए तो पुराना अच्छा plan force कर सकते हो।

---

## ✅ Answer / Solution

NOTE: not executed on SQL Server; behaviour per Microsoft docs. There is no equivalent engine here, so no result sets are shown (numbers would be invented).

```sql
-- ============================================
-- SETUP: enable Query Store (ON by default for new DBs in SQL 2022 and Azure SQL)
-- ============================================

ALTER DATABASE ShopDb SET QUERY_STORE = ON;

ALTER DATABASE ShopDb SET QUERY_STORE (
  OPERATION_MODE = READ_WRITE,
  QUERY_CAPTURE_MODE = AUTO,          -- ignore trivial one-off queries
  MAX_STORAGE_SIZE_MB = 1024,
  INTERVAL_LENGTH_MINUTES = 60,
  CLEANUP_POLICY = (STALE_QUERY_THRESHOLD_DAYS = 30)
);

-- Check the state (actual_state_desc should be READ_WRITE)
SELECT actual_state_desc, desired_state_desc, current_storage_size_mb
FROM sys.database_query_store_options;

-- ============================================
-- SOLUTION: top 5 queries by average duration in the last 24 hours
-- ============================================

SELECT TOP 5
    q.query_id,
    qt.query_sql_text,
    COUNT(DISTINCT p.plan_id)                      AS plan_count,   -- >1 = plan changed
    SUM(rs.count_executions)                       AS executions,
    SUM(rs.avg_duration * rs.count_executions)
        / NULLIF(SUM(rs.count_executions), 0)      AS weighted_avg_duration_us  -- microseconds
FROM sys.query_store_query_text AS qt
JOIN sys.query_store_query AS q          ON q.query_text_id = qt.query_text_id
JOIN sys.query_store_plan AS p           ON p.query_id = q.query_id
JOIN sys.query_store_runtime_stats AS rs ON rs.plan_id = p.plan_id
JOIN sys.query_store_runtime_stats_interval AS i
                                         ON i.runtime_stats_interval_id = rs.runtime_stats_interval_id
WHERE i.start_time > DATEADD(HOUR, -24, SYSDATETIMEOFFSET())
GROUP BY q.query_id, qt.query_sql_text
ORDER BY weighted_avg_duration_us DESC;

-- ============================================
-- FIND A REGRESSION: queries with more than one plan
-- ============================================

SELECT q.query_id, p.plan_id, p.last_execution_time
FROM sys.query_store_query AS q
JOIN sys.query_store_plan AS p ON p.query_id = q.query_id
WHERE q.query_id IN (
    SELECT query_id FROM sys.query_store_plan GROUP BY query_id HAVING COUNT(*) > 1
)
ORDER BY q.query_id, p.plan_id;

-- ============================================
-- FORCE the good plan (ids come from the queries above / SSMS "Regressed Queries" report)
-- ============================================

EXEC sys.sp_query_store_force_plan @query_id = 42, @plan_id = 17;

-- Undo when the underlying issue is really fixed:
EXEC sys.sp_query_store_unforce_plan @query_id = 42, @plan_id = 17;
```

---

## 🔍 Why This Works (3 lines max)
Query Store writes to internal tables inside the user database, so data survives restart, failover and plan-cache flush (unlike sys.dm_exec_query_stats). Runtime stats are aggregated per interval, so you compare "before deploy" and "after deploy" windows. Forcing a plan tells the optimizer to reuse that plan shape for the query, which is a quick mitigation without touching code.
हिंदी: Data database के अंदर save होता है, restart के बाद भी रहता है। Interval-wise stats से before/after compare करो। Force plan = जल्दी fix, code बदले बिना।

---

## ⚡ Alternative Solution

```sql
-- Without Query Store: the plan cache DMV (volatile — cleared on restart / memory pressure)
SELECT TOP 5
    qs.total_elapsed_time / qs.execution_count AS avg_elapsed_us,
    qs.execution_count,
    SUBSTRING(st.text, 1, 200)                 AS query_text
FROM sys.dm_exec_query_stats AS qs
CROSS APPLY sys.dm_exec_sql_text(qs.sql_handle) AS st
ORDER BY avg_elapsed_us DESC;

-- Azure SQL: Query Performance Insight in the portal is a UI over the same Query Store data.
```

---

## ⚠️ Common Mistake

```sql
-- ❌ Wrong: assuming Query Store is always recording
-- If the store hits MAX_STORAGE_SIZE_MB it flips to READ_ONLY and silently stops capturing.
-- ✅ Monitor it:
SELECT actual_state_desc, readonly_reason, current_storage_size_mb, max_storage_size_mb
FROM sys.database_query_store_options;

-- ❌ Wrong: QUERY_CAPTURE_MODE = ALL on a busy OLTP box (huge overhead and storage)
-- ✅ Use AUTO (default) so cheap ad-hoc noise is skipped.

-- ❌ Wrong: forcing a plan and forgetting it
-- A forced plan can fail (e.g. index dropped) and the query falls back to a normal plan.
-- ✅ Review forced plans regularly (sys.query_store_plan.is_forced_plan) and track failures.

-- ❌ Wrong: reading avg_duration as milliseconds — it is in microseconds.
```

---

## 🎯 Interview Tip (1 line)
Say: "After a regression I open Query Store's Regressed Queries view, compare the plan before and after the change, check whether it is parameter sniffing or a stats/index change, and force the last good plan as a stop-gap while I fix the root cause. I also keep Query Store READ_WRITE with size monitoring, because on Azure SQL it is my main performance history tool."

---

## 🔗 Related Questions
→ Q114 (parameter sniffing) | Q112 (missing index DMVs) | Q142 (finding slow queries) | Q151 (parameter sniffing deep-dive)
