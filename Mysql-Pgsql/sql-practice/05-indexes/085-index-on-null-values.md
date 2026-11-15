---

# Q085. Index on NULL Values - Does It Work?
# Category: Indexes
# Difficulty: ⭐⭐ Medium
# DB: Both (MySQL 8.0+ | PostgreSQL)

---

## ❓ Question
Are NULL values stored in an index? Can `WHERE col IS NULL` / `IS NOT NULL` use an index in MySQL and PostgreSQL? How do UNIQUE indexes treat multiple NULLs, and when is a plain index on a mostly-NULL column a waste?

---

## 💡 Quick Concept (2 lines only)
Both MySQL (InnoDB) and PostgreSQL B-Trees DO store NULLs, so `IS NULL` can use an index (unlike old Oracle). The optimizer still chooses a scan when a predicate matches most rows, and UNIQUE indexes allow many NULLs because NULL != NULL.
हिंदी: दोनों DB के B-Tree में NULL store होता है, IS NULL index use कर सकता है; UNIQUE में कई NULL allowed हैं।

---

## ✅ Answer / Solution

```sql
-- ============================================
-- SETUP (run this first) - MySQL 8.0+
-- ============================================

SET SESSION cte_max_recursion_depth = 100000;

CREATE TABLE users (
  user_id    BIGINT PRIMARY KEY,
  email      VARCHAR(100) NOT NULL,
  phone      VARCHAR(20)  NULL,           -- only 1% of users have a phone
  deleted_at DATETIME     NULL,           -- soft delete: 2% deleted, 98% NULL
  INDEX idx_deleted_at (deleted_at),
  UNIQUE KEY uq_phone (phone)             -- UNIQUE still permits many NULLs
);

INSERT INTO users
SELECT n, CONCAT('u', n, '@x.com'),
       IF(n % 100 = 0, CONCAT('9', LPAD(n, 9, '0')), NULL),
       IF(n % 50  = 0, NOW(), NULL)
FROM (WITH RECURSIVE s AS (SELECT 1 AS n UNION ALL SELECT n + 1 FROM s WHERE n < 20000)
      SELECT n FROM s) x;
ANALYZE TABLE users;

-- PostgreSQL setup instead:
--   CREATE TABLE users (user_id BIGINT PRIMARY KEY, email VARCHAR(100) NOT NULL,
--                       phone VARCHAR(20), deleted_at TIMESTAMP);
--   INSERT INTO users SELECT n, 'u'||n||'@x.com',
--          CASE WHEN n%100=0 THEN '9'||lpad(n::text,9,'0') END,
--          CASE WHEN n%50=0  THEN now() END FROM generate_series(1,20000) n;
--   CREATE UNIQUE INDEX uq_phone ON users(phone);
--   CREATE INDEX idx_deleted_partial ON users(user_id) WHERE deleted_at IS NOT NULL;  -- partial (Q090)

-- ============================================
-- SOLUTION
-- ============================================

SELECT COUNT(*) AS total, COUNT(phone) AS with_phone FROM users;   -- COUNT(col) skips NULLs

EXPLAIN SELECT * FROM users WHERE phone IS NULL;                    -- A
EXPLAIN SELECT * FROM users WHERE phone IS NOT NULL;                -- B
EXPLAIN SELECT * FROM users WHERE phone = '9000000100';             -- C
EXPLAIN SELECT * FROM users WHERE deleted_at IS NOT NULL;           -- D
EXPLAIN SELECT * FROM users WHERE phone = '9000000100' OR phone IS NULL;  -- E

-- UNIQUE with NULLs, and the three-valued logic traps
INSERT INTO users (user_id, email, phone) VALUES (30001,'a@x.com',NULL), (30002,'b@x.com',NULL);  -- OK
SELECT COUNT(*) FROM users WHERE phone = NULL;                      -- F: always 0
SELECT COUNT(*) FROM users WHERE phone <> '9000000100';             -- G: NULL rows excluded

-- ============================================
-- EXPECTED OUTPUT (verified on MySQL 9.1, 20,000 rows; rows = optimizer estimate)
-- ============================================

-- total | with_phone
-- 20000 | 200
--
-- Q | type        | key            | rows  | note
-- A | ref         | uq_phone       | 10199 | IS NULL uses the index (estimate is rough; ~19,800 real)
-- B | range       | uq_phone       | 200   | index range over non-NULL entries
-- C | const       | uq_phone       | 1     |
-- D | range       | idx_deleted_at | 400   |
-- E | ref_or_null | uq_phone       | 10200 | MySQL's special access type for "= x OR IS NULL"
--
-- F -> 0   (col = NULL is never true)        G -> 199 (the 2 new NULL rows and all old NULLs are excluded)
-- Inserting two NULL phones into the UNIQUE column succeeded.

-- PostgreSQL 18 (PGlite) results, same data:
--   phone IS NULL      -> Seq Scan (rows=19800: matches 99% of the table, index not worth it)
--   phone IS NOT NULL  -> Index Scan using uq_phone, Index Cond: (phone IS NOT NULL)
--   deleted_at IS NOT NULL (partial index) -> Index Scan / Index Only Scan using idx_deleted_partial
-- With RARE NULLs (1 in 1000 rows, PgSQL and MySQL both): WHERE manager_id IS NULL
--   -> Index Scan using idx_mgr, Index Cond: (manager_id IS NULL), rows=20
```

---

## 🔍 Why This Works (3 lines max)
NULLs are ordinary index entries (sorted first or last), so IS NULL is a normal range lookup; whether it is used depends only on selectivity, exactly like any other value. UNIQUE treats NULLs as distinct values, so any number of NULLs can coexist.
हिंदी: NULL भी index entry है, इसलिए IS NULL index चला सकता है; use होगा या नहीं ये selectivity पर निर्भर है।

---

## ⚡ Alternative Solution

```sql
-- PostgreSQL 15+: make NULLs collide in a UNIQUE index
CREATE UNIQUE INDEX uq_phone_strict ON users (phone) NULLS NOT DISTINCT;
-- Verified on PGlite: second INSERT of NULL -> ERROR duplicate key value violates unique constraint
-- MySQL has no NULLS NOT DISTINCT; to allow only one NULL, enforce it in the app or with a sentinel/generated column.

-- Mostly-NULL column where you only query the non-NULL rows (PostgreSQL): partial index is far smaller
CREATE INDEX idx_phone_notnull ON users (phone) WHERE phone IS NOT NULL;

-- MySQL has no partial indexes: a normal index on phone is the only option (NULL entries still take space).

-- NULL-safe equality (both): MySQL  a <=> b   |   PostgreSQL  a IS NOT DISTINCT FROM b
```

---

## ⚠️ Common Mistake

```sql
-- ❌ Wrong: WHERE phone = NULL           -- always 0 rows, index or not
-- ✅ WHERE phone IS NULL

-- ❌ Wrong: WHERE phone <> '9000000100'  and expecting NULL rows too (they are excluded)
-- ✅ WHERE phone <> '9000000100' OR phone IS NULL     (PgSQL: phone IS DISTINCT FROM '9000000100')

-- ❌ Wrong: believing "NULLs are not indexed, so IS NULL is always a full scan" (Oracle folklore)
-- ✅ MySQL InnoDB and PostgreSQL both index NULLs.

-- ❌ Wrong: NOT IN (subquery returning a NULL) -> returns zero rows, regardless of indexes
-- ✅ Use NOT EXISTS.
```

---

## 🎯 Interview Tip (1 line)
Say: "Both engines index NULLs, so IS NULL is index-eligible and the decision is pure selectivity; for soft-delete style columns in PostgreSQL I use a partial index, and I remember UNIQUE allows multiple NULLs unless I use PG15+ NULLS NOT DISTINCT."

---

## 🔗 Related Questions
→ Q081 (B-Tree index internals) | Q088 (When MySQL does NOT use an index) | Q090 (Partial index PgSQL) | Q086 (EXPLAIN output)
