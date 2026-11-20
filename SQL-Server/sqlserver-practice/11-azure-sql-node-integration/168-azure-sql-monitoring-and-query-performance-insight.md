---

# Q168. Azure SQL Monitoring and Query Performance Insight
# Category: Azure SQL + Node.js Integration
# Difficulty: ⭐⭐ Medium
# DB: SQL Server (Azure SQL Database). PostgreSQL has pg_stat_statements, MySQL has performance_schema; neither has a built-in Query Performance Insight UI.

---

## ❓ Question
Users say the checkout API became slow around 11:00. With only Azure SQL Database and Azure Monitor, how do you find out whether the database is the bottleneck and which queries are responsible?

---

## 💡 Quick Concept (2 lines only)
Start at resource level (CPU, data IO, log write percent in Azure Monitor metrics or `sys.dm_db_resource_stats`), then drill into queries with Query Performance Insight, which reads Query Store data (on by default in Azure SQL Database). Set alerts so you hear about it before users do.
हिंदी: पहले resource देखो (CPU, IO), फिर Query Performance Insight / Query Store से slow query पकड़ो। Alert लगाओ।

---

## ✅ Answer / Solution

```sql
-- ============================================
-- NOT EXECUTED ON SQL SERVER / AZURE (no Azure instance available here).
-- Syntax parsed with sqlglot (tsql); behaviour per Microsoft docs. Row values depend on your database.
-- ============================================

-- 1) Resource pressure in roughly 15-second samples, kept about an hour (run in the user database)
SELECT TOP (20)
       end_time,
       avg_cpu_percent,
       avg_data_io_percent,
       avg_log_write_percent,
       avg_memory_usage_percent
FROM sys.dm_db_resource_stats
ORDER BY end_time DESC;
-- Expected per docs: percentages of your service tier limit. Sustained values near 100 = tier too small
-- or a bad query. For longer history use sys.resource_stats (run in master) or Azure Monitor metrics.

-- 2) Is Query Store on? (it feeds Query Performance Insight)
SELECT actual_state_desc, desired_state_desc
FROM sys.database_query_store_options;
-- Expected per docs: READ_WRITE for both on a default Azure SQL Database.

-- 3) Top CPU queries in the last day from Query Store (the data QPI charts)
SELECT TOP (5)
       q.query_id,
       LEFT(qt.query_sql_text, 80)                          AS QueryText,
       SUM(rs.count_executions)                              AS Executions,
       SUM(rs.avg_cpu_time * rs.count_executions) / 1000.0   AS TotalCpuMs
FROM sys.query_store_query_text        AS qt
JOIN sys.query_store_query             AS q   ON q.query_text_id = qt.query_text_id
JOIN sys.query_store_plan              AS p   ON p.query_id = q.query_id
JOIN sys.query_store_runtime_stats     AS rs  ON rs.plan_id = p.plan_id
JOIN sys.query_store_runtime_stats_interval AS i ON i.runtime_stats_interval_id = rs.runtime_stats_interval_id
WHERE i.start_time > DATEADD(DAY, -1, SYSUTCDATETIME())
GROUP BY q.query_id, LEFT(qt.query_sql_text, 80)
ORDER BY TotalCpuMs DESC;

-- 4) Who is running / waiting right now
SELECT r.session_id, r.status, r.wait_type, r.total_elapsed_time, r.blocking_session_id
FROM sys.dm_exec_requests AS r
WHERE r.session_id <> @@SPID;
-- Expected per docs: a row per active request; wait_type is NULL when it is running on CPU.
-- Interpreting wait types is a topic of its own (Q148); not listed here.
```

```javascript
// Node.js: tag your connections so you can find your own app in DMVs and logs
const config = {
  server: 'sql-shop-prod.database.windows.net',
  database: 'ShopDb',
  options: { encrypt: true, appName: 'shop-api-checkout' }   // shows up as program_name in sys.dm_exec_sessions
};
```

---

## 🔍 Why This Works (3 lines max)
`sys.dm_db_resource_stats` tells you whether the database is out of a resource at all, which separates an app problem from a database one. Query Store persists plans and runtime stats per interval, so you can compare 11:00 against yesterday instead of guessing. Query Performance Insight in the portal is just a friendly view over that data.
हिंदी: पहले पूछो: DB सच में busy है? Query Store पुराने data से compare करने देता है। QPI उसी का UI है।

---

## ⚡ Alternative Solution

```sql
-- Portal / Azure Monitor alternatives (no T-SQL):
--   * Metrics: CPU percentage, DTU/vCore percentage, deadlocks, failed connections -> alert rules
--   * Diagnostic settings -> Log Analytics workspace to keep long history and run KQL
--   * Intelligent Insights / Automatic tuning (force last good plan, index recommendations)
--     are available in Azure SQL Database; review recommendations before enabling auto-apply.
-- Query Store plan regression: compare plans for one query_id and force the previous plan if needed (Q113).
```

---

## ⚠️ Common Mistake

```sql
-- ❌ Wrong: scaling the tier first and investigating later. One missing index can eat any size.
-- ❌ Wrong: reading only averages. A p95/p99 spike hides inside an average CPU of 40 percent.
-- ❌ Wrong: relying on sys.dm_db_resource_stats for history; it keeps only a short window.
-- ❌ Wrong: no alerts: you find out about CPU at 100 percent from a customer.
```

---

## 🎯 Interview Tip (5+ YOE level)
Say: "My order is metrics, then Query Store, then plan. I check resource percentages, find the top consumers by CPU, duration and IO in Query Performance Insight, look at the plan for scans or key lookups, fix with an index or query rewrite, and verify with Query Store afterwards. Alerts and a stored baseline mean I know what normal looks like." Add that the app should set `appName` per service so DMVs show who is who.

---

## 🔗 Related Questions
→ Q113 (Query Store basics) | Q142 (finding slow queries) | Q148 (wait stats basics) | Q156 (monitoring and baselines) | Q167 (elastic pools and scaling)
