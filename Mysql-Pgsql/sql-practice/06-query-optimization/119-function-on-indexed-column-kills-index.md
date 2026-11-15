---

# Q119. Function on Indexed Column Kills Index
# Category: Query Optimization
# Difficulty: ⭐⭐ Medium
# DB: Both

---

## ❓ Question
`WHERE DATE(created_at) = '2024-02-10'` on a table with an index on `created_at` is slow. Why is the index ignored, how do you rewrite it as a range, and what do you do when you genuinely need `LOWER(email)` or another expression (functional index / generated column)?

---

## 💡 Quick Concept (2 lines only)
A B-tree index stores the raw column values in sorted order; if you wrap the column in a function, the engine cannot binary-search the index (it would have to compute the function for every row). Keep the column bare ("sargable") and move the math to the constant side, or index the expression itself.
हिंदी: Index column की original values पर sorted होता है; column पर function लगाते ही index search नहीं हो पाता, इसलिए function constant वाली तरफ़ ले जाओ या expression पर index बनाओ।

---

## ✅ Answer / Solution

```sql
-- Verified: PostgreSQL on PGlite 18.6 and MySQL 9.1.0, 100,000 rows.

-- ============================================
-- SETUP (PostgreSQL)
-- ============================================

CREATE TABLE orders (
  id             SERIAL PRIMARY KEY,
  customer_email VARCHAR(100),
  created_at     TIMESTAMP,
  amount         NUMERIC(10,2)
);

INSERT INTO orders (customer_email, created_at, amount)
SELECT 'User' || g || '@Example.com',
       timestamp '2024-01-01' + (g || ' minutes')::interval,
       g % 500
FROM generate_series(1, 100000) g;

CREATE INDEX idx_orders_created_at ON orders (created_at);
CREATE INDEX idx_orders_email      ON orders (customer_email);
ANALYZE orders;

-- ============================================
-- SOLUTION
-- ============================================

-- Step 1: function on the column -> index unusable
EXPLAIN SELECT count(*) FROM orders WHERE DATE(created_at) = '2024-02-10';

-- Step 2: sargable range rewrite (half-open interval: >= start, < next day)
EXPLAIN SELECT count(*) FROM orders
WHERE created_at >= '2024-02-10' AND created_at < '2024-02-11';

-- Step 3: both return the same answer
SELECT count(*) FROM orders WHERE DATE(created_at) = '2024-02-10';
SELECT count(*) FROM orders WHERE created_at >= '2024-02-10' AND created_at < '2024-02-11';

-- Step 4: when the function is unavoidable, index the expression (PostgreSQL)
EXPLAIN SELECT id FROM orders WHERE lower(customer_email) = 'user500@example.com';   -- Seq Scan
CREATE INDEX idx_orders_email_lower ON orders (lower(customer_email));
ANALYZE orders;
EXPLAIN SELECT id FROM orders WHERE lower(customer_email) = 'user500@example.com';   -- Index Scan

-- ============================================
-- EXPECTED OUTPUT
-- ============================================

-- Step 1 (real):
-- Aggregate (cost=2435.25..2435.26 rows=1 width=8)
--   ->  Seq Scan on orders  (cost=0.00..2434.00 rows=500 width=0)
--         Filter: (date(created_at) = '2024-02-10'::date)
-- Step 2 (real):
-- Aggregate (cost=72.22..72.23 rows=1 width=8)
--   ->  Index Only Scan using idx_orders_created_at on orders  (cost=0.29..68.45 rows=1508 width=0)
-- Step 3: count = 1440 and 1440
-- Step 4 (real): Seq Scan (cost 2434.00) -> Index Scan using idx_orders_email_lower (cost 0.42..8.44)
-- Note the row estimate for Step 1 (500) is a blind default guess: the planner cannot use column stats through a function.
```

---

## 🔍 Why This Works (3 lines max)
`created_at >= X AND created_at < Y` is a contiguous range in the sorted index, so the engine seeks to X and reads until Y. `DATE(created_at) = ...` makes the engine evaluate the function on all 100,000 rows. An expression index stores the already-computed `lower(email)` values, so the lookup is a normal B-tree seek.
हिंदी: Range condition index में सीधे seek करती है, जबकि function हर row पर चलता है; expression index पहले से computed value store करके यह समस्या हल करता है।

---

## ⚡ Alternative Solution

```sql
-- MySQL 9.1.0 (real EXPLAIN; table identical, indexes idx_created_at, idx_email):
EXPLAIN SELECT COUNT(*) FROM orders WHERE DATE(created_at) = '2024-02-10';
--  type=index key=idx_created_at rows=99827  Extra: Using where; Using index
--  NOTE: it scans the WHOLE index (all 99,827 entries) - covering, but still a full index scan.
EXPLAIN SELECT COUNT(*) FROM orders WHERE created_at >= '2024-02-10' AND created_at < '2024-02-11';
--  type=range key=idx_created_at rows=1440  Using where; Using index

-- MySQL 8.0.13+ functional index (note DOUBLE parentheses):
ALTER TABLE orders ADD INDEX idx_email_lower ((LOWER(customer_email)));
--  EXPLAIN WHERE LOWER(customer_email)='user500@example.com' -> type=ref key=idx_email_lower rows=1
--  (before it: type=index rows=99827 full index scan)

-- MySQL generated column; optimizer even rewrites DATE(created_at) to use it (verified):
ALTER TABLE orders
  ADD COLUMN created_date DATE GENERATED ALWAYS AS (DATE(created_at)) VIRTUAL,
  ADD INDEX idx_created_date (created_date);
--  EXPLAIN WHERE DATE(created_at)='2024-02-10' -> key=idx_created_date rows=1440

-- Case-insensitive alternatives: PostgreSQL citext extension; MySQL default collations
-- (utf8mb4_0900_ai_ci) are already case-insensitive, so LOWER() is often unnecessary.
```

---

## ⚠️ Common Mistake
```sql
-- ❌ Wrong: function on the column
WHERE YEAR(created_at) = 2024                     -- MySQL
WHERE EXTRACT(YEAR FROM created_at) = 2024        -- PostgreSQL
WHERE amount + 0 = 5                              -- arithmetic on column (Seq Scan, verified on PostgreSQL)
WHERE CAST(id AS CHAR) = '42'                     -- implicit/explicit cast on the column
-- ✅ Correct: range on the bare column
WHERE created_at >= '2024-01-01' AND created_at < '2025-01-01'
-- ❌ BETWEEN '2024-02-10' AND '2024-02-10 23:59:59' misses 23:59:59.5 on fractional timestamps.
-- ✅ Always use half-open ranges: >= start AND < next_start.
-- ❌ Index expression must match the query EXACTLY: index on lower(email) is not used by upper(email).
```

---

## 🎯 Interview Tip (1 line)
Say: "I keep predicates sargable: bare column on the left, computed values on the right, half-open ranges for dates; when a function is truly needed I add a functional/expression index (PG) or functional index or generated column (MySQL 8) and verify with EXPLAIN."

---

## 🔗 Related Questions
→ Q117 (Avoid SELECT *) | Q118 (OR vs UNION) | Q109 (Slow query diagnosis) | Q114 (Statistics / ANALYZE)
