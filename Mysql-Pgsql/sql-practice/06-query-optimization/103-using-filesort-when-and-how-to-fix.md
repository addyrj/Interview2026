---

# Q103. Using filesort — When + How to Fix
# Category: Query Optimization
# Difficulty: ⭐⭐ Medium
# DB: Both (MySQL 8.0+ | PostgreSQL)

---

## ❓ Question
EXPLAIN shows `Using filesort` on `WHERE customer_id = ? ORDER BY created_at DESC LIMIT 10`. What does it mean, when is it acceptable, and how do you remove it? What is the PostgreSQL equivalent?

---

## 💡 Quick Concept (2 lines only)
"filesort" means MySQL sorts rows in memory/disk because no index delivers them in ORDER BY order (despite the name, not necessarily a file). Fix with an index whose key order is (equality columns, then ORDER BY columns); PostgreSQL shows an explicit `Sort` node (top-N heapsort, quicksort, or external merge on disk).
हिंदी: ORDER BY के क्रम में index न हो तो engine को अलग से sort करना पड़ता है; (filter column, sort column) का composite index इसे हटा देता है।

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
  created_at  DATETIME NOT NULL,
  KEY idx_customer (customer_id)
);
SET SESSION cte_max_recursion_depth = 100000;
INSERT INTO orders (customer_id, status, amount, created_at)
WITH RECURSIVE n AS (SELECT 1 i UNION ALL SELECT i+1 FROM n WHERE i < 100000)
SELECT i % 500 + 1, ELT(i % 4 + 1, 'delivered','shipped','pending','cancelled'),
       10 + (i % 490), TIMESTAMP('2024-01-01') + INTERVAL i MINUTE FROM n;
ANALYZE TABLE orders;

-- ============================================
-- SOLUTION
-- ============================================

-- Step 1: filter uses idx_customer, but ORDER BY created_at needs a sort
EXPLAIN SELECT * FROM orders WHERE customer_id = 42 ORDER BY created_at DESC LIMIT 10;
EXPLAIN ANALYZE SELECT * FROM orders WHERE customer_id = 42 ORDER BY created_at DESC LIMIT 10;

-- Step 2: sorting the whole table (nothing to filter on) - unavoidable without an index on amount
EXPLAIN SELECT * FROM orders ORDER BY amount DESC LIMIT 10;

-- Step 3: the fix - composite index (equality column, then sort column)
ALTER TABLE orders ADD KEY idx_cust_created (customer_id, created_at);
ANALYZE TABLE orders;
EXPLAIN SELECT * FROM orders WHERE customer_id = 42 ORDER BY created_at DESC LIMIT 10;
EXPLAIN ANALYZE SELECT * FROM orders WHERE customer_id = 42 ORDER BY created_at DESC LIMIT 10;

-- Step 4: cases that bring the filesort back
EXPLAIN SELECT * FROM orders WHERE customer_id = 42 ORDER BY created_at DESC, amount ASC LIMIT 10;  -- mixed order
EXPLAIN SELECT * FROM orders WHERE customer_id > 490 ORDER BY created_at DESC LIMIT 10;              -- range on 1st col

-- ============================================
-- EXPECTED OUTPUT (real, MySQL 9.1.0)
-- ============================================
-- Step 1: type=ref, key=idx_customer, rows=200, Extra: Using filesort
--   ANALYZE: Limit 10 -> Sort: created_at DESC, limit input to 10 row(s) per chunk
--            (actual time 0.303 ms) -> Index lookup rows=200 (all 200 rows fetched, then sorted)
-- Step 2: type=ALL, rows=99900, Extra: Using filesort   (top-10 heap sort over 100k rows)
-- Step 3: type=ref, key=idx_cust_created, rows=200, Extra: Backward index scan   <- filesort gone
--   ANALYZE: Limit 10 -> Index lookup ... (reverse) actual time 0.0588..0.0602 rows=10 (reads only 10 rows)
-- Step 4a: key=idx_customer, Extra: Using filesort   (DESC + ASC mix not satisfied by an ASC,ASC index)
-- Step 4b: type=range, key=idx_customer, Extra: Using index condition; Using filesort
```

```sql
-- ============================================
-- POSTGRESQL (verified on PGlite = PostgreSQL 18.6)
-- ============================================
-- Same orders table via generate_series, index idx_customer(customer_id):
EXPLAIN (ANALYZE, COSTS OFF, TIMING OFF) SELECT * FROM orders WHERE customer_id=42 ORDER BY created_at DESC LIMIT 10;
-- Limit -> Sort (Sort Key: created_at DESC; Sort Method: top-N heapsort Memory: 18kB)
--          -> Bitmap Heap Scan (rows=200) -> Bitmap Index Scan on idx_customer
CREATE INDEX idx_cust_created ON orders(customer_id, created_at);  ANALYZE orders;
-- -> Limit -> Index Scan Backward using idx_cust_created (actual rows=10)    no Sort node

EXPLAIN (COSTS OFF) SELECT * FROM orders WHERE customer_id=42 ORDER BY created_at DESC, amount ASC LIMIT 10;
-- Limit -> Incremental Sort (Presorted Key: created_at) -> Index Scan Backward   <- PG sorts only small groups

SET work_mem = '64kB';
EXPLAIN (ANALYZE, COSTS OFF, TIMING OFF) SELECT * FROM orders ORDER BY amount DESC, id;
-- Sort Method: external merge  Disk: 4184kB     <- when the sort doesn't fit in work_mem it spills to disk
```

---

## 🔍 Why This Works (3 lines max)
B-tree entries are already ordered by (customer_id, created_at), so after seeking customer 42 the engine just walks the index backward and stops after LIMIT rows. Without it, every matching row is read, sorted in a buffer (spilling to disk if too large), then trimmed.
हिंदी: Index पहले से sorted होता है, इसलिए उसे पीछे से पढ़कर LIMIT पर रुक जाओ; sort की ज़रूरत ही नहीं पड़ती।

---

## ⚡ Alternative Solution

```sql
-- MySQL 8.0+: descending / mixed-direction index to satisfy ORDER BY a DESC, b ASC
ALTER TABLE orders ADD KEY idx_cust_created_amt (customer_id, created_at DESC, amount ASC);   -- not run
-- Sort memory knobs: MySQL sort_buffer_size (per session!) | PostgreSQL work_mem
-- Check how often sorts spill:  MySQL  SHOW GLOBAL STATUS LIKE 'Sort_merge_passes';
-- PostgreSQL 13+: Incremental Sort is automatic when a prefix of the sort key is already indexed (shown above).
```

---

## ⚠️ Common Mistake

```sql
-- ❌ Panicking at every "Using filesort": on 200 rows it costs 0.3 ms - fine
-- ❌ Index on (created_at, customer_id) for this query: sort column first can't seek customer_id
-- ❌ Big sort_buffer_size / work_mem globally "to be safe" -> memory x connections = OOM
-- ✅ Equality columns first, ORDER BY columns next, matching direction; keep LIMIT so the scan can stop early.
```

---

## 🎯 Interview Tip (1 line)
Say: "Filesort is a cost, not an error - I care when it sorts many rows or spills to disk; the fix is an index on (equality columns, ORDER BY columns) so the engine reads in order and stops at LIMIT."

---

## 🔗 Related Questions
→ Q083 (Composite index order) | Q104 (Using temporary) | Q107 (Pagination) | Q096 (Multi-column index)
