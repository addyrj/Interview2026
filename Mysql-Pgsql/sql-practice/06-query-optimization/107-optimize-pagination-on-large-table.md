---

# Q107. Optimize Pagination on a Large Table
# Category: Query Optimization
# Difficulty: ⭐⭐⭐ Hard
# DB: Both (MySQL 8.0+ | PostgreSQL)

---

## ❓ Question
`LIMIT 20 OFFSET 250000` gets slower the deeper the page. Why, and how do you paginate a 300k+ row `products` table efficiently? Cover keyset (seek) pagination, the deferred-join trick, and a MySQL pitfall with row-value comparisons.

---

## 💡 Quick Concept (2 lines only)
OFFSET N reads and discards N rows, so cost grows linearly with page depth. Keyset pagination remembers the last (sort key, id) and asks for rows "after" it using an index range seek - constant cost per page.
हिंदी: OFFSET पहले N rows पढ़कर फेंकता है, इसलिए गहरे page धीमे होते हैं; keyset में आखिरी row की key से आगे का range seek होता है।

---

## ✅ Answer / Solution

```sql
-- ============================================
-- SETUP — MySQL (verified on MySQL 9.1.0, 300,000 rows)
-- ============================================

CREATE TABLE products (
  id          INT PRIMARY KEY AUTO_INCREMENT,
  name        VARCHAR(80) NOT NULL,
  category_id INT NOT NULL,
  price       DECIMAL(10,2) NOT NULL,
  description VARCHAR(300) NOT NULL,
  created_at  DATETIME NOT NULL,
  KEY idx_created_id (created_at, id)       -- sort key + unique tiebreaker
);
SET SESSION cte_max_recursion_depth = 300000;
INSERT INTO products (name, category_id, price, description, created_at)
WITH RECURSIVE n AS (SELECT 1 i UNION ALL SELECT i+1 FROM n WHERE i < 300000)
SELECT CONCAT('Product ', i), i % 50 + 1, 5 + (i % 995), REPEAT('d',200),
       TIMESTAMP('2023-01-01') + INTERVAL i MINUTE FROM n;
ANALYZE TABLE products;

-- ============================================
-- SOLUTION
-- ============================================

-- Step 1: OFFSET pagination - page 1 vs page 12,501
EXPLAIN ANALYZE SELECT id, name, price FROM products ORDER BY created_at DESC, id DESC LIMIT 20 OFFSET 0;
EXPLAIN ANALYZE SELECT id, name, price FROM products ORDER BY created_at DESC, id DESC LIMIT 20 OFFSET 250000;

-- Step 2: the cursor = last row of the previous page
SELECT id, created_at FROM products ORDER BY created_at DESC, id DESC LIMIT 3 OFFSET 250019;
--   49981 | 2023-02-04 17:01:00 (last row of page) -> next page starts AFTER (2023-02-04 17:01:00, 49981)

-- Step 3a: keyset with a ROW VALUE comparison - looks right, but MySQL scans!
EXPLAIN ANALYZE SELECT id, name, price FROM products
WHERE (created_at, id) < ('2023-02-04 17:01:00', 49981)
ORDER BY created_at DESC, id DESC LIMIT 20;

-- Step 3b: same logic, expanded - MySQL can range-scan this
EXPLAIN ANALYZE SELECT id, name, price FROM products
WHERE created_at < '2023-02-04 17:01:00' OR (created_at = '2023-02-04 17:01:00' AND id < 49981)
ORDER BY created_at DESC, id DESC LIMIT 20;

-- Step 3c: also fine, even better for the range bound
SELECT id, name, price FROM products
WHERE created_at <= '2023-02-04 17:01:00' AND (created_at < '2023-02-04 17:01:00' OR id < 49981)
ORDER BY created_at DESC, id DESC LIMIT 3;

-- Step 4: deferred join - keeps OFFSET but reads only the narrow index, then fetches 20 full rows
EXPLAIN ANALYZE SELECT p.id, p.name, p.price
FROM products p
JOIN (SELECT id FROM products ORDER BY created_at DESC, id DESC LIMIT 20 OFFSET 250000) x ON x.id = p.id
ORDER BY p.created_at DESC, p.id DESC;

-- ============================================
-- EXPECTED OUTPUT (real, MySQL 9.1.0; timings vary by machine)
-- ============================================
-- Step 1 OFFSET 0     : Index scan on products using idx_created_id (reverse) rows=20,  actual 0.04 ms
-- Step 1 OFFSET 250000: Limit/Offset 20/250000 <- Sort (limit input to 250020 rows) <- Table scan rows=300000
--                       actual ~162 ms   (the optimizer chose scan+sort, not the index)
-- Step 3a (row value) : Filter (created_at,id) < (...) over "Index scan ... (reverse)" read 250,040 rows, ~218 ms
-- Step 3b (expanded)  : Index range scan over (created_at < ...) OR (created_at = ... AND id < 49981) (reverse)
--                       actual 0.101..0.103 ms rows=20
-- Step 3c             : 49980 | Product 49980 | 235.00  /  49979 | Product 49979 | 234.00  /  49978 | Product 49978 | 233.00
-- Step 4 (deferred)   : Covering index scan ... rows=250020 then 20 PK lookups, actual ~52 ms  (3x faster than Step 1, still O(offset))
```

```sql
-- ============================================
-- POSTGRESQL (verified on PGlite = PostgreSQL 18.6)
-- ============================================
-- OFFSET: Limit -> Index Scan Backward using idx_created_id (actual rows=250020)   <- walks 250k entries
-- Keyset with row value - PostgreSQL handles it natively as an index condition:
SELECT id, name, price FROM products
WHERE (created_at, id) < ('2023-02-04 17:01:00', 49981)
ORDER BY created_at DESC, id DESC LIMIT 20;
-- Limit -> Index Scan Backward using idx_created_id (actual rows=20)
--   Index Cond: (ROW(created_at, id) < ROW('2023-02-04 17:01:00', 49981))      <- no filter, real seek
-- first rows: 49980 | Product 49980 | 235.00 ; 49979 | 234.00 ; 49978 | 233.00   (identical to MySQL)
```

---

## 🔍 Why This Works (3 lines max)
The keyset predicate turns "skip N rows" into a B-tree seek to the last-seen key followed by 20 reads, independent of page depth; (created_at, id) makes the order total so no rows are skipped or repeated. MySQL's optimizer only applies the seek when the condition is written in expanded boolean form.
हिंदी: Keyset में गहराई मायने नहीं रखती क्योंकि सीधे आखिरी key पर seek होता है; MySQL में row-value की जगह expanded OR/AND लिखो।

---

## ⚡ Alternative Solution

```sql
-- Deferred join (above) when you need arbitrary page jumps (page 500 of 1000) and keyset cannot jump.
-- Pre-computed page markers: store every 1000th id/created_at in a helper table, then keyset from the nearest marker.
-- Bidirectional keyset (previous page): flip comparison and ORDER BY, then reverse the 20 rows in the app.
-- Limit "deep paging" in the API (max page 100) and expose search/filters instead - Google-like UX.
-- Total page count: never COUNT(*) per request (see Q106); use an estimate or "has_next" via LIMIT 21.
```

---

## ⚠️ Common Mistake

```sql
-- ❌ OFFSET for infinite scroll / exports
SELECT * FROM products ORDER BY created_at DESC LIMIT 20 OFFSET 250000;   -- 162 ms vs 0.04 ms for page 1
-- ❌ Keyset on a non-unique sort key only:  WHERE created_at < :last   -> rows with identical timestamps are skipped
-- ❌ MySQL: WHERE (created_at, id) < (?, ?) assuming it is a range seek (verified: 250k rows examined)
-- ❌ ORDER BY without a matching index, or mixed ASC/DESC the index cannot serve
-- ✅ Unique, indexed, deterministic sort key + expanded predicate + opaque cursor token (base64) in the API.
```

---

## 🎯 Interview Tip (1 line)
Say: "OFFSET is O(offset) because skipped rows are still read; I switch to keyset pagination on a unique indexed sort key, mention MySQL needs the expanded OR form to get a range scan, and use deferred joins only when random page jumps are a hard requirement."

---

## 🔗 Related Questions
→ Q012 (Keyset / cursor pagination) | Q106 (Optimize COUNT(*)) | Q103 (Using filesort) | Q083 (Composite index order)
