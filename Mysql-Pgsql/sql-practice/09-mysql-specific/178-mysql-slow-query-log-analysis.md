---

# Q178. MySQL Slow Query Log Analysis
# Category: MySQL Specific
# Difficulty: ⭐⭐ Medium
# DB: MySQL (5.7 / 8.0+ / 9.x)

---

## ❓ Question
How do you enable the MySQL slow query log, what does an entry contain, and how do you find the worst queries using `mysqldumpslow` and `performance_schema`? What is the right `long_query_time`, and what is the gotcha when you change it at runtime?

---

## 💡 Quick Concept (2 lines only)
The slow query log records statements that run longer than `long_query_time` (and optionally those without indexes); aggregate it with `mysqldumpslow` or pt-query-digest to find the worst offenders by total time, not just single slow runs. `performance_schema` digests give the same view with no file parsing.
हिंदी: Slow log उन queries को लिखता है जो long_query_time से ज़्यादा चलीं; mysqldumpslow या performance_schema से कुल समय के हिसाब से worst queries मिलती हैं।

---

## ✅ Answer / Solution

```sql
-- ============================================
-- SETUP (verified on MySQL 9.1.0)
-- ============================================

SET GLOBAL slow_query_log_file = '/var/log/mysql/slow.log';
SET GLOBAL slow_query_log = ON;
SET GLOBAL long_query_time = 0.05;            -- seconds, fractions allowed. Production: 0.5-1s, tune down
SET GLOBAL log_queries_not_using_indexes = OFF; -- ON is noisy (logs tiny-table scans)
-- also useful: min_examined_row_limit, log_slow_extra=ON (8.0.14+, more fields), log_slow_admin_statements

CREATE TABLE big (id INT AUTO_INCREMENT PRIMARY KEY, user_id INT, payload VARCHAR(50));
SET SESSION cte_max_recursion_depth = 10000;  -- default 1000, my fill CTE needed more
INSERT INTO big (user_id, payload)
  WITH RECURSIVE n AS (SELECT 1 i UNION ALL SELECT i+1 FROM n WHERE i < 5000)
  SELECT i % 500, 'x' FROM n;
INSERT INTO big (user_id, payload) SELECT user_id, payload FROM big;   -- doubled 3 times -> 40,000 rows
INSERT INTO big (user_id, payload) SELECT user_id, payload FROM big;
INSERT INTO big (user_id, payload) SELECT user_id, payload FROM big;
SELECT SLEEP(0.2);                            -- deliberately slow statement

-- ============================================
-- SOLUTION: read the log entry
-- ============================================
-- Real slow.log entry (timestamps trimmed):
-- # Time: 2026-11-09T05:45:56.160963Z
-- # User@Host: root[root] @ localhost []  Id:    11
-- # Query_time: 0.205322  Lock_time: 0.000000 Rows_sent: 1  Rows_examined: 1
-- SELECT SLEEP(0.2);
--
-- # Query_time: 0.056246  Lock_time: 0.000001 Rows_sent: 0  Rows_examined: 20000
-- INSERT INTO big (user_id,payload) SELECT user_id,payload FROM big;
--
-- Key signal: Rows_examined >> Rows_sent  = missing/poor index (here: examined 20000, sent 0).

-- Aggregate with the bundled Perl script (shell, real output):
--   mysqldumpslow -s t -t 5 slow.log        (-s t = sort by total time, -t 5 = top 5)
-- Count: 1  Time=0.21s (0s)  Lock=0.00s (0s)  Rows=1.0 (1), root[root]@localhost
--   SELECT SLEEP(N.N)
-- Count: 1  Time=0.06s (0s)  Lock=0.00s (0s)  Rows=0.0 (0), root[root]@localhost
--   INSERT INTO big (user_id,payload) SELECT user_id,payload FROM big
-- (literals are normalised to N / 'S' so identical shapes group together)
-- My run printed "Died at ... line 163" after the report on 9.1.0 (script trips on the header lines);
-- the grouped output above was still produced. pt-query-digest (Percona) is the sturdier tool.

-- ============================================
-- No file needed: performance_schema digest (real output)
-- ============================================
SELECT DIGEST_TEXT, COUNT_STAR,
       ROUND(SUM_TIMER_WAIT/1e9,1) AS total_ms,
       SUM_ROWS_EXAMINED, SUM_NO_INDEX_USED
FROM performance_schema.events_statements_summary_by_digest
WHERE SCHEMA_NAME = 't'
ORDER BY SUM_TIMER_WAIT DESC LIMIT 3;
-- DIGEST_TEXT                                       | COUNT_STAR | total_ms | SUM_ROWS_EXAMINED | SUM_NO_INDEX_USED
-- SELECT `SLEEP` (?)                                | 1          | 205.4    | 1                 | 0
-- INSERT INTO `big` (...) SELECT ... FROM `big`     | 3          | 108.5    | 35000             | 3
-- INSERT INTO `big` (...) WITH RECURSIVE ...        | 2          | 20.7     | 5000              | 2
```

---

## 🔍 Why This Works (3 lines max)
The log is written after execution, so it captures real elapsed time, lock time and rows examined per statement; grouping by normalised text shows which query shape costs the most in total (1000 x 0.3s beats one 5s report). The digest table keeps the same aggregates in memory without log I/O.
हिंदी: Log execution के बाद लिखा जाता है, इसलिए असली time और rows examined मिलते हैं; normalised query से group करके total cost दिखती है।

---

## ⚡ Alternative Solution

```sql
-- Log to a table instead of a file (slower, but queryable):
SET GLOBAL log_output = 'TABLE';
SELECT start_time, query_time, rows_examined, sql_text FROM mysql.slow_log ORDER BY query_time DESC LIMIT 5;

-- Then explain the offender:
EXPLAIN ANALYZE SELECT COUNT(*) FROM big a JOIN big b ON a.user_id = b.user_id WHERE a.id < 200;   -- 8.0.18+

-- Percona toolkit (not run here):
--   pt-query-digest /var/log/mysql/slow.log | head -100

-- PostgreSQL equivalent: log_min_duration_statement = 500 (ms) + pg_stat_statements extension (Q190)
--   SELECT query, calls, total_exec_time, mean_exec_time FROM pg_stat_statements ORDER BY total_exec_time DESC LIMIT 10;
```

---

## ⚠️ Common Mistake

```sql
-- ❌ SET GLOBAL long_query_time = 0.05;  then testing in the SAME open session
-- GLOBAL only affects NEW connections. My first attempt logged nothing for exactly this reason.
-- ✅ Reconnect, or also run: SET SESSION long_query_time = 0.05;

-- ❌ long_query_time = 0 on a busy server  -> logs every statement, fills disk, adds I/O.
-- ✅ Use it only briefly for sampling; rotate with FLUSH SLOW LOGS.

-- ❌ Sorting by the single slowest query only.
-- ✅ Sort by TOTAL time (count x avg). A 0.2s query run 50k times/hour is the real problem.

-- ❌ log_queries_not_using_indexes = ON in production without min_examined_row_limit
```

---

## 🎯 Interview Tip (1 line)
Say: "I sample the slow log with a low threshold, rank digests by total time with pt-query-digest or performance_schema, then check Rows_examined vs Rows_sent and EXPLAIN ANALYZE before touching indexes."

---

## 🔗 Related Questions
→ Q162 (Buffer pool) | Q173 (Invisible indexes) | Q177 (Partitioning) | Q190 (pg_stat_statements)
