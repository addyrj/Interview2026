---

# Q088. When Does MySQL NOT Use an Index?
# Category: Indexes
# Difficulty: ⭐⭐⭐ Hard
# DB: MySQL (with PostgreSQL notes)

---

## ❓ Question
You created an index but EXPLAIN shows `type: ALL` (full table scan). List the classic reasons MySQL ignores an index and show how to rewrite each query so the index IS used.

---

## 💡 Quick Concept (2 lines only)
An index is usable only when the predicate is "sargable": the indexed column must appear bare, compared with a compatible type, and with a leftmost-anchored pattern. Otherwise MySQL must evaluate every row, and it also skips indexes when it estimates a scan is cheaper.
हिंदी: Index तभी चलता है जब column पर function/cast/leading % न हो; वरना MySQL पूरा table scan करता है।

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
  phone      VARCHAR(15)  NOT NULL,           -- stored as STRING
  status     VARCHAR(10)  NOT NULL,
  created_at DATETIME     NOT NULL,
  country    VARCHAR(2)   NOT NULL,
  bio        VARCHAR(50),                      -- NOT indexed
  INDEX idx_email (email), INDEX idx_phone (phone), INDEX idx_created (created_at),
  INDEX idx_status (status), INDEX idx_country (country)
);

INSERT INTO users
SELECT n, CONCAT('user', n, '@example.com'), CONCAT('9', LPAD(n, 9, '0')),
       IF(n % 20 = 0, 'inactive', 'active'), DATE_ADD('2023-01-01', INTERVAL n MINUTE),
       ELT(1 + n % 3, 'IN', 'US', 'UK'), NULL
FROM (WITH RECURSIVE s AS (SELECT 1 AS n UNION ALL SELECT n + 1 FROM s WHERE n < 20000)
      SELECT n FROM s) x;
ANALYZE TABLE users;

-- ============================================
-- SOLUTION: bad query  ->  fixed query
-- ============================================

-- 1) Function on the column
EXPLAIN SELECT * FROM users WHERE UPPER(email) = 'USER42@EXAMPLE.COM';          -- BAD  (ALL)
EXPLAIN SELECT * FROM users WHERE DATE(created_at) = '2023-01-05';               -- BAD  (ALL)
EXPLAIN SELECT * FROM users WHERE created_at >= '2023-01-05' AND created_at < '2023-01-06';  -- GOOD (range)
-- (email is case-insensitive under the default collation, so plain  email = '...'  already matches)

-- 2) Leading wildcard
EXPLAIN SELECT * FROM users WHERE email LIKE '%42@example.com';                  -- BAD  (ALL)
EXPLAIN SELECT * FROM users WHERE email LIKE 'user42%';                          -- GOOD (range)

-- 3) Implicit type conversion (string column compared with a NUMBER)
EXPLAIN SELECT * FROM users WHERE phone = 9000000042;                            -- BAD  (ALL)
EXPLAIN SELECT * FROM users WHERE phone = '9000000042';                          -- GOOD (ref)

-- 4) Arithmetic on the column
EXPLAIN SELECT * FROM users WHERE user_id + 1 = 43;                              -- BAD  (ALL)
EXPLAIN SELECT * FROM users WHERE user_id = 42;                                  -- GOOD

-- 5) OR with an un-indexed column vs OR with indexed columns
EXPLAIN SELECT * FROM users WHERE email = 'user42@example.com' OR bio = 'x';     -- BAD  (ALL)
EXPLAIN SELECT * FROM users WHERE email = 'user42@example.com' OR phone = '9000000043';  -- index_merge

-- 6) Low selectivity (optimizer chooses scan on purpose)
EXPLAIN SELECT * FROM users WHERE status <> 'inactive';                          -- ALL: matches 95%

-- ============================================
-- EXPECTED OUTPUT (verified on MySQL 9.1, 20,000 rows; "rows" are estimates)
-- ============================================

-- Query                                   | type        | key                  | rows
-- UPPER(email) = ...                      | ALL         | NULL                 | 20160
-- DATE(created_at) = ...                  | ALL         | NULL                 | 20160
-- created_at >= .. AND < ..               | range       | idx_created          | 1440
-- email LIKE '%42@example.com'            | ALL         | NULL                 | 20160
-- email LIKE 'user42%'                    | range       | idx_email            | 111
-- phone = 9000000042  (number)            | ALL         | NULL                 | 20160
-- phone = '9000000042' (string)           | ref         | idx_phone            | 1
-- user_id + 1 = 43                        | ALL         | NULL                 | 20160
-- email = .. OR bio = 'x'                 | ALL         | NULL                 | 20160
-- email = .. OR phone = ..                | index_merge | idx_email,idx_phone  | 2
-- status <> 'inactive'                    | ALL         | NULL                 | 20160
-- status <> 'active' (5% of rows)         | range       | idx_status           | 1001
--
-- Surprise (verified): country = 'IN' (33% of rows) and status = 'active' (95%!) STILL used the index
-- (rows=6666 / 10080 estimates) - MySQL has no histogram by default and index dives are optimistic,
-- while status <> 'inactive' flipped to ALL. Don't predict, run EXPLAIN.
```

---

## 🔍 Why This Works (3 lines max)
B-Tree order is on the raw column value, so any transformation (function, cast, arithmetic, leading `%`) breaks the ordering and forces per-row evaluation. Rewrite the predicate so the column stands alone and the constant side does the conversion.
हिंदी: B-Tree raw value पर sorted होता है, इसलिए column पर function या cast लगाने से ordering बेकार हो जाती है; constant वाली तरफ convert करो।

---

## ⚡ Alternative Solution

```sql
-- MySQL 8.0.13+: functional index lets you keep the function in the query
CREATE INDEX idx_email_upper ON users ((UPPER(email)));
EXPLAIN SELECT * FROM users WHERE UPPER(email) = 'USER42@EXAMPLE.COM';   -- now uses idx_email_upper
-- Verified: type=ref, key=idx_email_upper, rows=1. (Functional index = hidden generated column + index; see Q089.)

-- Leading-wildcard search needs FULLTEXT (Q091) or a reversed-string column, not a B-Tree.
-- Stale stats: ANALYZE TABLE users;   Force/ignore for testing: FORCE INDEX (idx) / IGNORE INDEX (idx)

-- PostgreSQL differences (verified on PGlite, PG 18):
--   UPPER(email) = '..'     -> Seq Scan (same problem; fix with expression index, Q089)
--   phone = 9000000042      -> ERROR: operator does not exist: character varying = bigint
--                              (PgSQL refuses the implicit cast; MySQL silently converts and loses the index)
--   email LIKE 'user42%'    -> Index Cond: (email >= 'user42' AND email < 'user43')  - works here in C collation;
--                              under en_US.UTF-8 you need  CREATE INDEX ... (email text_pattern_ops)  (not run)
```

---

## ⚠️ Common Mistake

```sql
-- ❌ Wrong: WHERE phone = 9000000042   (number vs VARCHAR) -> every row is cast to a number, index useless
--   Worse: results can be wrong too - '9000000042abc' casts to the same number.
-- ✅ WHERE phone = '9000000042'  - quote string literals, and match parameter types in prepared statements.

-- ❌ Wrong: WHERE DATE(created_at) = '2023-01-05'  -> use a half-open range instead
-- ✅ WHERE created_at >= '2023-01-05' AND created_at < '2023-01-06'

-- ❌ Wrong: joining columns with different charset/collation (utf8mb4 vs latin1) or different types
-- (INT vs VARCHAR) - the index on the converted side cannot be used. Keep join column definitions identical.

-- ❌ Wrong: forcing an index with FORCE INDEX permanently - plans change as data grows.
```

---

## 🎯 Interview Tip (1 line)
Say: "I check sargability first (no function, cast or arithmetic on the column, no leading wildcard, matching types), then leftmost prefix and selectivity; I confirm with EXPLAIN type/key/rows, and I use functional indexes or generated columns when the expression is unavoidable."

---

## 🔗 Related Questions
→ Q083 (Composite index order) | Q085 (Index on NULL values) | Q086 (EXPLAIN output) | Q089 (Functional index PgSQL) | Q091 (Full-text index)
