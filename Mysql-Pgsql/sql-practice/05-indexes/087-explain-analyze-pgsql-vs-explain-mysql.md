---

# Q087. EXPLAIN ANALYZE (PgSQL) vs EXPLAIN (MySQL)
# Category: Indexes
# Difficulty: ⭐⭐ Medium
# DB: Both (MySQL 8.0.18+ | PostgreSQL)

---

## ❓ Question
What is the difference between plain `EXPLAIN` and `EXPLAIN ANALYZE`? Compare how PostgreSQL and MySQL expose estimated vs actual rows, timing and I/O, and what the danger of `EXPLAIN ANALYZE` is.

---

## 💡 Quick Concept (2 lines only)
`EXPLAIN` shows the optimizer's PLAN with estimates only (query not run). `EXPLAIN ANALYZE` actually EXECUTES the query and adds actual rows, loops and timings, so you can spot bad estimates. MySQL gained it in 8.0.18 (tree format only).
हिंदी: EXPLAIN सिर्फ plan और अनुमान दिखाता है; EXPLAIN ANALYZE query असल में चलाकर actual rows और time दिखाता है।

---

## ✅ Answer / Solution

```sql
-- ============================================
-- SETUP (run this first) - MySQL 8.0.18+
-- ============================================

SET SESSION cte_max_recursion_depth = 100000;

CREATE TABLE orders (
  order_id    BIGINT PRIMARY KEY,
  customer_id INT NOT NULL,
  status      VARCHAR(20) NOT NULL,
  amount      DECIMAL(10,2),
  INDEX idx_customer (customer_id)
);

INSERT INTO orders
SELECT n, 1 + n % 500, ELT(1 + n % 3, 'pending', 'shipped', 'delivered'), n % 1000
FROM (WITH RECURSIVE s AS (SELECT 1 AS n UNION ALL SELECT n + 1 FROM s WHERE n < 20000)
      SELECT n FROM s) x;
ANALYZE TABLE orders;

-- PostgreSQL setup instead:
--   CREATE TABLE orders (order_id BIGINT PRIMARY KEY, customer_id INT NOT NULL, status VARCHAR(20) NOT NULL, amount NUMERIC(10,2));
--   INSERT INTO orders SELECT n, 1+n%500, (ARRAY['pending','shipped','delivered'])[1+n%3], n%1000 FROM generate_series(1,20000) n;
--   CREATE INDEX idx_customer ON orders(customer_id);  ANALYZE orders;

-- ============================================
-- SOLUTION - MySQL
-- ============================================

EXPLAIN SELECT * FROM orders WHERE customer_id = 42 AND status = 'shipped';           -- tabular, estimates
EXPLAIN FORMAT=TREE SELECT * FROM orders WHERE customer_id = 42 AND status = 'shipped';  -- tree, estimates
EXPLAIN ANALYZE SELECT * FROM orders WHERE customer_id = 42 AND status = 'shipped';   -- executes + actuals
EXPLAIN FORMAT=JSON SELECT * FROM orders WHERE customer_id = 42 AND status = 'shipped';  -- costs in JSON

-- ============================================
-- SOLUTION - PostgreSQL
-- ============================================

EXPLAIN SELECT * FROM orders WHERE customer_id = 42 AND status = 'shipped';
EXPLAIN (ANALYZE, BUFFERS) SELECT * FROM orders WHERE customer_id = 42 AND status = 'shipped';

-- ============================================
-- EXPECTED OUTPUT (verified: MySQL 9.1, PostgreSQL 18 via PGlite; timings vary per run)
-- ============================================

-- MySQL EXPLAIN (tabular):
-- id | select_type | table  | type | possible_keys | key          | key_len | ref   | rows | filtered | Extra
-- 1  | SIMPLE      | orders | ref  | idx_customer  | idx_customer | 4       | const | 40   | 10.00    | Using where
--
-- MySQL EXPLAIN ANALYZE:
-- -> Filter: (orders.`status` = 'shipped')  (cost=10.4 rows=4) (actual time=0.0573..0.062 rows=13 loops=1)
--     -> Index lookup on orders using idx_customer (customer_id = 42)  (cost=10.4 rows=40) (actual time=0.0549..0.0578 rows=40 loops=1)
--    Estimated 4 rows after the filter, actually 13 (MySQL assumes filtered=10%); index scan returned 40 as estimated.
--
-- PostgreSQL EXPLAIN (ANALYZE, BUFFERS):
-- Bitmap Heap Scan on orders (cost=4.59..95.93 rows=13 width=24) (actual time=0.063..0.097 rows=13.00 loops=1)
--   Recheck Cond: (customer_id = 42)
--   Filter: ((status)::text = 'shipped'::text)
--   Rows Removed by Filter: 27
--   Heap Blocks: exact=40
--   Buffers: shared hit=40 read=2
--   -> Bitmap Index Scan on idx_customer (cost=0.00..4.59 rows=40 width=0) (actual time=0.043..0.043 rows=40.00 loops=1)
--        Index Cond: (customer_id = 42)
-- Planning Time: 0.048 ms
-- Execution Time: 0.229 ms
-- (PG 18 prints rows=13.00 with decimals and an "Index Searches" line; older versions print rows=13)
```

---

## 🔍 Why This Works (3 lines max)
Comparing `rows=` estimate to `actual rows` exposes stale statistics or skewed data (the usual root cause of a bad plan). PostgreSQL's BUFFERS adds shared hit/read pages (cache vs disk); MySQL's ANALYZE shows per-node actual time and loops but no buffer counts.
हिंदी: Estimated rows और actual rows की तुलना से bad statistics पकड़ में आती हैं; PgSQL BUFFERS से disk/cache reads भी दिखते हैं।

---

## ⚡ Alternative Solution

```sql
-- Safely analyzing writes: ANALYZE really executes INSERT/UPDATE/DELETE!
-- PostgreSQL - wrap in a transaction and roll back (run BEGIN and ROLLBACK as separate statements):
BEGIN;
EXPLAIN ANALYZE DELETE FROM orders WHERE customer_id = 42;
--  Delete on orders (cost=4.60..95.83 rows=0 width=0) (actual time=0.230..0.232 rows=0.00 loops=1)
--    -> Bitmap Heap Scan on orders (actual ... rows=40.00 loops=1) -> Bitmap Index Scan on idx_customer
ROLLBACK;
-- Verified on PGlite: the 40 rows were deleted inside the transaction and ROLLBACK restores them.

-- MySQL 9.1 (verified): EXPLAIN ANALYZE DELETE FROM orders WHERE customer_id=42;
--   prints "-> <not executable by iterator executor>" and deletes NOTHING (40 rows still there), i.e. a
--   single-table DELETE gets no actual timings. EXPLAIN ANALYZE FORMAT=JSON raises ERROR 6412
--   (needs explain_json_format_version=2). So for MySQL write analysis use the slow log / performance_schema.

-- Useful PostgreSQL options: EXPLAIN (ANALYZE, BUFFERS, VERBOSE, SETTINGS, FORMAT JSON)
-- Useful MySQL: EXPLAIN FORMAT=TREE, EXPLAIN FORMAT=JSON, EXPLAIN FOR CONNECTION <id>, optimizer_trace
```

---

## ⚠️ Common Mistake

```sql
-- ❌ Wrong: EXPLAIN ANALYZE on a production DELETE/UPDATE without a transaction
EXPLAIN ANALYZE DELETE FROM orders WHERE status = 'delivered';   -- really deletes the rows!
-- ✅ BEGIN; EXPLAIN ANALYZE ...; ROLLBACK;   (or test on a replica / copy)

-- ❌ Wrong: trusting plain EXPLAIN cost numbers as timings
-- cost is in arbitrary optimizer units, not milliseconds, and the two engines' units are not comparable.
-- ✅ Use ANALYZE for real time; compare estimated vs actual rows first.

-- ❌ Wrong: reading actual time of a node as total - in PgSQL it is PER LOOP; multiply by loops=N
-- (nested loop inner side with loops=10000 can dominate even if each loop is 0.01 ms).
```

---

## 🎯 Interview Tip (1 line)
Say: "I start with EXPLAIN (ANALYZE, BUFFERS) in PostgreSQL or EXPLAIN ANALYZE in MySQL 8, compare estimated to actual rows to find stale stats or skew, remember it executes the statement so I wrap writes in a rolled-back transaction, and I read node times multiplied by loops."

---

## 🔗 Related Questions
→ Q086 (EXPLAIN output) | Q083 (Composite index order) | Q088 (When MySQL does NOT use an index) | Q093 (Index bloat PgSQL)
