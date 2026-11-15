---

# Q111. MySQL Slow Query Log Setup
# Category: Query Optimization
# Difficulty: ⭐⭐ Medium
# DB: MySQL (PostgreSQL equivalent noted below)

---

## ❓ Question
Production API is slow at peak hours and nobody knows which queries are responsible. How do you enable the MySQL slow query log, decide what counts as "slow", read it, and find the top offenders without restarting the server?

---

## 💡 Quick Concept (2 lines only)
The slow query log records every statement that runs longer than `long_query_time` (optionally also those that use no index), with Query_time, Lock_time, Rows_sent and Rows_examined. A big gap between Rows_examined and Rows_sent is the classic missing-index signal.
हिंदी: Slow query log हर उस query को लिखता है जो `long_query_time` से ज़्यादा चले; Rows_examined बहुत बड़ा और Rows_sent छोटा हो तो index missing है।

---

## ✅ Answer / Solution

```sql
-- Verified on MySQL 9.1.0 (same variables exist in 5.7 / 8.0)

-- ============================================
-- SETUP (run this first)
-- ============================================

CREATE DATABASE IF NOT EXISTS shop;
USE shop;

CREATE TABLE orders (
  id          INT AUTO_INCREMENT PRIMARY KEY,
  customer_id INT,
  amount      DECIMAL(10,2),
  created_at  DATETIME
);

INSERT INTO orders (customer_id, amount, created_at) VALUES
  (1, 10.00, '2024-01-01'),
  (2, 20.00, '2024-01-02'),
  (3, 30.00, '2024-01-03');

-- ============================================
-- SOLUTION
-- ============================================

-- Step 1: inspect current settings (defaults: OFF, 10 sec, FILE)
SHOW VARIABLES WHERE Variable_name IN
  ('slow_query_log','long_query_time','log_output',
   'log_queries_not_using_indexes','slow_query_log_file');

-- Step 2: enable at runtime (no restart). Needs SUPER / SYSTEM_VARIABLES_ADMIN.
SET GLOBAL slow_query_log   = 'ON';
SET GLOBAL long_query_time  = 0.2;     -- seconds, fractions allowed
SET GLOBAL log_output       = 'TABLE'; -- 'FILE' (default) or 'TABLE' or 'FILE,TABLE'
SET GLOBAL log_queries_not_using_indexes = 'ON';  -- noisy! use with min_examined_row_limit
SET GLOBAL min_examined_row_limit = 0;

-- Step 3: generate a slow query and an unindexed query
SELECT SLEEP(0.5);                              -- slow: 0.5s > 0.2s
SELECT * FROM orders WHERE customer_id = 2;     -- fast but full scan (no index)

-- Step 4: read the log (TABLE output)
SELECT start_time, query_time, rows_examined, rows_sent,
       CONVERT(sql_text USING utf8mb4) AS sql_text
FROM mysql.slow_log
ORDER BY query_time DESC;

-- Step 5: make it permanent in my.cnf
-- [mysqld]
-- slow_query_log      = 1
-- slow_query_log_file = /var/log/mysql/slow.log
-- long_query_time     = 0.5
-- log_slow_extra      = ON      -- 8.0.14+: adds Bytes_sent, Tmp_tables, etc. (FILE only)

-- Step 6: summarise a FILE log from the shell (ships with MySQL)
-- mysqldumpslow -s t -t 10 /var/log/mysql/slow.log   -- top 10 by total time
-- (also: pt-query-digest from Percona Toolkit for much better reports)

-- ============================================
-- EXPECTED OUTPUT
-- ============================================

-- Defaults (SHOW VARIABLES), real output:
-- log_output                    | FILE
-- log_queries_not_using_indexes | OFF
-- long_query_time               | 10.000000
-- slow_query_log                | OFF
--
-- After the SET GLOBALs, a NEW connection ran SELECT SLEEP(0.5). mysql.slow_log:
-- query_time      | rows_examined | sql_text
-- 00:00:00.503295 | 1             | SELECT SLEEP(0.5)
--
-- The unindexed SELECT (log_queries_not_using_indexes=ON) was logged too:
-- 00:00:00.000192 | 3 | SELECT * FROM orders WHERE customer_id = 2
-- (rows_examined 3, rows_sent 1 -> full scan). Timings vary per run.
--
-- FILE output looks like (real):
-- # Time: 2026-11-06T05:16:39.513585Z
-- # User@Host: root[root] @ localhost []  Id:    11
-- # Query_time: 0.405076  Lock_time: 0.000000 Rows_sent: 1  Rows_examined: 1
-- SET timestamp=1793942199;
-- SELECT SLEEP(0.4);
```

---

## 🔍 Why This Works (3 lines max)
The server compares each statement's execution time to `long_query_time` after it finishes and appends a record if it exceeded it. `SET GLOBAL long_query_time` only applies to NEW connections, because each session copies the value at connect time. Logging to TABLE is convenient for ad-hoc SQL; FILE is cheaper and works with mysqldumpslow / pt-query-digest.
हिंदी: `SET GLOBAL long_query_time` सिर्फ़ नए connections पर लागू होता है, पुराने session में पुरानी value रहती है।

---

## ⚡ Alternative Solution

```sql
-- Current session only (works immediately, no privileges beyond session vars):
SET SESSION long_query_time = 0;     -- log EVERYTHING for this connection (debugging)

-- Performance Schema (no log file; always on in 8.0): top statements by total time
SELECT DIGEST_TEXT, COUNT_STAR, ROUND(SUM_TIMER_WAIT/1e12,3) AS total_sec,
       SUM_ROWS_EXAMINED, SUM_ROWS_SENT
FROM performance_schema.events_statements_summary_by_digest
ORDER BY SUM_TIMER_WAIT DESC
LIMIT 10;   -- (not run in this session; same idea as PgSQL pg_stat_statements, see Q112)

-- PostgreSQL equivalent of the slow log:
--   postgresql.conf:  log_min_duration_statement = 200   -- ms; -1 disables, 0 logs all
--   or:  ALTER SYSTEM SET log_min_duration_statement = '200ms'; SELECT pg_reload_conf();
-- (PgSQL syntax shown from knowledge; not run - PGlite has no server log.)
```

---

## ⚠️ Common Mistake
```sql
-- ❌ Setting long_query_time = 0 globally on a busy production box
--    -> log grows by GBs/hour and the logging itself adds I/O load.
-- ❌ SET GLOBAL long_query_time = 1; then testing in the SAME old connection
--    -> the session still uses the old value, nothing gets logged. Reconnect.
-- ❌ Turning on log_queries_not_using_indexes without min_examined_row_limit
--    -> tiny lookup tables flood the log (a 3-row full scan is not a problem).
-- ✅ Start at 0.5-1s, add min_examined_row_limit = 1000, rotate the file
--    (logrotate + FLUSH SLOW LOGS), then lower the threshold gradually.
```

---

## 🎯 Interview Tip (1 line)
Say: "I enable slow log with a 0.5s threshold, aggregate with pt-query-digest or performance_schema digests, rank by TOTAL time (count x avg) not worst single run, then EXPLAIN the top offenders - and I remember GLOBAL changes only affect new connections."

---

## 🔗 Related Questions
→ Q109 (Slow query diagnosis) | Q112 (pg_stat_statements) | Q108 (N+1 problem) | Q114 (Statistics / ANALYZE)
