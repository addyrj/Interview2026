---

# Q109. Slow Query Diagnosis — Step-by-Step Workflow
# Category: Query Optimization
# Difficulty: ⭐⭐⭐⭐ Expert
# DB: Both (MySQL + PostgreSQL)

---

## ❓ Question
A production query suddenly becomes slow. Walk through your complete diagnosis and fix workflow. How do you find slow queries, read the execution plan, apply fixes, and verify improvement?

---

## 💡 Quick Concept (2 lines only)
Slow query diagnosis = 4 steps: (1) Identify the query (slow log / pg_stat_statements). (2) EXPLAIN ANALYZE to find the bottleneck node. (3) Apply fix (index, query rewrite, statistics update). (4) Verify improvement with EXPLAIN ANALYZE again.
हिंदी: 4 steps: slow query identify करो → EXPLAIN ANALYZE से bottleneck ढूंढो → fix apply करो → verify करो।

---

## ✅ Answer / Solution

```sql
-- ============================================
-- STEP 1: FIND THE SLOW QUERY
-- ============================================

-- MYSQL: Enable slow query log
-- In my.cnf or SET globally:
SET GLOBAL slow_query_log = 'ON';
SET GLOBAL long_query_time = 1;          -- log queries > 1 second
SET GLOBAL log_queries_not_using_indexes = 'ON';  -- also log no-index queries
SET GLOBAL slow_query_log_file = '/var/log/mysql/slow.log';

-- Analyze slow log with mysqldumpslow:
-- mysqldumpslow -s t -t 10 /var/log/mysql/slow.log
-- -s t = sort by total time, -t 10 = top 10 queries

-- MySQL performance_schema:
SELECT DIGEST_TEXT AS query,
  COUNT_STAR AS executions,
  ROUND(AVG_TIMER_WAIT / 1e12, 3) AS avg_seconds,
  ROUND(SUM_TIMER_WAIT / 1e12, 3) AS total_seconds
FROM performance_schema.events_statements_summary_by_digest
ORDER BY SUM_TIMER_WAIT DESC
LIMIT 10;

-- POSTGRESQL: pg_stat_statements (most powerful):
-- Enable in postgresql.conf:
-- shared_preload_libraries = 'pg_stat_statements'
-- pg_stat_statements.track = all

CREATE EXTENSION IF NOT EXISTS pg_stat_statements;

SELECT
  LEFT(query, 100) AS query_preview,
  calls,
  ROUND(mean_exec_time::numeric, 2) AS avg_ms,
  ROUND(total_exec_time::numeric / 1000, 2) AS total_seconds,
  ROUND((100 * total_exec_time / SUM(total_exec_time) OVER ())::numeric, 2) AS pct_total_time,
  rows / NULLIF(calls, 0) AS avg_rows
FROM pg_stat_statements
ORDER BY total_exec_time DESC
LIMIT 20;

-- Look for: high avg_ms (slow per call), OR high total_seconds (called many times × moderate time)
-- Reset statistics after fixes: SELECT pg_stat_statements_reset();

-- ============================================
-- STEP 2: REPRODUCE AND EXPLAIN ANALYZE
-- ============================================

-- The slow query (example):
SELECT u.id, u.name, u.email, COUNT(o.id) AS order_count
FROM users u
LEFT JOIN orders o ON u.id = o.user_id
WHERE u.created_at > '2024-01-01'
  AND o.status = 'completed'
GROUP BY u.id, u.name, u.email
ORDER BY order_count DESC
LIMIT 20;

-- Run EXPLAIN ANALYZE:
-- PgSQL:
EXPLAIN (ANALYZE, BUFFERS, FORMAT TEXT)
SELECT u.id, u.name, u.email, COUNT(o.id) AS order_count
FROM users u
LEFT JOIN orders o ON u.id = o.user_id
WHERE u.created_at > '2024-01-01'
  AND o.status = 'completed'
GROUP BY u.id, u.name, u.email
ORDER BY order_count DESC
LIMIT 20;

-- Sample SLOW output:
-- Limit  (cost=82943..82943 rows=20) (actual time=3842..3843 rows=20 loops=1)
--   ->  Sort  (cost=82943..83043) (actual time=3842..3842 rows=20 loops=1)
--         Sort Key: (count(o.id)) DESC
--         Sort Method: top-N heapsort  Memory: 27kB
--         ->  HashAggregate  (cost=82443..82543) (actual time=3801..3830 rows=45000)
--               ->  Hash Right Join  (cost=18000..82343)
--                     (actual time=500..3756 rows=180000 loops=1)
--                     Hash Cond: (o.user_id = u.id)
--                     Buffers: shared hit=234 read=5823  ← 5823 DISK READS!
--                     ->  Seq Scan on orders           ← FULL SCAN (no index used!)
--                           Filter: ((status)::text = 'completed'::text)
--                           Rows Removed by Filter: 820000  ← 820K rows scanned, 180K kept
--                     ->  Hash  (cost=14000..14000 rows=50000)
--                           ->  Seq Scan on users
--                                 Filter: (created_at > '2024-01-01')
--                                 Rows Removed by Filter: 10000
-- Execution Time: 3843ms  ← 3.8 SECONDS!

-- ============================================
-- STEP 3: IDENTIFY BOTTLENECK
-- ============================================

/*
Reading the plan (bottom-up — innermost nodes first):

NODE 1 — Seq Scan on orders (PROBLEM #1):
  Filter: status = 'completed'
  Rows Removed by Filter: 820,000  ← scans ALL orders, discards 82%!
  Buffers: read=5823 ← disk reads (not in cache)
  FIX: index on orders(status) or composite index

NODE 2 — Seq Scan on users:
  Filter: created_at > '2024-01-01'
  Rows Removed by Filter: 10,000
  FIX: index on users(created_at)

NODE 3 — HashAggregate:
  rows=45000 estimate but actual rows might vary
  Check: are GROUP BY columns indexed? Not an issue here — aggregation is necessary

NODE 4 — Sort (top-N heapsort):
  Sort Key: count(o.id) DESC
  This is ORDER BY on an aggregated value — hard to index
  But with LIMIT 20, heapsort is efficient for top-N → OK

Key metrics:
  ← Execution time: 3843ms = BAD (target < 100ms)
  ← shared read = 5823: too many disk reads (data not cached)
  ← Rows Removed by Filter: 820,000 → index needed!
*/

-- ============================================
-- STEP 4: APPLY FIXES
-- ============================================

-- FIX 1: Add indexes (PgSQL — CONCURRENTLY for zero downtime):
CREATE INDEX CONCURRENTLY idx_orders_status ON orders(status);
CREATE INDEX CONCURRENTLY idx_users_created ON users(created_at);

-- Better: composite index pushing status + user_id into one lookup:
CREATE INDEX CONCURRENTLY idx_orders_status_user ON orders(status, user_id);
-- Now: WHERE status = 'completed' + JOIN on user_id = both in one index!

-- MySQL:
CREATE INDEX idx_orders_status_user ON orders(status, user_id);
CREATE INDEX idx_users_created ON users(created_at);

-- FIX 2: Update statistics (in case estimates are wrong):
-- PgSQL:
ANALYZE users;
ANALYZE orders;
-- MySQL:
ANALYZE TABLE users, orders;

-- FIX 3: Query rewrite — the LEFT JOIN with WHERE on right table is effectively INNER JOIN:
-- WHERE o.status = 'completed' filters out NULL rows from LEFT JOIN → equivalent to INNER JOIN
-- Make it explicit (helps optimizer):
SELECT u.id, u.name, u.email, COUNT(o.id) AS order_count
FROM users u
INNER JOIN orders o ON u.id = o.user_id AND o.status = 'completed'  -- JOIN condition!
WHERE u.created_at > '2024-01-01'
GROUP BY u.id, u.name, u.email
ORDER BY order_count DESC
LIMIT 20;
-- Moving o.status = 'completed' to ON clause (not WHERE) is semantically cleaner for INNER JOIN

-- ============================================
-- STEP 5: VERIFY IMPROVEMENT
-- ============================================

-- Run EXPLAIN ANALYZE again after indexes:
EXPLAIN (ANALYZE, BUFFERS, FORMAT TEXT)
SELECT u.id, u.name, u.email, COUNT(o.id) AS order_count
FROM users u
INNER JOIN orders o ON u.id = o.user_id AND o.status = 'completed'
WHERE u.created_at > '2024-01-01'
GROUP BY u.id, u.name, u.email
ORDER BY order_count DESC
LIMIT 20;

-- Expected FAST output:
-- Limit  (cost=1234..1235 rows=20) (actual time=45..45 rows=20 loops=1)
--   ->  Sort  (actual time=45..45 rows=20 loops=1)
--         ->  HashAggregate (actual time=40..44 rows=12000 loops=1)
--               ->  Hash Join (actual time=2..35 rows=180000 loops=1)
--                     ->  Index Scan using idx_orders_status_user on orders
--                           Index Cond: (status = 'completed')
--                           Buffers: shared hit=1823 read=0  ← ALL FROM CACHE!
--                     ->  Bitmap Heap Scan on users
--                           Bitmap Index Scan on idx_users_created
-- Execution Time: 45ms  ← from 3843ms to 45ms! (85× improvement)

-- ============================================
-- COMMON BOTTLENECK PATTERNS & FIXES
-- ============================================

/*
PATTERN                 | SYMPTOM IN EXPLAIN              | FIX
────────────────────────┼─────────────────────────────────┼──────────────────────────
Missing index           | Seq Scan on large table         | CREATE INDEX CONCURRENTLY
Post-index filter       | Rows Removed by Filter: large # | Add filter col to composite index
No covering index       | "Index Scan" (not Index Only)   | Add missing cols to index
Filesort / disk sort    | Sort Method: external merge     | Index on ORDER BY columns
                        | Memory: 0kB (spill to disk)     | Or: increase work_mem
Stale statistics        | rows estimate >> actual rows    | ANALYZE table
Wrong join order        | Small table on wrong side       | SET enable_hashjoin=off to debug
                        |                                 | Or: SET join_collapse_limit
Correlated subquery     | "SubPlan" in explain            | Rewrite as JOIN or window fn
N+1 pattern             | Same query called N times       | Batch with IN or JOIN
Missing FK index (PgSQL)| Seq Scan on child for DELETE    | Index on FK column (PgSQL!)
                        | (PgSQL doesn't auto-index FKs!) |
Large result set        | High rows count on all nodes    | Add more specific WHERE clauses
                        |                                 | Paginate, add LIMIT
*/

-- ============================================
-- MYSQL-SPECIFIC DIAGNOSTIC TOOLS
-- ============================================

-- Show currently running queries (find what's blocking):
SHOW PROCESSLIST;
-- Or: SELECT * FROM information_schema.PROCESSLIST WHERE TIME > 5;

-- Show index usage:
SELECT TABLE_NAME, INDEX_NAME, SEQ_IN_INDEX, COLUMN_NAME, CARDINALITY
FROM information_schema.STATISTICS
WHERE TABLE_SCHEMA = 'mydb' AND TABLE_NAME = 'orders'
ORDER BY TABLE_NAME, INDEX_NAME, SEQ_IN_INDEX;

-- Show unused indexes:
SELECT * FROM sys.schema_unused_indexes
WHERE object_schema = 'mydb';

-- Show redundant indexes:
SELECT * FROM sys.schema_redundant_indexes WHERE table_schema = 'mydb';

-- ============================================
-- POSTGRESQL-SPECIFIC DIAGNOSTIC TOOLS
-- ============================================

-- Find tables with stale statistics:
SELECT schemaname, tablename, n_live_tup, n_dead_tup,
  last_analyze, last_autoanalyze
FROM pg_stat_user_tables
WHERE n_dead_tup > 10000
ORDER BY n_dead_tup DESC;

-- Find missing indexes (tables with lots of sequential scans):
SELECT relname AS table, seq_scan, idx_scan,
  ROUND(100.0 * idx_scan / NULLIF(seq_scan + idx_scan, 0), 2) AS idx_pct
FROM pg_stat_user_tables
WHERE seq_scan > 1000
ORDER BY seq_scan DESC
LIMIT 20;
-- Tables with high seq_scan and low idx_pct are good candidates for new indexes

-- Check index bloat:
SELECT indexname, pg_size_pretty(pg_relation_size(indexname::regclass)) AS size
FROM pg_indexes WHERE tablename = 'orders'
ORDER BY pg_relation_size(indexname::regclass) DESC;

-- Active queries with wait events (blocking?):
SELECT pid, state, wait_event_type, wait_event,
  NOW() - query_start AS duration, query
FROM pg_stat_activity
WHERE state != 'idle'
ORDER BY duration DESC;
```

---

## 🔍 Why This Works (3 lines max)
The workflow is: observe (slow log / pg_stat_statements) → understand (EXPLAIN ANALYZE, reading bottom-up) → hypothesize (index missing, stale stats, N+1) → fix (index, rewrite, ANALYZE) → verify (re-run EXPLAIN, compare times). The most impactful fixes are usually adding a composite index that covers both the WHERE filter and JOIN key, converting correlated subqueries to JOINs, and keeping statistics fresh.
हिंदी: Observe → understand → hypothesize → fix → verify। Most impactful fix = composite index (WHERE + JOIN key दोनों)। Correlated subquery → JOIN। Statistics fresh रखो।

---

## ⚡ Alternative Solution

```sql
-- PgSQL: auto_explain for automatic slow query logging with plans:
-- postgresql.conf:
-- shared_preload_libraries = 'auto_explain'
-- auto_explain.log_min_duration = 1000
-- auto_explain.log_analyze = true
-- auto_explain.log_buffers = true
-- Now: any query > 1s gets its EXPLAIN ANALYZE plan written to the error log automatically!
-- No manual EXPLAIN needed — plans captured in production
```

---

## ⚠️ Common Mistake

```sql
-- ❌ Wrong: Running EXPLAIN ANALYZE on expensive UPDATE/DELETE without transaction
EXPLAIN ANALYZE DELETE FROM orders WHERE status = 'old';
-- ACTUALLY DELETES ROWS! EXPLAIN ANALYZE runs the query!
-- ✅ Wrap in transaction:
BEGIN;
EXPLAIN ANALYZE DELETE FROM orders WHERE status = 'old';
ROLLBACK;  -- see the plan, undo the deletion

-- ❌ Wrong: Only checking EXPLAIN (not ANALYZE) — missing actual execution info
EXPLAIN SELECT ...;
-- Shows estimated rows and costs but NOT actual execution time or actual rows!
-- ✅ Always use EXPLAIN ANALYZE for diagnosis

-- ❌ Wrong: Adding indexes without measuring write performance impact
-- Every index = additional B-tree maintained on every INSERT/UPDATE/DELETE
-- ✅ Measure: benchmark INSERT throughput before/after adding indexes
-- Rule of thumb: < 5-6 indexes per table for write-heavy tables

-- ❌ Wrong: Forgetting PgSQL doesn't auto-index foreign keys
-- In MySQL InnoDB: FK columns get automatic indexes
-- In PgSQL: NO automatic index for FK columns!
-- DELETE from parent table → full scan of child table for each deleted parent row!
-- ✅ Always manually create index on FK columns in PgSQL:
CREATE INDEX idx_orders_user_id ON orders(user_id);
-- (FK: orders.user_id → users.id)
```

---

## 🎯 Interview Tip (1 line)
Say: "My workflow: find slow queries via pg_stat_statements or slow_query_log → EXPLAIN ANALYZE bottom-up (look for Seq Scans, high 'Rows Removed by Filter', disk reads) → apply fix (usually composite index covering WHERE + JOIN, or ANALYZE for stale stats) → verify by re-running EXPLAIN ANALYZE and checking execution time. I always test EXPLAIN ANALYZE wrapped in BEGIN/ROLLBACK for UPDATE/DELETE."

---

## 🔗 Related Questions
→ Q086 (EXPLAIN output) | Q084 (covering index) | Q081 (B-Tree internals) | Q108 (N+1 problem) | Q035 (correlated subquery)
