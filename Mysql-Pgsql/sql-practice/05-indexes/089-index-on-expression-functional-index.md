---

# Q089. Index on Expression / Functional Index (PgSQL)
# Category: Indexes
# Difficulty: ⭐⭐ Medium
# DB: PostgreSQL (MySQL 8.0.13+ equivalent shown)

---

## ❓ Question
`WHERE LOWER(email) = '...'` does a full table scan even though `email` is indexed. How do you make it fast in PostgreSQL with an expression (functional) index? What are the rules and the MySQL equivalent?

---

## 💡 Quick Concept (2 lines only)
An expression index stores the RESULT of an expression (e.g. `LOWER(email)`) in the B-Tree, so queries that use exactly that expression become index lookups. The expression must be IMMUTABLE and the query must repeat it identically.
हिंदी: Expression index में function का result store होता है; query में वही expression लिखो तभी index चलेगा, और function IMMUTABLE होना चाहिए।

---

## ✅ Answer / Solution

```sql
-- ============================================
-- SETUP (run this first) - PostgreSQL
-- ============================================

CREATE TABLE users (
  user_id    BIGINT PRIMARY KEY,
  email      VARCHAR(100) NOT NULL,
  full_name  VARCHAR(100),
  created_at TIMESTAMP NOT NULL
);

INSERT INTO users
SELECT n,
       CASE WHEN n % 2 = 0 THEN 'User' || n || '@Example.com'      -- mixed-case emails
            ELSE 'user' || n || '@example.com' END,
       'Name ' || n,
       TIMESTAMP '2024-01-01' + n * INTERVAL '10 minute'
FROM generate_series(1, 20000) n;
ANALYZE users;

-- ============================================
-- SOLUTION
-- ============================================

-- Step 1: without the index, the function forces a Seq Scan
EXPLAIN SELECT * FROM users WHERE LOWER(email) = 'user42@example.com';

-- Step 2: create the expression index (note the extra parentheses are optional for a plain function call)
CREATE INDEX idx_users_lower_email ON users (LOWER(email));
ANALYZE users;

-- Step 3: same query now uses it
EXPLAIN SELECT * FROM users WHERE LOWER(email) = 'user42@example.com';

-- Step 4: it only helps queries with the SAME expression
EXPLAIN SELECT * FROM users WHERE email = 'user42@example.com';

-- Step 5: date bucket index, and a case-insensitive UNIQUE rule
CREATE INDEX idx_users_day ON users (DATE(created_at));       -- created_at is TIMESTAMP (no tz)
ANALYZE users;
EXPLAIN SELECT count(*) FROM users WHERE DATE(created_at) = '2024-02-01';
CREATE UNIQUE INDEX uq_users_lower_email ON users (LOWER(email));   -- no 'A@x.com' vs 'a@x.com' duplicates

-- ============================================
-- EXPECTED OUTPUT (verified on PostgreSQL 18 via PGlite; costs vary)
-- ============================================

-- Step 1: Seq Scan on users (cost=0.00..517.00 rows=100 width=55)
--           Filter: (lower((email)::text) = 'user42@example.com'::text)
-- Step 3: Index Scan using idx_users_lower_email on users (cost=0.29..8.30 rows=1 width=55)
--           Index Cond: (lower((email)::text) = 'user42@example.com'::text)
-- Result row: 42 | User42@Example.com            (matched despite different case)
-- Step 4: Seq Scan on users ... Filter: ((email)::text = 'user42@example.com'::text)  <- plain email = ... no index
-- Step 5: Index Scan using idx_users_day (rows=144), Index Cond: (date(created_at) = '2024-02-01'::date)
-- UNIQUE expression index created without error.
```

---

## 🔍 Why This Works (3 lines max)
The planner can use an index only when the query expression matches the indexed expression, since the tree is ordered by the computed value. The function must be IMMUTABLE (same input, same output forever) because the stored values are never recomputed at query time.
हिंदी: Planner तभी index चुनता है जब query का expression index वाले expression से match करे; function IMMUTABLE हो ताकि stored value कभी न बदले।

---

## ⚡ Alternative Solution

```sql
-- MySQL 8.0.13+ functional key part (note the DOUBLE parentheses). Verified on MySQL 9.1:
CREATE INDEX idx_users_lower_email ON users ((LOWER(email)));
CREATE INDEX idx_users_day         ON users ((DATE(created_at)));
EXPLAIN SELECT * FROM users WHERE LOWER(email) = 'user42@example.com';     -- type=ref, key=idx_users_lower_email, rows=1
EXPLAIN SELECT * FROM users WHERE DATE(created_at) = '2024-02-01';        -- type=ref, key=idx_users_day, rows=144
-- SHOW INDEX Expression column displays: lower(`email`) and cast(`created_at` as date)
-- MySQL builds a hidden VIRTUAL generated column for it. (Default MySQL collations are already
-- case-insensitive, so LOWER(email) is rarely needed there.)

-- PostgreSQL alternatives:
--  * citext extension column type: email CITEXT (case-insensitive compare, plain index works) - extension, not run here.
--  * Generated column + normal index (PG 12+ STORED): ADD COLUMN email_lc text GENERATED ALWAYS AS (lower(email)) STORED;
--  * Partial + expression combined: CREATE INDEX ... (LOWER(email)) WHERE deleted_at IS NULL;  (see Q090)
```

---

## ⚠️ Common Mistake

```sql
-- ❌ Wrong: non-IMMUTABLE expression, e.g. DATE() on TIMESTAMPTZ (depends on session time zone)
CREATE TABLE t (id int, ts TIMESTAMPTZ);
CREATE INDEX bad ON t (DATE(ts));
-- ERROR: functions in index expression must be marked IMMUTABLE      (verified)
-- ✅ Pin the zone:  CREATE INDEX ok ON t (DATE(ts AT TIME ZONE 'UTC'));   or use a TIMESTAMP column.

-- ❌ Wrong: index on LOWER(email), query on UPPER(email) or plain email -> Seq Scan (expression must match)
-- ✅ Standardize one normalized form (always LOWER) in code and in the index.

-- ❌ Wrong: expecting a plain index on (email) to serve case-insensitive search in PostgreSQL
-- PgSQL string compare is case-sensitive by default (MySQL is insensitive) - another cross-DB gotcha.

-- Cost: index entries are computed on every INSERT/UPDATE of the column (write overhead).
```

---

## 🎯 Interview Tip (1 line)
Say: "I'd index LOWER(email) (ideally UNIQUE to enforce case-insensitive uniqueness), keep the query expression identical, make sure the function is IMMUTABLE, and weigh write overhead; MySQL 8.0.13+ offers the same via ((expr)) indexes, and CITEXT or a generated column are alternatives."

---

## 🔗 Related Questions
→ Q085 (Index on NULL values) | Q088 (When MySQL does NOT use an index) | Q090 (Partial index PgSQL) | Q091 (Full-text index)
