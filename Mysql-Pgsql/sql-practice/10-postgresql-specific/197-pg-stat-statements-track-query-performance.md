---

# Q197. pg_stat_statements — Track Query Performance
# Category: PostgreSQL Specific
# Difficulty: ⭐⭐ Medium
# DB: Both (PostgreSQL pg_stat_statements | MySQL performance_schema digest)

---

## ❓ Question
The database CPU is at 90%. How do you find the top queries by total time, by mean time and by calls, across all sessions, even for queries that finished long ago?

---

## 💡 Quick Concept (2 lines only)
`pg_stat_statements` is an extension that aggregates statistics per normalised query (literals replaced by $1, $2) : calls, total/mean time, rows, buffer hits. It must be preloaded, then `CREATE EXTENSION`.
हिंदी: pg_stat_statements हर normalised query के calls, total/mean time वगैरह जमा करता है; पहले shared_preload_libraries में डालना पड़ता है।

---

## ✅ Answer / Solution

```sql
-- ============================================
-- SETUP -- PostgreSQL  (NOT RUN: extension unavailable in PGlite;
--          I confirmed CREATE EXTENSION pg_stat_statements -> "extension is not available")
-- ============================================
-- postgresql.conf (restart required):
--   shared_preload_libraries = 'pg_stat_statements'
--   pg_stat_statements.track = all          -- top | all | none
--   compute_query_id = auto                 -- PG14+
-- then, in the database:
CREATE EXTENSION IF NOT EXISTS pg_stat_statements;

-- ============================================
-- SOLUTION (column names are PostgreSQL 13+; total_exec_time replaced total_time)
-- ============================================

-- Step 1: top 10 by TOTAL time = what burns the CPU
SELECT queryid,
       calls,
       round(total_exec_time::numeric, 1) AS total_ms,
       round(mean_exec_time::numeric, 2)  AS mean_ms,
       rows,
       left(query, 70)                    AS query
FROM pg_stat_statements
ORDER BY total_exec_time DESC
LIMIT 10;

-- Step 2: slow on average (even if rarely called)
SELECT calls, round(mean_exec_time::numeric, 2) AS mean_ms,
       round(stddev_exec_time::numeric, 2) AS stddev_ms, left(query, 70) AS query
FROM pg_stat_statements WHERE calls > 50 ORDER BY mean_exec_time DESC LIMIT 10;

-- Step 3: cache-unfriendly queries
SELECT left(query, 70) AS query,
       shared_blks_hit, shared_blks_read,
       round(100.0 * shared_blks_hit / NULLIF(shared_blks_hit + shared_blks_read, 0), 1) AS hit_pct
FROM pg_stat_statements ORDER BY shared_blks_read DESC LIMIT 10;

-- Step 4: reset counters before a load test
SELECT pg_stat_statements_reset();

-- ============================================
-- EXPECTED OUTPUT (illustrative -- NOT from a real run)
-- ============================================
-- queryid | calls  | total_ms  | mean_ms | rows   | query
-- 8123..  | 912344 | 4812340.2 | 5.27    | 912344 | SELECT * FROM orders WHERE customer_id = $1
-- 5521..  | 12     | 2210033.0 | 184169  | 12     | SELECT ... FROM events e JOIN ... GROUP BY ...
```

---

## 🔍 Why This Works (3 lines max)
Queries are fingerprinted after parsing, so `WHERE id = 5` and `WHERE id = 9` collapse into one row with summed stats. Sorting by total time finds the biggest aggregate cost (a 5 ms query called 900k times beats a rare slow one).
हिंदी: Query fingerprint होती है इसलिए अलग-अलग values वाली same query एक row में जुड़ जाती है; total time से असली बोझ दिखता है।

---

## ⚡ Alternative Solution

```sql
-- MySQL 9.1 (verified that these views exist and return data):
SELECT DIGEST_TEXT, COUNT_STAR,
       ROUND(SUM_TIMER_WAIT/1e12, 3) AS total_sec,      -- picoseconds -> seconds
       ROUND(AVG_TIMER_WAIT/1e9, 3)  AS avg_ms,
       SUM_ROWS_EXAMINED, SUM_ROWS_SENT
FROM performance_schema.events_statements_summary_by_digest
ORDER BY SUM_TIMER_WAIT DESC LIMIT 10;
-- Friendlier: SELECT query, exec_count, total_latency FROM sys.statement_analysis LIMIT 10;
-- Real output in my run (tiny sample): DIGEST_TEXT "SELECT `SLEEP` (?)", COUNT_STAR 1

-- Single-query deep dive in PostgreSQL (works in PGlite too):
EXPLAIN (ANALYZE, BUFFERS) SELECT ...;
-- Log slow ones: log_min_duration_statement = '500ms'   (MySQL: slow_query_log + long_query_time)
```

---

## ⚠️ Common Mistake

```sql
-- ❌ Querying the view without preloading the library
SELECT * FROM pg_stat_statements;
-- ERROR: pg_stat_statements must be loaded via "shared_preload_libraries"
-- ✅ Set it in postgresql.conf, RESTART, then CREATE EXTENSION

-- ❌ Using old column total_time on PG13+ (renamed to total_exec_time; plan time is separate)
-- ❌ Ordering only by mean_exec_time and missing the 900k-calls/5ms query that dominates load
-- ❌ Ignoring that the default pg_stat_statements.max = 5000 evicts rare statements
```

---

## 🎯 Interview Tip (1 line)
Say: "I start tuning from pg_stat_statements sorted by total_exec_time, then EXPLAIN (ANALYZE, BUFFERS) the top offenders, and fix by index or query rewrite; ORM-generated N+1 shows up as huge calls with tiny mean time."

---

## 🔗 Related Questions
→ Q196 (pg_stat_activity) | Q191 (VACUUM) | Q193 (Materialized views for heavy aggregates)
