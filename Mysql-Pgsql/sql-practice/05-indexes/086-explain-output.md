---

# Q086. Reading EXPLAIN — MySQL vs PostgreSQL EXPLAIN ANALYZE
# Category: Indexes
# Difficulty: ⭐⭐⭐ Hard
# DB: Both (MySQL + PostgreSQL)

---

## ❓ Question
How do you read EXPLAIN output in MySQL and EXPLAIN ANALYZE in PostgreSQL? What are the critical columns and values to watch for? Show a slow query diagnosis and fix.

---

## 💡 Quick Concept (2 lines only)
EXPLAIN shows the query execution plan — what the optimizer PLANS to do (estimates). EXPLAIN ANALYZE actually RUNS the query and shows what ACTUALLY happened (timing + actual rows). MySQL and PgSQL have different output formats but similar concepts.
हिंदी: EXPLAIN = optimizer का plan (estimates)। EXPLAIN ANALYZE = actual execution (real timing)। दोनों में type/key/rows देखो।

---

## ✅ Answer / Solution

```sql
-- ============================================
-- SETUP
-- ============================================

CREATE TABLE orders (
  id         BIGINT PRIMARY KEY AUTO_INCREMENT,
  user_id    INT NOT NULL,
  status     VARCHAR(20),
  amount     DECIMAL(10,2),
  created_at DATETIME NOT NULL
);

CREATE INDEX idx_user ON orders(user_id);
-- Insert 1M sample rows (imagine)

-- ============================================
-- MYSQL EXPLAIN — KEY COLUMNS
-- ============================================

EXPLAIN SELECT o.id, o.amount, o.status
FROM orders o
WHERE o.user_id = 42
  AND o.status = 'pending'
ORDER BY o.created_at DESC
LIMIT 10;

-- Sample output:
-- +----+-------------+-------+------+----------+----------+---------+------+------+-----------------------------+
-- | id | select_type | table | type | key      | key_len  | ref     | rows | filt | Extra                       |
-- +----+-------------+-------+------+----------+----------+---------+------+------+-----------------------------+
-- |  1 | SIMPLE      | o     | ref  | idx_user | 4        | const   | 5000 |  10  | Using index condition; ...  |
-- +----+-------------+-------+------+----------+----------+---------+------+------+-----------------------------+

-- ============================================
-- MYSQL EXPLAIN COLUMN BREAKDOWN
-- ============================================

/*
Column: type (ACCESS METHOD — most important!)
───────────────────────────────────────────────
Best → Worst:
  const     → PK or unique index equality (fastest, returns 1 row max)
  eq_ref    → unique index join (one row per outer row — great for JOINs)
  ref       → non-unique index equality (WHERE indexed_col = value)
  range     → index range scan (WHERE id BETWEEN 1 AND 100)
  index     → full index scan (reads entire index — better than ALL)
  ALL       → full table scan (WORST — reads every row in the table)

  ALL on a 1M row table = read 1,000,000 rows every time the query runs!
  ref/range on same table = read ~100-1000 rows via index

Column: key
───────────
  Shows which index was chosen.
  NULL = no index used → query is doing a full table scan!
  "idx_user" = the idx_user index was used.
  Check: is this the best index, or did optimizer pick wrong?

Column: rows
────────────
  Estimated rows MySQL will examine. Lower = better.
  5000 rows examined to return 10 = inefficient.
  10 rows examined to return 10 = perfect.
  Estimate based on statistics — can be wrong! Use ANALYZE TABLE to update stats.

Column: filtered
────────────────
  % of rows that will pass the WHERE condition AFTER index lookup.
  10% filtered = 5000 rows examined × 10% = 500 rows actually returned.
  100% = all rows pass filter (no extra filtering after index).
  Low filtered % = expensive post-index filtering.

Column: Extra (CRITICAL FLAGS)
──────────────────────────────
  "Using index"          → COVERING INDEX! No table access needed. 🟢 BEST
  "Using index condition"→ Index used for WHERE but table access still needed. 🟡 OK
  "Using where"          → WHERE applied after index/scan (post-filter). 🟡 OK
  "Using filesort"       → ORDER BY can't use index — sorts in memory/disk. 🔴 BAD on large sets
  "Using temporary"      → Temp table created for GROUP BY/ORDER BY. 🔴 BAD
  "Using join buffer"    → JOIN without index on joining column. 🔴 BAD

  The worst combination: "Using temporary; Using filesort" on a large table!
*/

-- ============================================
-- MYSQL EXPLAIN FORMAT=JSON (more detail)
-- ============================================

EXPLAIN FORMAT=JSON SELECT * FROM orders WHERE user_id = 42\G
-- Shows:
-- "cost_info": {"query_cost": "502.50"}
-- "rows_examined_per_scan": 5000
-- "access_type": "ref"
-- "used_key_parts": ["user_id"]
-- "filtered": "10.00"

-- ============================================
-- POSTGRESQL EXPLAIN ANALYZE
-- ============================================

EXPLAIN (ANALYZE, BUFFERS, FORMAT TEXT)
SELECT id, amount, status
FROM orders
WHERE user_id = 42
  AND status = 'pending'
ORDER BY created_at DESC
LIMIT 10;

-- Sample output:
-- Limit  (cost=44.72..44.74 rows=10 width=36) (actual time=8.432..8.441 rows=10 loops=1)
--   ->  Sort  (cost=44.72..44.77 rows=20 width=36) (actual time=8.430..8.434 rows=10 loops=1)
--         Sort Key: created_at DESC
--         Sort Method: top-N heapsort  Memory: 26kB
--         ->  Index Scan using idx_user on orders  (cost=0.43..44.30 rows=20 width=36)
--                                                  (actual time=0.061..8.380 rows=200 loops=1)
--               Index Cond: (user_id = 42)
--               Filter: ((status)::text = 'pending'::text)
--               Rows Removed by Filter: 4800
-- Planning Time: 0.3 ms
-- Execution Time: 8.5 ms
-- Buffers: shared hit=215 read=38

-- ============================================
-- POSTGRESQL EXPLAIN COLUMN BREAKDOWN
-- ============================================

/*
Format: NodeType (cost=start..total rows=est width=bytes)
                  (actual time=start..end rows=actual loops=N)

cost=0.43..44.30
  start cost (0.43): cost before first row output (startup)
  total cost (44.30): cost to return ALL rows from this node
  Units: abstract cost units (not milliseconds!)
  Lower total cost = optimizer prefers this plan

rows=20 vs actual rows=200
  rows=20: optimizer ESTIMATED 20 rows
  actual rows=200: query ACTUALLY returned 200 rows
  BIG MISMATCH → statistics are stale → run ANALYZE orders;

actual time=0.061..8.380
  0.061ms: time to return first row
  8.380ms: total time for this node

loops=1
  Node executed 1 time. In nested loop joins: inner node shows loops=N
  actual time is PER LOOP. Total = time × loops.

Node types to watch:
  "Seq Scan"         → Full table scan → add index 🔴
  "Index Scan"       → Using index but still fetches heap rows 🟡
  "Index Only Scan"  → Covering index! No heap access 🟢 BEST
  "Bitmap Heap Scan" → Multiple index ranges combined → can be good 🟡
  "Hash Join"        → Hash-based join (good for large tables)
  "Nested Loop"      → Row-by-row join (good for small result sets)
  "Sort"             → Explicit sort (look for "Sort Method: external merge" = disk sort!) 🔴

Buffers (with BUFFERS option):
  shared hit=215  → pages served from shared_buffers (memory) ← good
  shared read=38  → pages read from disk ← each disk read is slow!
  High shared read → table not in cache → may need work_mem or vacuum

Rows Removed by Filter: 4800
  ← 4800 rows fetched from index but filtered out by `status = 'pending'`
  ← Need index on (user_id, status) to push filter into index!
*/

-- ============================================
-- DIAGNOSIS AND FIX WORKFLOW
-- ============================================

-- STEP 1: Find the slow query
-- MySQL: slow_query_log = ON, long_query_time = 1
-- PgSQL: log_min_duration_statement = 1000  (log queries > 1 second)
-- Both: pg_stat_statements / performance_schema

-- STEP 2: Run EXPLAIN ANALYZE and identify bottleneck
EXPLAIN ANALYZE SELECT id, amount, status
FROM orders WHERE user_id = 42 AND status = 'pending' ORDER BY created_at DESC LIMIT 10;

-- Signs of problem in PgSQL:
-- "Rows Removed by Filter: 4800"  → filter not in index, add to composite index
-- "Sort Method: external merge"   → sort spilling to disk, increase work_mem or add index
-- "Seq Scan on large table"       → missing index entirely
-- "actual rows >> estimated rows" → stale statistics, run ANALYZE table

-- STEP 3: Apply fix

-- Problem: filter on status applied AFTER index lookup (4800 rows wasted)
-- Fix: composite index pushing status into the index:
CREATE INDEX idx_user_status ON orders(user_id, status);

-- After fix:
-- Index Scan using idx_user_status on orders
--   Index Cond: (user_id = 42 AND status = 'pending')
--   Rows Removed by Filter: 0  ← status filter now IN the index!
-- Execution Time: 0.3ms (down from 8.5ms!)

-- Problem: ORDER BY created_at causing sort node
-- Fix: add created_at to index:
DROP INDEX idx_user_status;
CREATE INDEX idx_user_status_created ON orders(user_id, status, created_at DESC);
-- Now ORDER BY created_at DESC already in index → no Sort node!

-- STEP 4: Update statistics if estimates are off
-- MySQL:
ANALYZE TABLE orders;  -- updates index statistics
-- PgSQL:
ANALYZE orders;  -- or runs automatically via autovacuum

-- ============================================
-- MYSQL EXPLAIN FORMAT TIPS
-- ============================================

-- Visual tree format (MySQL 8.0+):
EXPLAIN FORMAT=TREE SELECT * FROM orders WHERE user_id = 42\G
-- More readable, shows actual execution tree

-- See actual execution (MySQL 8.0.18+):
EXPLAIN ANALYZE SELECT * FROM orders WHERE user_id = 42;
-- MySQL added EXPLAIN ANALYZE in 8.0.18!
-- Same as PgSQL — shows actual rows and timing

-- Check all running queries' plans (PgSQL):
SELECT pid, query, state FROM pg_stat_activity WHERE state = 'active';
-- Get plan of running query:
SELECT * FROM pg_stat_plans;  -- requires extension
```

---

## 🔍 Why This Works (3 lines max)
EXPLAIN shows the optimizer's cost-based execution plan before running — use it to check if an index is used and how many rows are estimated. EXPLAIN ANALYZE runs the query and reveals actual rows vs estimates, showing stale statistics or wrong index choices. The most actionable signals are: `type=ALL` (MySQL) / `Seq Scan` (PgSQL) on large tables, `Using filesort`, and large "Rows Removed by Filter" counts.
हिंदी: EXPLAIN plan दिखाता है (estimate), EXPLAIN ANALYZE actual execution दिखाता है। type=ALL और Rows Removed by Filter देखो — यही bottlenecks हैं।

---

## ⚡ Alternative Solution

```sql
-- PgSQL: auto_explain extension (log slow query plans automatically):
-- postgresql.conf:
-- shared_preload_libraries = 'auto_explain'
-- auto_explain.log_min_duration = 1000  (log plans for queries > 1s)
-- auto_explain.log_analyze = true
-- All slow query plans automatically logged — no manual EXPLAIN needed!

-- MySQL: sys schema (MySQL 5.7+) for top slow queries:
SELECT * FROM sys.statements_with_runtimes_in_95th_percentile LIMIT 10;
-- Shows top queries by latency percentile — easy identification of slow queries
```

---

## ⚠️ Common Mistake

```sql
-- ❌ Wrong: Trusting EXPLAIN estimates without ANALYZE
EXPLAIN SELECT * FROM orders WHERE user_id = 42;
-- Shows rows=200 but actual might be 50,000!
-- Always use EXPLAIN ANALYZE in MySQL 8.0+ or PgSQL to see actual rows

-- ❌ Wrong: Running EXPLAIN ANALYZE on a slow UPDATE/DELETE in production
EXPLAIN ANALYZE DELETE FROM orders WHERE status = 'old';
-- EXPLAIN ANALYZE ACTUALLY RUNS the query (wraps in auto-ROLLBACK in PgSQL but still slow!)
-- ✅ Wrap in explicit transaction:
BEGIN;
EXPLAIN ANALYZE DELETE FROM orders WHERE status = 'old';
ROLLBACK;  -- undoes the delete but keeps the plan output

-- ❌ Wrong: Ignoring "loops" in PgSQL output
-- "actual time=0.5..1.2 rows=5 loops=100"
-- Real cost = 1.2ms × 100 loops = 120ms total!
-- Cost shown is PER LOOP — multiply by loops to get actual total cost

-- ❌ Wrong: Adding index based on EXPLAIN without testing actual query time
-- Always: measure query time before index → add index → measure after
-- Use: SELECT NOW(); run_query; SELECT NOW(); to measure elapsed time
-- Or: \timing in psql, or SET profiling=1 in MySQL
```

---

## 🎯 Interview Tip (1 line)
Say: "I look for three things in EXPLAIN: (1) type=ALL or Seq Scan on large tables — missing index; (2) 'Using filesort' or Sort nodes — ORDER BY can't use the index; (3) 'Rows Removed by Filter' in PgSQL or filtered% in MySQL — WHERE condition applied after index lookup, needs composite index. Then I add the right index and verify the improvement with EXPLAIN ANALYZE."

---

## 🔗 Related Questions
→ Q081 (B-Tree internals) | Q084 (covering index) | Q083 (composite index) | Q108 (N+1 problem) | Q109 (slow query optimization)
