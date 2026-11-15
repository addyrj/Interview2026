---

# Q229. How Would You Optimize a Slow Query?
# Category: Interview Classics
# Difficulty: ⭐⭐⭐ Hard
# DB: Both (MySQL 8.0+ | PostgreSQL)

---

## ❓ Question
A query on a 100,000-row `orders` table is slow. Walk through your method: how you measure it, read the plan, and fix it. Show a before/after with EXPLAIN, including the "function on indexed column" trap.

---

## 💡 Quick Concept (2 lines only)
Never guess: measure (slow log / pg_stat_statements), read EXPLAIN ANALYZE, then fix the biggest cost — missing or wrong index, non-sargable predicate, too many rows/columns, or a bad join. Re-measure after each change.
हिंदी: पहले measure करो, फिर EXPLAIN ANALYZE पढ़ो, फिर index/predicate ठीक करो, और बदलाव के बाद दोबारा measure करो।

---

## ✅ Answer / Solution

```sql
-- ============================================
-- SETUP — MySQL 9.1 (needs 8.0+ for recursive CTE)
-- ============================================

CREATE TABLE orders (
  id          INT AUTO_INCREMENT PRIMARY KEY,
  customer_id INT NOT NULL,
  status      VARCHAR(20) NOT NULL,
  amount      DECIMAL(10,2) NOT NULL,
  created_at  DATETIME NOT NULL,
  notes       VARCHAR(200)
) ENGINE=InnoDB;

SET SESSION cte_max_recursion_depth = 100000;

INSERT INTO orders (customer_id, status, amount, created_at, notes)
WITH RECURSIVE seq AS (SELECT 1 AS n UNION ALL SELECT n+1 FROM seq WHERE n < 100000)
SELECT (n * 7919) % 5000 + 1,                                   -- ~5000 customers
       ELT((n * 31) % 7 % 4 + 1, 'completed','pending','cancelled','refunded'),
       ROUND(10 + (n % 997) * 0.5, 2),
       TIMESTAMP('2024-01-01') + INTERVAL (n % 365) DAY + INTERVAL (n % 86400) SECOND,
       CONCAT('note-', n)
FROM seq;

ANALYZE TABLE orders;     -- refresh statistics so the optimizer sees real row counts

-- Data check: 100,000 rows; customer 42 has 5 'completed' orders.

-- ============================================
-- SOLUTION — the workflow
-- ============================================

-- Step 1: reproduce + look at the plan of the slow query
EXPLAIN ANALYZE
SELECT * FROM orders
WHERE customer_id = 42 AND status = 'completed'
ORDER BY created_at DESC LIMIT 10;

-- BEFORE (MySQL 9.1):
-- -> Limit: 10 row(s)           (actual time=24.3..24.3 rows=5)
--    -> Sort: created_at DESC, limit input to 10 row(s) per chunk
--       -> Filter: (status='completed' and customer_id=42)
--          -> Table scan on orders  (rows=100000 read to return 5)     <- full scan + filesort
-- (plain EXPLAIN shows type=ALL, key=NULL, rows~99750, Extra: Using where; Using filesort)

-- Step 2: composite index = equality columns first, then the ORDER BY column
CREATE INDEX idx_cust_status_created ON orders (customer_id, status, created_at);

EXPLAIN ANALYZE
SELECT * FROM orders
WHERE customer_id = 42 AND status = 'completed'
ORDER BY created_at DESC LIMIT 10;

-- AFTER:
-- -> Limit: 10 row(s)           (actual time=0.015..0.026 rows=5)
--    -> Index lookup on orders using idx_cust_status_created
--       (customer_id = 42, status = 'completed') (reverse)          <- no scan, no sort
-- ~24 ms -> ~0.03 ms (timings vary per machine; the shape of the plan is what matters).

-- Step 3: the non-sargable trap — a function on the indexed column
CREATE INDEX idx_created ON orders (created_at);

EXPLAIN FORMAT=TREE SELECT id FROM orders WHERE DATE(created_at) = '2024-03-15';
-- -> Filter: (cast(orders.created_at as date) = '2024-03-15')
--    -> Covering index scan on orders using idx_created  (rows=99750)     <- scans the WHOLE index

EXPLAIN FORMAT=TREE SELECT id FROM orders
WHERE created_at >= '2024-03-15' AND created_at < '2024-03-16';          -- sargable rewrite
-- -> Covering index range scan on orders using idx_created
--    over ('2024-03-15 00:00:00' <= created_at < '2024-03-16 00:00:00')  (rows=274)

-- Step 4: leading wildcard cannot use a B-Tree
EXPLAIN FORMAT=TREE SELECT id FROM orders WHERE notes LIKE '%note-77%';
-- -> Table scan on orders  (rows=99750)    -> use FULLTEXT / pg_trgm for contains-search

-- ============================================
-- POSTGRESQL (verified on PGlite, same data via generate_series)
-- ============================================

EXPLAIN (ANALYZE, COSTS OFF, TIMING OFF)
SELECT * FROM orders WHERE customer_id = 42 AND status = 'completed'
ORDER BY created_at DESC LIMIT 10;
-- BEFORE: Seq Scan on orders, Rows Removed by Filter: 99995, Buffers: shared hit=962, Execution ~8 ms
CREATE INDEX idx_cust_status_created ON orders (customer_id, status, created_at);
-- AFTER:  Bitmap Index Scan on idx_cust_status_created -> Bitmap Heap Scan, Buffers: hit=5 read=3,
--         Execution ~0.06 ms   (a small Sort remains; it sorts only the 5 matching rows)

EXPLAIN (COSTS OFF) SELECT id FROM orders WHERE created_at::date = '2024-03-15';
-- Seq Scan on orders  (Filter: (created_at)::date = ...)    <- index idx_created NOT used
EXPLAIN (COSTS OFF) SELECT id FROM orders
WHERE created_at >= '2024-03-15' AND created_at < '2024-03-16';
-- Bitmap Index Scan on idx_created                          <- sargable range uses the index
-- PG alternative: expression index  CREATE INDEX ON orders ((created_at::date));
```

---

## 🔍 Why This Works (3 lines max)
The B-Tree index on (customer_id, status, created_at) jumps straight to the matching range and returns rows already sorted, so there is no scan and no filesort. Wrapping the column in a function hides it from the index, so the predicate must be rewritten as a range on the raw column.
हिंदी: Index सीधे matching rows तक पहुँचाता है और sort भी बचाता है; column पर function लगाने से index बेकार हो जाता है।

---

## ⚡ Alternative Solution

```sql
-- Other levers once the plan is sane:
-- 1) Covering index: put selected columns in the index to avoid table lookups
CREATE INDEX idx_cover ON orders (customer_id, status, created_at, amount);
-- 2) Select only needed columns instead of SELECT *
-- 3) Keyset pagination instead of OFFSET 100000 (see Q012)
-- 4) Rewrite correlated subquery / IN to JOIN or EXISTS; fix N+1 (Q228)
-- 5) Pre-aggregate heavy reports into a summary table / materialized view (PostgreSQL)
-- 6) Update stats:  MySQL ANALYZE TABLE t;   PostgreSQL ANALYZE t;
-- 7) PostgreSQL: CREATE INDEX CONCURRENTLY on live tables (see Q224)

-- Find slow queries first:
--   MySQL:      slow_query_log=ON, long_query_time=0.5, then pt-query-digest / performance_schema digests
--   PostgreSQL: pg_stat_statements (ORDER BY total_exec_time DESC) + auto_explain
--   (slow-log and pg_stat_statements were NOT run here)
```

---

## ⚠️ Common Mistake

```sql
-- ❌ Wrong: index column order (status, customer_id, created_at) for the query above
--    leftmost-prefix rule: low-selectivity first works but is less reusable; put equality
--    columns that you filter on most often/most selective first, range/sort column last.
-- ❌ Wrong: WHERE DATE(created_at) = '2024-03-15'   (function on column)
-- ❌ Wrong: adding an index for every slow query -> slower INSERT/UPDATE, more memory
-- ❌ Wrong: optimizing on an empty dev table; plans change with real data volume and fresh statistics
-- ✅ Correct: measure -> EXPLAIN ANALYZE -> targeted index/rewrite -> re-measure
```

---

## 🎯 Interview Tip (1 line)
Say: "I start from evidence — slow log or pg_stat_statements — then EXPLAIN ANALYZE to compare estimated vs actual rows, fix sargability and composite index order (equality, then range/sort), prefer fewer columns and keyset pagination, and re-verify, while weighing the write-cost of every new index."

---

## 🔗 Related Questions
→ Q223 (B-Tree index) | Q224 (adding index to running table) | Q228 (N+1) | Q012 (keyset pagination)
