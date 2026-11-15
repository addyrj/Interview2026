---

# Q102. Full Table Scan — When + How to Fix
# Category: Query Optimization
# Difficulty: ⭐⭐ Medium
# DB: Both (MySQL 8.0+ | PostgreSQL)

---

## ❓ Question
EXPLAIN shows `type=ALL` (MySQL) or `Seq Scan` (PostgreSQL). When is a full table scan fine, when is it a problem, and what are the standard fixes?

---

## 💡 Quick Concept (2 lines only)
A full scan reads every row; it is optimal for tiny tables or when the query needs most rows, and a bug when a selective predicate has no usable index (or the index is defeated by a function, type mismatch, or low selectivity). Fix: index the predicate, make it sargable, or restrict the data read.
हिंदी: Full scan तब ठीक है जब ज़्यादातर rows चाहिए हों; selective query पर यह bug है - index लगाओ या predicate को sargable बनाओ।

---

## ✅ Answer / Solution

```sql
-- ============================================
-- SETUP — MySQL (verified on MySQL 9.1.0)
-- ============================================

CREATE TABLE orders (
  id          INT PRIMARY KEY AUTO_INCREMENT,
  customer_id INT NOT NULL,
  status      VARCHAR(20) NOT NULL,
  amount      DECIMAL(10,2) NOT NULL,
  created_at  DATETIME NOT NULL
);
SET SESSION cte_max_recursion_depth = 100000;
INSERT INTO orders (customer_id, status, amount, created_at)
WITH RECURSIVE n AS (SELECT 1 i UNION ALL SELECT i+1 FROM n WHERE i < 100000)
SELECT i % 5000 + 1, ELT(i % 4 + 1, 'delivered','shipped','pending','cancelled'),
       10 + (i % 490), TIMESTAMP('2024-01-01') + INTERVAL i MINUTE FROM n;
ANALYZE TABLE orders;

-- ============================================
-- SOLUTION
-- ============================================

-- Step 1: selective predicate, no index -> scan everything for 20 rows
EXPLAIN ANALYZE SELECT * FROM orders WHERE customer_id = 1234;

-- Step 2: add the index
ALTER TABLE orders ADD KEY idx_customer (customer_id);
ANALYZE TABLE orders;
EXPLAIN ANALYZE SELECT * FROM orders WHERE customer_id = 1234;

-- Step 3: cases where an index EXISTS but the scan remains
ALTER TABLE orders ADD KEY idx_status (status), ADD KEY idx_created (created_at);
ANALYZE TABLE orders;
EXPLAIN SELECT * FROM orders WHERE customer_id + 0 = 1234;               -- (a) expression on column
EXPLAIN SELECT * FROM orders WHERE status <> 'delivered';                -- (b) matches most rows
EXPLAIN SELECT * FROM orders WHERE status = 0;                           -- (c) implicit type conversion
EXPLAIN SELECT * FROM orders WHERE DATE(created_at) = '2024-03-01';      -- (d) function on column
-- Fix for (d): range predicate
EXPLAIN SELECT * FROM orders WHERE created_at >= '2024-03-01' AND created_at < '2024-03-02';

-- ============================================
-- EXPECTED OUTPUT (real, MySQL 9.1.0)
-- ============================================
-- Step 1: Filter (customer_id=1234) -> Table scan on orders rows=100000 (actual ~16.6 ms)  returned 20 rows
-- Step 2: Index lookup on orders using idx_customer (customer_id=1234) rows=20 (actual ~0.03 ms)
-- Step 3a: type=ALL, key=NULL, rows=99900, Extra: Using where
-- Step 3b: type=ALL, possible_keys=idx_status, key=NULL, rows=99900, filtered=98.41
-- Step 3c: type=ALL, possible_keys=idx_status, key=NULL (string column compared to number)
-- Step 3d: type=ALL, key=NULL, rows=99900
-- Fix(d) : type=range, key=idx_created, rows=1440, Extra: Using index condition
```

```sql
-- ============================================
-- POSTGRESQL (verified on PGlite = PostgreSQL 18.6)
-- ============================================
CREATE TABLE orders (id SERIAL PRIMARY KEY, customer_id INT NOT NULL, status TEXT NOT NULL,
                     amount NUMERIC(10,2) NOT NULL, created_at TIMESTAMP NOT NULL);
INSERT INTO orders (customer_id,status,amount,created_at)
SELECT i%5000+1, (ARRAY['delivered','shipped','pending','cancelled'])[i%4+1], 10+(i%490),
       TIMESTAMP '2024-01-01'+i*INTERVAL '1 minute' FROM generate_series(1,100000) i;
ANALYZE orders;
EXPLAIN (ANALYZE, COSTS OFF, TIMING OFF) SELECT * FROM orders WHERE customer_id = 1234;
-- Seq Scan  Filter: (customer_id = 1234)  Rows Removed by Filter: 99980  Buffers: shared hit=736
CREATE INDEX idx_customer ON orders(customer_id);  ANALYZE orders;
-- -> Bitmap Heap Scan + Bitmap Index Scan on idx_customer, actual rows=20, Heap Blocks: exact=20

EXPLAIN SELECT * FROM orders WHERE created_at::date = '2024-03-01';   -- Seq Scan (cast on column)
CREATE INDEX idx_created_date ON orders ((created_at::date));          -- PG fix: expression index
-- -> Index Scan using idx_created_date          (or use the range predicate with idx_created)
EXPLAIN SELECT * FROM orders WHERE customer_id <> 1234;               -- Seq Scan (99,980 of 100,000 rows)
-- WHERE customer_id::text = '1234' (cast on the column) -> Seq Scan; even with enable_seqscan=off the plan
--   stays a Seq Scan marked "Disabled: true", because no index can serve it. (PostgreSQL errors on int = 'text' columns
--   with a mismatched literal type instead of silently converting every row - not run here.)
```

---

## 🔍 Why This Works (3 lines max)
A lookup via B-tree costs O(log n) + matching rows, a scan costs O(n); the optimizer picks the scan only if it estimates a large fraction of rows or finds no usable access path. Making the predicate sargable (column alone on one side, comparable type on the other) is what re-enables the index.
हिंदी: Sargable predicate (column अकेला, function/cast के बिना) ही index को use होने देता है।

---

## ⚡ Alternative Solution

```sql
-- When most rows ARE needed (reports): leave the scan, make it cheaper
-- - select only needed columns (covering index scan), partition by date, summary tables, parallel scan (PG).
-- MySQL functional index (8.0.13+) so DATE(created_at) is sargable without rewriting the query:
ALTER TABLE orders ADD KEY idx_created_date ((DATE(created_at)));    -- not run in this verification
-- PostgreSQL partial index for a hot subset:
CREATE INDEX idx_pending ON orders (created_at) WHERE status = 'pending';
```

---

## ⚠️ Common Mistake

```sql
-- ❌ Adding an index and assuming it's used
SELECT * FROM orders WHERE DATE(created_at) = '2024-03-01';   -- scan, index ignored
-- ❌ Comparing string column to number: WHERE status = 0   (MySQL converts every row)
-- ❌ Forcing an index for a predicate that matches 98% of rows: slower than the scan
-- ✅ Rewrite as range, match types, or create functional/expression index.
```

---

## 🎯 Interview Tip (1 line)
Say: "A scan isn't automatically wrong - I check selectivity and table size first; if it's a selective predicate I make it sargable or add the right composite index, and verify with EXPLAIN ANALYZE rows-examined versus rows-returned."

---

## 🔗 Related Questions
→ Q088 (When MySQL doesn't use an index) | Q119 (Function on indexed column) | Q101 (EXPLAIN key columns) | Q083 (Composite index order)
