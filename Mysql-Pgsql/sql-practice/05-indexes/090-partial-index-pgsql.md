---

# Q090. Partial Index (PgSQL) - What and When
# Category: Indexes
# Difficulty: ⭐⭐ Medium
# DB: PostgreSQL (MySQL workaround shown)

---

## ❓ Question
What is a partial index in PostgreSQL, when should you use it (hot subset of rows, soft deletes, conditional uniqueness), and how do you get similar behaviour in MySQL, which has no partial indexes?

---

## 💡 Quick Concept (2 lines only)
A partial index is built with `WHERE <predicate>` and contains only the rows that satisfy it, so it is tiny, cheap to maintain and fast. The planner uses it only when the query's WHERE implies the index predicate.
हिंदी: Partial index सिर्फ उन rows को index करता है जो WHERE condition match करें; छोटा और तेज़ होता है, और query की condition उससे match होनी चाहिए।

---

## ✅ Answer / Solution

```sql
-- ============================================
-- SETUP (run this first) - PostgreSQL
-- ============================================

CREATE TABLE orders (
  order_id    BIGINT PRIMARY KEY,
  customer_id INT NOT NULL,
  status      VARCHAR(20) NOT NULL,
  created_at  TIMESTAMP NOT NULL,
  amount      NUMERIC(10,2)
);

-- 50,000 orders, only 1% are still 'pending'
INSERT INTO orders
SELECT n, 1 + n % 2000,
       CASE WHEN n % 100 = 0 THEN 'pending' ELSE 'completed' END,
       TIMESTAMP '2024-01-01' + n * INTERVAL '1 minute', n % 500
FROM generate_series(1, 50000) n;

-- ============================================
-- SOLUTION
-- ============================================

-- Full index vs partial index on the hot subset
CREATE INDEX idx_orders_status_full ON orders (status, created_at);
CREATE INDEX idx_orders_pending     ON orders (created_at) WHERE status = 'pending';
ANALYZE orders;

-- Compare sizes
SELECT indexname, pg_size_pretty(pg_relation_size(indexname::regclass)) AS size
FROM pg_indexes WHERE tablename = 'orders' ORDER BY indexname;

-- Query matching the predicate -> partial index
EXPLAIN SELECT order_id, created_at FROM orders
WHERE status = 'pending' AND created_at > '2024-02-01' ORDER BY created_at;

-- Query for the other status -> cannot use the partial index
EXPLAIN SELECT order_id FROM orders WHERE status = 'completed' AND created_at > '2024-02-01';

-- Conditional uniqueness: email unique only among NON-deleted accounts
CREATE TABLE accounts (account_id BIGINT PRIMARY KEY, email VARCHAR(100) NOT NULL, deleted_at TIMESTAMP);
CREATE UNIQUE INDEX uq_active_email ON accounts (email) WHERE deleted_at IS NULL;
INSERT INTO accounts VALUES (1, 'a@x.com', NULL), (2, 'b@x.com', NULL);
UPDATE accounts SET deleted_at = now() WHERE account_id = 1;       -- soft delete
INSERT INTO accounts VALUES (3, 'a@x.com', NULL);                   -- allowed: old a@x.com is deleted
INSERT INTO accounts VALUES (4, 'a@x.com', NULL);                   -- fails: active duplicate

-- ============================================
-- EXPECTED OUTPUT (verified on PostgreSQL 18 via PGlite; sizes approximate)
-- ============================================

-- indexname              | size
-- idx_orders_pending     | 32 kB        <- ~1% of rows
-- idx_orders_status_full | 2000 kB      <- ~60x bigger
-- orders_pkey            | 1112 kB
--
-- pending query:   Index Scan using idx_orders_pending on orders (rows=54)
--                    Index Cond: (created_at > '2024-02-01 00:00:00')       <- 'pending' is implied by the index
-- completed query: Bitmap Heap Scan ... Bitmap Index Scan on idx_orders_status_full  (partial index unusable)
--
-- accounts after the three inserts:
-- account_id | email   | active
-- 1          | a@x.com | false
-- 2          | b@x.com | true
-- 3          | a@x.com | true
-- 4th insert: ERROR duplicate key value violates unique constraint "uq_active_email"
```

---

## 🔍 Why This Works (3 lines max)
Only rows matching the predicate get index entries, so the index is small, stays in cache and rows leaving the predicate stop costing writes. The planner proves "query WHERE implies index WHERE" at plan time, so the predicate must be compatible with the query's constant conditions.
हिंदी: सिर्फ matching rows index में जाते हैं, इसलिए index छोटा और cache में रहता है; planner सिद्ध करता है कि query की WHERE index की WHERE को imply करती है।

---

## ⚡ Alternative Solution

```sql
-- MySQL has NO partial indexes (verified: "CREATE INDEX ... WHERE" is a syntax error on 9.1).
-- Workaround for CONDITIONAL UNIQUENESS: unique index over a generated column that is NULL when inactive
-- (UNIQUE allows many NULLs). Verified on MySQL 9.1:
CREATE TABLE accounts (
  account_id   BIGINT PRIMARY KEY,
  email        VARCHAR(100) NOT NULL,
  deleted_at   DATETIME NULL,
  active_email VARCHAR(100) GENERATED ALWAYS AS (IF(deleted_at IS NULL, email, NULL)) VIRTUAL,
  UNIQUE KEY uq_active_email (active_email)
);
-- Same inserts as above: ids 1,2 ok; soft-delete id 1 -> its active_email becomes NULL;
-- id 3 'a@x.com' accepted; id 4 'a@x.com' -> ERROR 1062 Duplicate entry 'a@x.com' for key 'accounts.uq_active_email'

-- For the "hot subset" speed-up in MySQL: composite index with status first, or a separate small table
-- (e.g. pending_orders) / partitioning. A MySQL index is always over the whole table.

-- PgSQL: partial + expression + covering are combinable:
--   CREATE INDEX ... ON orders (customer_id) INCLUDE (amount) WHERE status = 'pending';
```

---

## ⚠️ Common Mistake

```sql
-- ❌ Wrong: query does not repeat the predicate (or uses a parameter the planner can't prove)
SELECT * FROM orders WHERE created_at > '2024-02-01';        -- cannot use idx_orders_pending
-- ✅ Include  AND status = 'pending'  literally.

-- ❌ Wrong: prepared statement with a bind parameter for the predicate column
--   WHERE status = $1   -- a generic plan can't assume $1 = 'pending' -> partial index skipped
-- ✅ Put the constant in the SQL text, or rely on custom plans.

-- ❌ Wrong: partial index on a predicate that is true for most rows (saves nothing)
-- ✅ Use it where the subset is small: pending jobs, unprocessed events, active (non-deleted) rows, NOT NULL of a sparse column.

-- Note: with PostgreSQL 18, the planner could even use the full (status, created_at) index for a query without
-- status (skip scan; seen for the date-range query here). Don't assume - EXPLAIN.
```

---

## 🎯 Interview Tip (1 line)
Say: "For queue-like or soft-delete tables I create a partial index on the small hot subset (WHERE status='pending' or deleted_at IS NULL), which cuts size and write cost by orders of magnitude, and a partial UNIQUE index enforces uniqueness among active rows; in MySQL I emulate the unique case with a generated column that is NULL when inactive."

---

## 🔗 Related Questions
→ Q085 (Index on NULL values) | Q089 (Functional index) | Q084 (Covering index) | Q088 (When MySQL does NOT use an index)
