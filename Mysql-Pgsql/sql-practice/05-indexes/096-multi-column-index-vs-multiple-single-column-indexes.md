---

# Q096. Multi-Column Index vs Multiple Single-Column Indexes
# Category: Indexes
# Difficulty: ⭐⭐ Medium
# DB: Both (MySQL 8.0+ | PostgreSQL)

---

## ❓ Question
A query filters `customer_id = ? AND status = ?` and sorts by `created_at DESC`. You have three single-column indexes. Is one composite index better? Show how the plan changes in MySQL and PostgreSQL.

---

## 💡 Quick Concept (2 lines only)
MySQL usually uses ONE index per table (or index-merge); PostgreSQL can combine several via BitmapAnd, but neither can use them to give sorted output. One composite `(customer_id, status, created_at)` serves filter + sort in a single B-tree range scan.
हिंदी: कई single indexes filter तो कर लेते हैं पर sort नहीं; एक composite index filter और ORDER BY दोनों एक साथ संभालता है।

---

## ✅ Answer / Solution

```sql
-- ============================================
-- SETUP (MySQL 8.0+/9.x) — verified on MySQL 9.1.0
-- ============================================

CREATE TABLE orders (
  id          INT PRIMARY KEY AUTO_INCREMENT,
  customer_id INT NOT NULL,
  status      VARCHAR(20) NOT NULL,
  created_at  DATETIME NOT NULL,
  amount      DECIMAL(10,2) NOT NULL,
  KEY idx_customer (customer_id),
  KEY idx_status   (status),
  KEY idx_created  (created_at)
);
SET SESSION cte_max_recursion_depth = 50000;
INSERT INTO orders (customer_id, status, created_at, amount)
WITH RECURSIVE n AS (SELECT 1 i UNION ALL SELECT i+1 FROM n WHERE i < 50000)
SELECT i % 200 + 1, ELT((i DIV 7) % 4 + 1, 'delivered','shipped','pending','cancelled'),
       TIMESTAMP('2024-01-01') + INTERVAL i MINUTE, 10 + (i % 90)
FROM n;
ANALYZE TABLE orders;

-- ============================================
-- SOLUTION
-- ============================================

-- Step 1: with only single-column indexes
EXPLAIN SELECT * FROM orders WHERE customer_id = 42 AND status = 'shipped' AND created_at >= '2024-01-01';
EXPLAIN SELECT * FROM orders WHERE customer_id = 42 AND status = 'shipped' ORDER BY created_at DESC LIMIT 5;

-- Step 2: add ONE composite index (equality columns first, range/sort column last)
ALTER TABLE orders ADD KEY idx_cust_status_created (customer_id, status, created_at);
ANALYZE TABLE orders;

-- Step 3: same queries again
EXPLAIN SELECT * FROM orders WHERE customer_id = 42 AND status = 'shipped' AND created_at >= '2024-01-01';
EXPLAIN SELECT * FROM orders WHERE customer_id = 42 AND status = 'shipped' ORDER BY created_at DESC LIMIT 5;

-- ============================================
-- EXPECTED OUTPUT (real MySQL 9.1.0)
-- ============================================

-- Step 1 query A: type=ref, key=idx_customer, rows=250, Extra: Using where
--   (status + created_at filtered row by row AFTER the index lookup)
-- Step 1 query B: type=ref, key=idx_customer, rows=250, Extra: Using where; Using filesort
-- Step 3 query A: type=range, key=idx_cust_status_created, key_len=91, rows=71, Extra: Using index condition
-- Step 3 query B: type=ref, key=idx_cust_status_created, key_len=86 (customer_id+status),
--                 rows=71, Extra: Backward index scan   <- no filesort, LIMIT 5 stops early
-- Leading column missing: WHERE status='shipped' AND created_at>='2024-03-01'
--   -> composite NOT used; optimizer picks idx_created (type=range, rows=1)
```

```sql
-- ============================================
-- POSTGRESQL (verified on PGlite = PostgreSQL 18.6)
-- ============================================
CREATE TABLE orders (id SERIAL PRIMARY KEY, customer_id INT NOT NULL, status TEXT NOT NULL,
                     created_at TIMESTAMP NOT NULL, amount NUMERIC(10,2) NOT NULL);
INSERT INTO orders (customer_id,status,created_at,amount)
SELECT i%200+1, (ARRAY['delivered','shipped','pending','cancelled'])[(i/7)%4+1],
       TIMESTAMP '2024-01-01' + i*INTERVAL '1 minute', 10+(i%90)
FROM generate_series(1,50000) i;
CREATE INDEX idx_customer ON orders(customer_id);
CREATE INDEX idx_status   ON orders(status);
CREATE INDEX idx_created  ON orders(created_at);
ANALYZE orders;

EXPLAIN SELECT * FROM orders WHERE customer_id=42 AND status='shipped' AND created_at>='2024-01-01';
-- Bitmap Heap Scan -> BitmapAnd( Bitmap Index Scan idx_customer, Bitmap Index Scan idx_status ); Filter: created_at
EXPLAIN SELECT * FROM orders WHERE customer_id=42 AND status='shipped' ORDER BY created_at DESC LIMIT 5;
-- Limit -> Index Scan Backward using idx_created ... Filter: (customer_id=42 AND status='shipped')
--   (walks the time index and filters: can be terrible when matches are rare)

CREATE INDEX idx_cust_status_created ON orders(customer_id, status, created_at);
ANALYZE orders;
EXPLAIN SELECT * FROM orders WHERE customer_id=42 AND status='shipped' ORDER BY created_at DESC LIMIT 5;
-- Limit (cost 0.41..19.54) -> Index Scan Backward using idx_cust_status_created
--   Index Cond: (customer_id = 42 AND status = 'shipped')    <- cost fell ~8x vs 157.71
```

---

## 🔍 Why This Works (3 lines max)
A B-tree on (a,b,c) is sorted by a, then b within a, then c within b - equality on a and b leaves rows already ordered by c, so ORDER BY needs no sort and LIMIT stops early. Separate indexes each answer one predicate, so rows must be intersected (PG) or re-filtered (MySQL).
हिंदी: Composite index में rows (a,b,c) क्रम में sorted रहते हैं, इसलिए filter के बाद sort की ज़रूरत नहीं पड़ती।

---

## ⚡ Alternative Solution

```sql
-- Index merge / bitmap does exist, but it is a fallback, not a design:
-- MySQL: type=index_merge "Using intersect(idx_a,idx_b)" (see Q105)
-- PostgreSQL: BitmapAnd (shown above)

-- PostgreSQL 11+: keep the index narrow, INCLUDE extra columns for index-only scans
CREATE INDEX idx_cust_status_created_inc ON orders (customer_id, status, created_at) INCLUDE (amount);
-- MySQL has no INCLUDE; add the column to the key (wider) to make it covering.
```

---

## ⚠️ Common Mistake

```sql
-- ❌ "Index every column that appears in WHERE" -> 3 single indexes, slow writes, still a filesort
-- ❌ Wrong order: (created_at, customer_id, status) -> customer_id/status equality can't narrow the range
-- ✅ Equality columns first, then range/ORDER BY column; most selective-first is a myth when ranges exist.
-- ❌ Expecting (customer_id, status, created_at) to help WHERE status='shipped' alone (leftmost prefix rule)
-- Verified: such a query still used idx_created / idx_status, not the composite.
```

---

## 🎯 Interview Tip (1 line)
Say: "I design indexes from the query: equality columns, then the range or ORDER BY column last; one composite replaces several singles and removes the filesort, while every extra index taxes writes and the buffer pool."

---

## 🔗 Related Questions
→ Q083 (Composite index column order) | Q084 (Covering index) | Q103 (Using filesort) | Q105 (Index merge)
