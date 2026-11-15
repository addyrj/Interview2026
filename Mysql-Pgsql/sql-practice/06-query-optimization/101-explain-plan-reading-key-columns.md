---

# Q101. EXPLAIN Plan Reading — Key Columns
# Category: Query Optimization
# Difficulty: ⭐⭐ Medium
# DB: Both (MySQL 8.0+ | PostgreSQL)

---

## ❓ Question
You get an EXPLAIN for a two-table join. Which columns/nodes do you read first to decide if the plan is healthy, in MySQL and in PostgreSQL?

---

## 💡 Quick Concept (2 lines only)
MySQL tabular EXPLAIN: look at `type` (ALL = bad, ref/range/const = good), `key`, `rows`, `filtered`, `Extra`. PostgreSQL EXPLAIN (ANALYZE): look at node types (Seq/Index/Bitmap scan, join method), estimated vs actual rows, "Rows Removed by Filter", and buffers.
हिंदी: MySQL में type/key/rows/Extra देखो; PostgreSQL में scan/join node, estimated बनाम actual rows और buffers देखो।

---

## ✅ Answer / Solution

```sql
-- ============================================
-- SETUP — MySQL (verified on MySQL 9.1.0)
-- ============================================

CREATE TABLE customers (
  id   INT PRIMARY KEY AUTO_INCREMENT,
  name VARCHAR(60) NOT NULL,
  city VARCHAR(30) NOT NULL,
  KEY idx_city (city)
);
CREATE TABLE orders (
  id          INT PRIMARY KEY AUTO_INCREMENT,
  customer_id INT NOT NULL,
  status      VARCHAR(20) NOT NULL,
  amount      DECIMAL(10,2) NOT NULL,
  created_at  DATETIME NOT NULL,
  KEY idx_customer (customer_id)
);
SET SESSION cte_max_recursion_depth = 50000;
INSERT INTO customers (name, city)
WITH RECURSIVE n AS (SELECT 1 i UNION ALL SELECT i+1 FROM n WHERE i < 2000)
SELECT CONCAT('Customer ', i), ELT(i % 5 + 1, 'Pune','Delhi','Mumbai','Bengaluru','Chennai') FROM n;
INSERT INTO orders (customer_id, status, amount, created_at)
WITH RECURSIVE n AS (SELECT 1 i UNION ALL SELECT i+1 FROM n WHERE i < 50000)
SELECT i % 2000 + 1, ELT(i % 4 + 1, 'delivered','shipped','pending','cancelled'),
       10 + (i % 490), TIMESTAMP('2024-01-01') + INTERVAL i MINUTE FROM n;
ANALYZE TABLE customers, orders;

-- ============================================
-- SOLUTION
-- ============================================

-- Step 1: tabular plan
EXPLAIN SELECT c.name, o.amount
FROM customers c JOIN orders o ON o.customer_id = c.id
WHERE c.city = 'Pune' AND o.status = 'shipped';

-- Step 2: tree plan (shows join order + filters) and Step 3: real timings
EXPLAIN FORMAT=TREE SELECT c.name, o.amount
FROM customers c JOIN orders o ON o.customer_id = c.id WHERE c.city = 'Pune' AND o.status = 'shipped';
EXPLAIN ANALYZE SELECT c.name, o.amount
FROM customers c JOIN orders o ON o.customer_id = c.id WHERE c.city = 'Pune' AND o.status = 'shipped';

-- ============================================
-- EXPECTED OUTPUT (real, MySQL 9.1.0)
-- ============================================
-- Step 1:
-- id | table | type | possible_keys    | key          | key_len | ref       | rows | filtered | Extra
-- 1  | c     | ref  | PRIMARY,idx_city | idx_city     | 122     | const     | 400  | 100.00   | NULL
-- 1  | o     | ref  | idx_customer     | idx_customer | 4       | d101.c.id | 25   | 10.00    | Using where
--   Read top to bottom = join order: customers (driving) -> orders (nested loop, 400 index lookups)
--   key_len 122 = VARCHAR(30) utf8mb4 (30*4+2); filtered 10% = guess for status='shipped'
-- Step 3 (EXPLAIN ANALYZE):
-- -> Nested loop inner join (cost=3587 rows=1012) (actual time=0.115..8.22 rows=2500 loops=1)
--    -> Index lookup on c using idx_city (city='Pune') (rows=400) (actual rows=400 loops=1)
--    -> Filter: (o.status='shipped') (rows=2.53) (actual rows=6.25 loops=400)
--       -> Index lookup on o using idx_customer (customer_id=c.id) (rows=25.3) (actual rows=25 loops=400)
-- Optimizer estimated 1012 result rows, reality was 2500 -> filtered guess was off by ~2.5x.
```

```sql
-- ============================================
-- POSTGRESQL (verified on PGlite = PostgreSQL 18.6)
-- ============================================
-- same tables created with SERIAL / TEXT / generate_series, then:
EXPLAIN (ANALYZE, BUFFERS, TIMING OFF)
SELECT c.name, o.amount FROM customers c JOIN orders o ON o.customer_id = c.id
WHERE c.city = 'Pune' AND o.status = 'shipped';
-- Hash Join (cost=31.38..1056.70 rows=2458) (actual rows=2500.00 loops=1)
--   Hash Cond: (o.customer_id = c.id)
--   -> Seq Scan on orders o (rows=12288) (actual rows=12500.00)   Rows Removed by Filter: 37500
--   -> Hash  (Buckets: 1024  Batches: 1  Memory Usage: 22kB)
--       -> Bitmap Heap Scan on customers c -> Bitmap Index Scan on idx_city (actual rows=400)
-- Buffers: shared hit=384      Execution Time: ~6 ms (machine dependent)
-- PostgreSQL chose Hash Join + Seq Scan on orders (25% of rows match status) - a different, equally valid plan.
```

---

## 🔍 Why This Works (3 lines max)
Plans are trees: the driving table and join order come first, and the biggest red flags are full scans on large tables, huge `rows` multipliers, and estimates far from actuals. `ANALYZE` variants execute the query so you compare estimated vs actual rows - the root cause of most bad plans.
हिंदी: Plan एक tree है; बड़े table पर full scan और estimate-बनाम-actual rows का बड़ा अंतर ही असली लाल झंडे हैं।

---

## ⚡ Alternative Solution

```sql
-- MySQL: JSON plan with costs
EXPLAIN FORMAT=JSON SELECT ...;                 -- query_cost, used_key_parts, attached_condition
-- MySQL: why were other indexes rejected / which join order?
SET optimizer_trace='enabled=on'; SELECT ...; SELECT * FROM information_schema.optimizer_trace\G
-- PostgreSQL: machine-readable + buffers + settings that differ from default
EXPLAIN (ANALYZE, BUFFERS, SETTINGS, FORMAT JSON) SELECT ...;
-- Caution: EXPLAIN ANALYZE really executes - wrap DML in BEGIN; ... ROLLBACK;
```

---

## ⚠️ Common Mistake

```sql
-- ❌ Judging by cost numbers across different queries, or reading only "key is not NULL"
-- ❌ Ignoring Extra: "Using filesort", "Using temporary" (MySQL) / "Rows Removed by Filter" (PG)
-- ❌ Running EXPLAIN on tiny/dev data: optimizer picks different plans (this demo: 50k rows)
-- ✅ Use production-like row counts, compare rows vs actual rows, and re-run ANALYZE TABLE / ANALYZE first.
```

---

## 🎯 Interview Tip (1 line)
Say: "I read the plan top-down for join order, check type/key and rows multipliers, then use EXPLAIN ANALYZE to compare estimates with actuals - a 10x misestimate means stale or missing statistics, not just a missing index."

---

## 🔗 Related Questions
→ Q086 (EXPLAIN output) | Q087 (EXPLAIN ANALYZE PgSQL vs MySQL) | Q102 (Full table scan) | Q114 (Statistics / ANALYZE)
