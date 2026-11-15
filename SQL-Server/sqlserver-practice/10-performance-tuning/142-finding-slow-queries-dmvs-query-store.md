---

# Q142. Finding Slow Queries — DMVs and Query Store
# Category: Performance Tuning
# Difficulty: ⭐⭐⭐ Hard
# DB: SQL Server (MySQL: slow query log / performance_schema | PostgreSQL: pg_stat_statements). Not executed on SQL Server; behaviour per Microsoft docs.

---

## ❓ Question
Production API is "slow since yesterday". Find the top 10 queries by total CPU and by average duration, see their text, and use Query Store to compare yesterday's plan with today's.

---

## 💡 Quick Concept (2 lines only)
`sys.dm_exec_query_stats` holds aggregated stats for plans currently in cache (lost on restart/eviction). Query Store persists query text, plans and runtime stats per time interval in the database, so you can compare before/after.
हिंदी: DMV = अभी cache में जो plans हैं उनके stats (restart पर गायब)। Query Store = history database में सेव रहती है, plan regression पकड़ने के लिए बेस्ट।

---

## ✅ Answer / Solution

```sql
-- ============================================
-- SETUP (not executed on SQL Server; behaviour per Microsoft docs)
-- Query Store is ON by default for new databases from SQL Server 2022 and Azure SQL
-- ============================================
ALTER DATABASE ShopDB SET QUERY_STORE = ON;
ALTER DATABASE ShopDB SET QUERY_STORE (OPERATION_MODE = READ_WRITE, QUERY_CAPTURE_MODE = AUTO);

-- ============================================
-- 1) DMV: top 10 by total CPU (plan cache; times are in microseconds)
-- ============================================
SELECT TOP 10
    qs.total_worker_time / 1000.0           AS total_cpu_ms,
    qs.execution_count,
    qs.total_elapsed_time / qs.execution_count / 1000.0 AS avg_duration_ms,
    qs.total_logical_reads / qs.execution_count AS avg_reads,
    SUBSTRING(st.text, (qs.statement_start_offset / 2) + 1,
        ((CASE qs.statement_end_offset WHEN -1 THEN DATALENGTH(st.text)
          ELSE qs.statement_end_offset END - qs.statement_start_offset) / 2) + 1) AS statement_text
FROM sys.dm_exec_query_stats AS qs
CROSS APPLY sys.dm_exec_sql_text(qs.sql_handle) AS st
ORDER BY qs.total_worker_time DESC;

-- ============================================
-- 2) Query Store: slowest by average duration in the last 24h
-- ============================================
SELECT TOP 10
    q.query_id,
    qt.query_sql_text,
    SUM(rs.count_executions)                       AS executions,
    SUM(rs.avg_duration * rs.count_executions) / SUM(rs.count_executions) / 1000.0 AS avg_duration_ms
FROM sys.query_store_query q
JOIN sys.query_store_query_text qt    ON qt.query_text_id = q.query_text_id
JOIN sys.query_store_plan p           ON p.query_id = q.query_id
JOIN sys.query_store_runtime_stats rs ON rs.plan_id = p.plan_id
JOIN sys.query_store_runtime_stats_interval i ON i.runtime_stats_interval_id = rs.runtime_stats_interval_id
WHERE i.start_time > DATEADD(HOUR, -24, SYSUTCDATETIME())
GROUP BY q.query_id, qt.query_sql_text
ORDER BY avg_duration_ms DESC;

-- 3) Queries with more than one plan = plan regression suspects
SELECT query_id, COUNT(DISTINCT plan_id) AS plan_count
FROM sys.query_store_plan
GROUP BY query_id
HAVING COUNT(DISTINCT plan_id) > 1;

-- 4) Force the good plan (after verifying in Query Store reports)
EXEC sp_query_store_force_plan @query_id = 48, @plan_id = 49;

-- EXPECTED OUTPUT: shape only, values depend on your workload (nothing invented here):
--   total_cpu_ms | execution_count | avg_duration_ms | avg_reads | statement_text
```

---

## 🔍 Why This Works (3 lines max)
The DMV shows what is hot right now with cheap setup; Query Store adds time and plan history, so "was fast yesterday" becomes provable. Always rank by total cost (avg x executions), not only by the single slowest call, because a 20 ms query run 5 million times beats a 10 s report.
हिंदी: Total cost = avg x executions। 20ms वाली query लाखों बार चले तो वही असली problem है।

---

## ⚡ Alternative Solution

```sql
-- Currently running requests + blockers (live view, not history)
SELECT r.session_id, r.status, r.wait_type, r.total_elapsed_time, r.blocking_session_id, t.text
FROM sys.dm_exec_requests r
CROSS APPLY sys.dm_exec_sql_text(r.sql_handle) t
WHERE r.session_id > 50;

-- Extended Events / Azure: Query Performance Insight (Q168) and Intelligent Insights.
```

---

## ⚠️ Common Mistake

```sql
-- ❌ Trusting dm_exec_query_stats after a restart or memory pressure: the cache was emptied
-- ❌ Ignoring that statement_start/end_offset are in BYTES of Unicode text (hence / 2)
-- ❌ Forcing a plan without checking why it regressed (stats, parameter sniffing, missing index)
--    A forced plan can fail silently if the index it needs is dropped.
-- ❌ Turning Query Store to READ_ONLY when it hits max size: capture stops. Set size + cleanup policy.
```

---

## 🎯 Interview Tip (1 line)
Say: "I start with Query Store top resource consumers by total CPU/duration/reads, check for multi-plan queries, then confirm in the plan (scan vs seek, estimate vs actual rows). DMVs are for the live picture. I fix the root cause - index, stats, sniffing - and only force a plan as a stopgap."

---

## 🔗 Related Questions
→ Q113 (Query Store basics) | Q112 (Missing index DMVs) | Q148 (Wait stats basics) | Q151 (Parameter sniffing deep-dive)
