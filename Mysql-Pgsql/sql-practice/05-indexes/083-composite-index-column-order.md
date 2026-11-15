---

# Q083. Composite Index - Does Column Order Matter?
# Category: Indexes
# Difficulty: ⭐⭐ Medium
# DB: Both (MySQL 8.0+ | PostgreSQL)

---

## ❓ Question
You have an index on `(customer_id, status, order_date)`. Which of these queries can use it, how much of it, and how should you choose the column order for a new composite index?

---

## 💡 Quick Concept (2 lines only)
A composite B-Tree is sorted by the first column, then the second within it, and so on, so it is usable only through a leftmost prefix; the first range condition stops further columns from narrowing the seek. Rule of thumb: equality columns first, then range/sort column last.
हिंदी: Composite index leftmost-prefix से चलता है; equality columns पहले, range/sort column आख़िर में रखो।

---

## ✅ Answer / Solution

```sql
-- ============================================
-- SETUP (run this first) - MySQL 8.0+
-- ============================================

SET SESSION cte_max_recursion_depth = 100000;

CREATE TABLE orders (
  order_id    BIGINT PRIMARY KEY,
  customer_id INT NOT NULL,
  status      VARCHAR(20) NOT NULL,
  order_date  DATE NOT NULL,
  amount      DECIMAL(10,2),
  INDEX idx_cust_status_date (customer_id, status, order_date)
);

INSERT INTO orders
SELECT n, 1 + n % 500,
       ELT(1 + n % 3, 'pending', 'shipped', 'delivered'),
       DATE_ADD('2024-01-01', INTERVAL n % 365 DAY), n % 1000
FROM (WITH RECURSIVE s AS (SELECT 1 AS n UNION ALL SELECT n + 1 FROM s WHERE n < 20000)
      SELECT n FROM s) x;

ANALYZE TABLE orders;

-- PostgreSQL setup instead: same table, then
--   INSERT INTO orders SELECT n, 1+n%500, (ARRAY['pending','shipped','delivered'])[1+n%3],
--          DATE '2024-01-01' + (n % 365), n % 1000 FROM generate_series(1,20000) n;
--   CREATE INDEX idx_cust_status_date ON orders (customer_id, status, order_date);  ANALYZE orders;

-- ============================================
-- SOLUTION: try each predicate with EXPLAIN
-- ============================================

-- Q1: all three columns (equality, equality, range)         -> full index used
EXPLAIN SELECT * FROM orders WHERE customer_id = 42 AND status = 'shipped' AND order_date >= '2024-06-01';
-- Q2: leftmost column only                                  -> prefix used
EXPLAIN SELECT * FROM orders WHERE customer_id = 42;
-- Q3: skips the middle column                               -> only customer_id narrows the seek
EXPLAIN SELECT * FROM orders WHERE customer_id = 42 AND order_date >= '2024-06-01';
-- Q4: leftmost column missing                               -> index not usable
EXPLAIN SELECT * FROM orders WHERE status = 'shipped' AND order_date >= '2024-06-01';
-- Q5: only the last column                                  -> index not usable
EXPLAIN SELECT * FROM orders WHERE order_date >= '2024-06-01';
-- Q6: range on status, equality after it                    -> order_date can't narrow the seek
EXPLAIN SELECT * FROM orders WHERE customer_id = 42 AND status > 'a' AND order_date = '2024-06-01';
-- Q7/Q8: ORDER BY satisfied by index order (no filesort)
EXPLAIN SELECT * FROM orders WHERE customer_id = 42 ORDER BY status, order_date;
EXPLAIN SELECT * FROM orders WHERE customer_id = 42 AND status = 'shipped' ORDER BY order_date;

-- ============================================
-- EXPECTED OUTPUT (verified on MySQL 9.1, 20,000 rows; rows are estimates)
-- ============================================

-- Q  | type  | key                  | key_len | rows  | Extra
-- Q1 | range | idx_cust_status_date | 89      | 9     | Using index condition
-- Q2 | ref   | idx_cust_status_date | 4       | 40    | NULL
-- Q3 | ref   | idx_cust_status_date | 4       | 40    | Using index condition  (key_len 4 = only customer_id seeks)
-- Q4 | ALL   | NULL                 | NULL    | 20160 | Using where
-- Q5 | ALL   | NULL                 | NULL    | 20160 | Using where
-- Q6 | range | idx_cust_status_date | 86      | 40    | Using index condition  (order_date only filtered)
-- Q7 | ref   | idx_cust_status_date | 4       | 40    | NULL                   (no "Using filesort")
-- Q8 | ref   | idx_cust_status_date | 86      | 13    | NULL                   (no "Using filesort")

-- PostgreSQL (PGlite) for Q1, Q4, Q3:
--   Q1: Bitmap Index Scan on idx_cust_status_date, Index Cond: all 3 predicates
--   Q4: Seq Scan on orders (Filter: order_date..., status...)   <- leading column missing
--   Q3: Bitmap Index Scan, Index Cond: (customer_id = 42) AND (order_date >= ...)
--       (PgSQL can evaluate non-prefix columns inside the index, but it still has to scan the
--        whole customer_id=42 range of the index - cheaper than heap but not a tight seek)
```

---

## 🔍 Why This Works (3 lines max)
Entries are ordered by (customer_id, status, order_date); without a fixed customer_id the matching status/date entries are scattered across the whole tree, so there is no contiguous range to seek. After the first range predicate the later columns are only filters, not seek keys.
हिंदी: Index (customer_id, status, order_date) के क्रम में sorted है; पहला column न हो तो matching entries पूरे tree में बिखरे होते हैं।

---

## ⚡ Alternative Solution

```sql
-- Choosing column order (checklist)
-- 1. Columns tested with "=" first, in any order among themselves for filtering power
-- 2. Then ONE range or ORDER BY column last (so index order serves the sort)
-- 3. If several queries differ, put the column most queries filter on first
-- 4. Selectivity is a tie-breaker, NOT the main rule:
--      (status, customer_id) is worse than (customer_id, status) if queries often filter customer_id alone

-- Need to serve "WHERE status = ? AND order_date >= ?" as well? Add a second index:
CREATE INDEX idx_status_date ON orders (status, order_date);

-- MySQL 8.0 can sometimes "skip scan" a low-cardinality leading column (optimizer decides);
-- it was NOT chosen for Q4 here (full scan). PostgreSQL has no skip scan before v18.
-- Covering variant (both DBs): add amount to avoid table lookups:
--   MySQL:  INDEX (customer_id, status, order_date, amount)
--   PgSQL:  CREATE INDEX ... ON orders (customer_id, status, order_date) INCLUDE (amount);
```

---

## ⚠️ Common Mistake

```sql
-- ❌ Wrong: putting the range column in the middle
INDEX (customer_id, order_date, status)
-- WHERE customer_id = 42 AND order_date >= '2024-06-01' AND status = 'shipped'
-- order_date range stops the seek; status is only a filter.
-- ✅ INDEX (customer_id, status, order_date)  -> equality, equality, range

-- ❌ Wrong: creating (customer_id) AND (customer_id, status, order_date)
-- The single-column index is redundant - the composite already serves its prefix. Drop it.

-- ❌ Wrong: assuming mixed ORDER BY directions use the index in MySQL 5.7
-- ORDER BY status ASC, order_date DESC needs a filesort in 5.7; MySQL 8.0 supports
-- descending index parts: INDEX (customer_id, status ASC, order_date DESC).
```

---

## 🎯 Interview Tip (1 line)
Say: "Leftmost-prefix rule: equality columns first, then the range or ORDER BY column; I verify with EXPLAIN (key_len shows how many columns actually seek) and drop redundant prefix indexes because every extra index slows writes."

---

## 🔗 Related Questions
→ Q081 (B-Tree index internals) | Q084 (Covering index) | Q086 (EXPLAIN output) | Q088 (When MySQL does NOT use an index)
