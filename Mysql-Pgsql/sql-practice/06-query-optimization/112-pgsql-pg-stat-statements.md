---

# Q112. PgSQL pg_stat_statements
# Category: Query Optimization
# Difficulty: ⭐⭐ Medium
# DB: PostgreSQL

---

## ❓ Question
How do you find the most expensive queries in PostgreSQL across thousands of different parameter values? Enable `pg_stat_statements`, explain what it normalizes, and write the queries to rank by total time, mean time and calls.

---

## 💡 Quick Concept (2 lines only)
`pg_stat_statements` keeps one row per normalized query (constants replaced by `$1, $2`) with calls, total/mean/max time, rows and buffer counters. It must be loaded via `shared_preload_libraries` (restart needed), then `CREATE EXTENSION` in each database.
हिंदी: `pg_stat_statements` हर query को normalize करके (values की जगह `$1`) calls और time जोड़ देता है; इसे `shared_preload_libraries` में डालकर restart करना पड़ता है।

---

## ✅ Answer / Solution

```sql
-- Verified on PGlite (PostgreSQL 18.6 compiled to WASM) with its pg_stat_statements contrib module.
-- On a real server you first need (restart required):
--   postgresql.conf:  shared_preload_libraries = 'pg_stat_statements'
--                     pg_stat_statements.track = all     -- top (default) | all | none
--                     compute_query_id = on              -- auto since PG14

-- ============================================
-- SETUP (run this first)
-- ============================================

CREATE EXTENSION IF NOT EXISTS pg_stat_statements;

CREATE TABLE orders (
  id          SERIAL PRIMARY KEY,
  customer_id INT,
  amount      NUMERIC(10,2),
  status      TEXT
);

INSERT INTO orders (customer_id, amount, status)
SELECT g % 100, g, 'paid' FROM generate_series(1, 5000) g;

-- ============================================
-- SOLUTION
-- ============================================

-- Step 1: run a workload (two different constants, one query shape)
SELECT * FROM orders WHERE customer_id = 5;
SELECT * FROM orders WHERE customer_id = 7;
SELECT count(*), sum(amount) FROM orders WHERE status = 'paid';

-- Step 2: top queries by TOTAL time (what actually costs you the most)
SELECT calls,
       rows,
       round(total_exec_time::numeric, 2) AS total_ms,
       round(mean_exec_time::numeric, 2)  AS mean_ms,
       round((100 * total_exec_time / sum(total_exec_time) OVER ())::numeric, 1) AS pct_of_total,
       query
FROM pg_stat_statements
WHERE query NOT LIKE '%pg_stat_statements%'
ORDER BY total_exec_time DESC
LIMIT 10;

-- Step 3: other useful cuts
--   ORDER BY mean_exec_time DESC   -> consistently slow queries
--   ORDER BY calls DESC            -> chatty queries (N+1 suspects)
--   ORDER BY shared_blks_read DESC -> I/O heavy (cache misses)
--   ORDER BY stddev_exec_time DESC -> unstable latency

-- Step 4: reset after a deploy so numbers reflect the new code
SELECT pg_stat_statements_reset();

-- ============================================
-- EXPECTED OUTPUT
-- ============================================

-- Real output, filtered to our table (times omitted, they vary per run):
-- calls | rows | query
-- 2     | 100  | SELECT * FROM orders WHERE customer_id = $1
-- 1     | 5000 | INSERT INTO orders(customer_id, amount, status) SELECT g%$1, g, $2 FROM generate_series($3,$4) g
-- 1     | 0    | CREATE TABLE orders (id serial primary key, customer_id int, amount numeric(10,2), status text)
-- 1     | 1    | SELECT count(*), sum(amount) FROM orders WHERE status=$1
--
-- Note: customer_id = 5 and customer_id = 7 collapsed into ONE row (calls = 2, rows = 50 + 50).
-- After pg_stat_statements_reset(): SELECT count(*) FROM pg_stat_statements -> 1 (only the count query itself).
```

---

## 🔍 Why This Works (3 lines max)
Every executed statement is hashed to a `queryid` after constants are stripped, so 10,000 lookups with different IDs become one row you can rank. Ranking by `total_exec_time` surfaces the biggest cost to the system, which is usually a medium-speed query called millions of times, not the one 30-second report.
हिंदी: Constants हटाकर एक ही query shape की एक row बनती है, इसलिए `total_exec_time` से असली भारी query मिलती है।

---

## ⚡ Alternative Solution

```sql
-- MySQL equivalent: performance_schema digests (see Q111)
SELECT DIGEST_TEXT, COUNT_STAR, SUM_TIMER_WAIT/1e12 AS total_sec
FROM performance_schema.events_statements_summary_by_digest
ORDER BY SUM_TIMER_WAIT DESC LIMIT 10;      -- MySQL, not run here

-- Log only slow ones instead of aggregating (PgSQL):
--   ALTER SYSTEM SET log_min_duration_statement = '250ms'; SELECT pg_reload_conf();

-- Pair with auto_explain to capture PLANS of slow statements:
--   shared_preload_libraries = 'pg_stat_statements,auto_explain'
--   auto_explain.log_min_duration = '500ms'

-- Column names: PG13+ uses total_exec_time / mean_exec_time.
-- PG12 and older used total_time / mean_time.
```

---

## ⚠️ Common Mistake
```sql
-- ❌ CREATE EXTENSION pg_stat_statements; without shared_preload_libraries
--    -> the view exists but querying it errors:
--       "pg_stat_statements must be loaded via shared_preload_libraries"
-- ❌ Sorting by mean_exec_time only -> you chase rare slow queries and miss the
--    cheap-but-called-10M-times query that eats the CPU.
-- ❌ Never resetting -> stats include ancient pre-deploy code.
-- ✅ Rank by total_exec_time, check calls and mean, reset after releases,
--    and snapshot the view into a table periodically for trend graphs.
```

---

## 🎯 Interview Tip (1 line)
Say: "I load pg_stat_statements at startup, rank by total_exec_time with percent-of-total, then take the top few queryids to EXPLAIN (ANALYZE, BUFFERS) - and I add auto_explain to catch the plan, since pg_stat_statements has no plans or parameter values."

---

## 🔗 Related Questions
→ Q111 (MySQL slow query log) | Q109 (Slow query diagnosis) | Q113 (Prepared statements) | Q114 (ANALYZE)
