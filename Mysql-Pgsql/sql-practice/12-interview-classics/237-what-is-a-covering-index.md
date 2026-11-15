---

# Q237. What Is a Covering Index?
# Category: Interview Classics
# Difficulty: ⭐⭐ Medium
# DB: Both (MySQL 8.0+ | PostgreSQL 11+ for INCLUDE)

---

## ❓ Question
What is a covering index? Show how a query is answered from the index alone (no table lookup), how to prove it with EXPLAIN, and how adding one extra selected column breaks it.

---

## 💡 Quick Concept (2 lines only)
A covering index contains every column the query needs (filter, group, select), so the engine never touches the table rows: MySQL shows "Using index", PostgreSQL shows "Index Only Scan".
हिंदी: Covering index में query की सारी columns होती हैं, इसलिए table पर जाना ही नहीं पड़ता।

---

## ✅ Answer / Solution

```sql
-- ============================================
-- SETUP — MySQL 8.0+ (20,000 rows)
-- ============================================

SET SESSION cte_max_recursion_depth = 30000;   -- default 1000 would abort the generator below

CREATE TABLE orders (
  id         INT PRIMARY KEY AUTO_INCREMENT,
  user_id    INT NOT NULL,
  status     VARCHAR(20) NOT NULL,
  amount     DECIMAL(10,2) NOT NULL,
  note       VARCHAR(200),
  created_at DATETIME NOT NULL
);

INSERT INTO orders (user_id, status, amount, note, created_at)
WITH RECURSIVE n AS (SELECT 1 AS i UNION ALL SELECT i+1 FROM n WHERE i < 20000)
SELECT i % 500 + 1,
       ELT(i % 3 + 1, 'completed', 'pending', 'refunded'),
       (i % 97) + 0.50,
       CONCAT('note ', i),
       '2024-01-01' + INTERVAL i MINUTE
FROM n;

-- ============================================
-- SOLUTION (MySQL)
-- ============================================

-- Step 1: index only on user_id -> must visit the table for status and amount
CREATE INDEX idx_user ON orders (user_id);
ANALYZE TABLE orders;
EXPLAIN SELECT user_id, status, SUM(amount) FROM orders
WHERE user_id = 42 GROUP BY user_id, status;
-- key: idx_user | rows: 40 | Extra: Using temporary        (index + row lookups)

-- Step 2: covering index = filter column first, then the columns only read
CREATE INDEX idx_user_status_amount ON orders (user_id, status, amount);
ANALYZE TABLE orders;
EXPLAIN SELECT user_id, status, SUM(amount) FROM orders
WHERE user_id = 42 GROUP BY user_id, status;
-- key: idx_user_status_amount | rows: 40 | Extra: Using index   <- covered, no table access

-- Step 3: add a column that is NOT in the index -> no longer covered
EXPLAIN SELECT user_id, status, SUM(amount), MAX(note) FROM orders
WHERE user_id = 42 GROUP BY user_id, status;
-- key: idx_user_status_amount | Extra: NULL                  <- must fetch `note` from the row

SELECT user_id, status, SUM(amount) AS total FROM orders
WHERE user_id = 42 GROUP BY user_id, status ORDER BY status;

-- ============================================
-- SOLUTION (PostgreSQL) — INCLUDE keeps payload columns out of the sort key
-- ============================================
-- (use SERIAL / NUMERIC / generate_series for the table + data; see Alternative)
CREATE INDEX idx_user_status_amount ON orders (user_id, status) INCLUDE (amount);
VACUUM ANALYZE orders;   -- needed so the visibility map lets Index Only Scan skip the heap

EXPLAIN (COSTS OFF) SELECT user_id, status, SUM(amount) FROM orders
WHERE user_id = 42 GROUP BY user_id, status;
-- GroupAggregate
--   Group Key: status
--   ->  Index Only Scan using idx_user_status_amount on orders
--         Index Cond: (user_id = 42)

EXPLAIN (COSTS OFF) SELECT user_id, status, SUM(amount), MAX(note) FROM orders
WHERE user_id = 42 GROUP BY user_id, status;
-- HashAggregate
--   Group Key: status
--   ->  Bitmap Heap Scan on orders              <- note forces heap access
--         Recheck Cond: (user_id = 42)
--         ->  Bitmap Index Scan on idx_user_status_amount

-- ============================================
-- EXPECTED OUTPUT (identical on both)
-- ============================================
-- user_id | status    | total
-- 42      | completed | 656.50
-- 42      | pending   | 655.50
-- 42      | refunded  | 699.00
```

---

## 🔍 Why This Works (3 lines max)
The B-tree leaf entries already hold user_id, status and amount, so the engine reads them straight from the index. Column order matters: equality filter columns first, then GROUP BY/ORDER BY columns, then payload columns. PostgreSQL additionally needs a recent VACUUM so the visibility map says pages are all-visible.
हिंदी: Index के leaf में ही सारा data है, इसलिए table read नहीं होता; query में एक भी बाहर की column आई तो covering टूट जाती है।

---

## ⚡ Alternative Solution

```sql
-- PostgreSQL setup that was run (PGlite):
CREATE TABLE orders (
  id SERIAL PRIMARY KEY, user_id INT NOT NULL, status VARCHAR(20) NOT NULL,
  amount NUMERIC(10,2) NOT NULL, note VARCHAR(200), created_at TIMESTAMP NOT NULL
);
INSERT INTO orders (user_id, status, amount, note, created_at)
SELECT i % 500 + 1, (ARRAY['completed','pending','refunded'])[i % 3 + 1], (i % 97) + 0.50,
       'note ' || i, TIMESTAMP '2024-01-01' + i * INTERVAL '1 minute'
FROM generate_series(1, 20000) AS i;

-- MySQL vs PgSQL differences:
-- * MySQL has no INCLUDE; put payload columns in the key (wider key, usable for ORDER BY too).
-- * MySQL secondary indexes silently contain the PK, so (user_id) already covers `SELECT id, user_id`.
-- * PostgreSQL INCLUDE columns are not searchable/sortable, only returned; not allowed with every index type.
-- * PostgreSQL index-only scans still hit the heap for pages not marked all-visible (heavy-update tables).
```

---

## ⚠️ Common Mistake

```sql
-- ❌ SELECT * with a "covering" index -> never covered, every row is fetched from the table
SELECT * FROM orders WHERE user_id = 42;

-- ❌ Wrong column order: (amount, status, user_id) cannot seek on user_id = 42
-- ❌ Indexing every selected column of every query -> write amplification, huge indexes

-- ✅ Select only needed columns, filter column first, then payload
CREATE INDEX idx_user_status_amount ON orders (user_id, status, amount);
```

---

## 🎯 Interview Tip (1 line)
Say: "A covering index answers the query from the index alone; I verify with EXPLAIN (Using index / Index Only Scan), design it as equality columns, then range/sort, then payload (INCLUDE in PostgreSQL), and weigh it against slower writes and index size."

---

## 🔗 Related Questions
→ Q100 (Composite index column order) | Q101 (EXPLAIN reading) | Q231 (Primary key vs unique key) | Q228 (N+1 problem)
