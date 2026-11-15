---

# Q113. Query Plan Caching — PgSQL Prepared Statements
# Category: Query Optimization
# Difficulty: ⭐⭐⭐ Hard
# DB: PostgreSQL (MySQL difference noted)

---

## ❓ Question
How do PostgreSQL prepared statements cache query plans? Explain custom vs generic plans, when a generic plan hurts on skewed data, and how `plan_cache_mode` controls it. Why does the same query sometimes get slower after the 6th execution?

---

## 💡 Quick Concept (2 lines only)
`PREPARE` parses once; for each `EXECUTE` Postgres picks a custom plan (built using the actual parameter value) for the first 5 runs, then may switch to a cached generic plan (parameter treated as unknown) if its estimated cost is not worse than the average custom cost.
हिंदी: पहले 5 बार हर value के लिए अलग custom plan बनता है, उसके बाद Postgres सस्ता लगे तो cached generic plan इस्तेमाल करता है, जो skewed data में बुरा हो सकता है।

---

## ✅ Answer / Solution

```sql
-- Verified on PGlite (PostgreSQL 18.6). Costs are planner estimates, stable for this data.

-- ============================================
-- SETUP (run this first)
-- ============================================

CREATE TABLE orders (
  id          SERIAL PRIMARY KEY,
  customer_id INT,
  status      TEXT,
  amount      NUMERIC(10,2)
);

-- Skewed: 20 'refunded' rows vs 19,980 'paid' rows
INSERT INTO orders (customer_id, status, amount)
SELECT g % 500, CASE WHEN g <= 20 THEN 'refunded' ELSE 'paid' END, g
FROM generate_series(1, 20000) g;

CREATE INDEX idx_orders_status ON orders (status);
ANALYZE orders;

-- ============================================
-- SOLUTION
-- ============================================

-- Step 1: prepare once (parse + rewrite are cached for the session)
PREPARE orders_by_status (text) AS
  SELECT count(*) FROM orders WHERE status = $1;

-- Step 2: executions 1-5 always get CUSTOM plans
EXPLAIN EXECUTE orders_by_status('refunded');   -- run it 6 times
EXPLAIN EXECUTE orders_by_status('paid');

-- Step 3: force the generic plan to see what the cache would use
SET plan_cache_mode = force_generic_plan;
EXPLAIN EXECUTE orders_by_status('refunded');
EXPLAIN EXECUTE orders_by_status('paid');
SET plan_cache_mode = auto;                     -- default

-- Step 4: inspect and clean up
SELECT name, generic_plans, custom_plans FROM pg_prepared_statements;
DEALLOCATE orders_by_status;

-- ============================================
-- EXPECTED OUTPUT
-- ============================================

-- 'refunded' x6 (custom plan, planner knows ~20 rows):
-- Aggregate  (cost=9.55..9.56 rows=1 width=8)
--   ->  Index Only Scan using idx_orders_status on orders  (cost=0.29..9.50 rows=20 width=0)
--         Index Cond: (status = 'refunded'::text)
--
-- 'paid' (custom plan, planner knows ~19,980 rows -> seq scan):
-- Aggregate  (cost=427.95..427.96 rows=1 width=8)
--   ->  Seq Scan on orders  (cost=0.00..378.00 rows=19980 width=0)
--         Filter: (status = 'paid'::text)
--
-- force_generic_plan (SAME plan for both values, value unknown -> $1, rows guessed 10000):
-- Aggregate  (cost=312.61..312.62 rows=1 width=8)
--   ->  Index Only Scan using idx_orders_status on orders  (cost=0.29..287.61 rows=10000 width=0)
--         Index Cond: (status = $1)
--
-- pg_prepared_statements after the above (EXPLAIN EXECUTE counts as an execution):
-- name             | generic_plans | custom_plans
-- orders_by_status | 2             | 7
-- (Exact counts depend on how many EXECUTEs you ran.)
```

---

## 🔍 Why This Works (3 lines max)
A custom plan can use the parameter against column statistics (`'refunded'` is rare, `'paid'` is common), a generic plan cannot, so it guesses an average. After 5 custom executions, Postgres compares the generic plan's cost to the average custom cost and caches the generic plan only if it is not clearly worse; on skewed data this estimate can be wrong.
हिंदी: Generic plan को parameter की value पता नहीं होती, इसलिए अंदाज़ा लगाता है; skewed data में यही गलत plan का कारण बनता है।

---

## ⚡ Alternative Solution

```sql
-- plan_cache_mode (PG12+): auto (default) | force_custom_plan | force_generic_plan
SET plan_cache_mode = force_custom_plan;     -- safest for skewed columns, replans each time
-- Per-role or per-database: ALTER ROLE app_user SET plan_cache_mode = 'force_custom_plan';

-- MySQL difference: server-side PREPARE/EXECUTE (verified on 9.1.0) saves parse cost
-- but there is NO plan cache; the optimizer re-optimizes with the bound value on each EXECUTE.
PREPARE find_cust FROM 'SELECT id, email FROM customers WHERE phone = ?';
SET @p = '9000000777';
EXECUTE find_cust USING @p;
DEALLOCATE PREPARE find_cust;
-- (placeholder is ? in MySQL, $1 in PostgreSQL)

-- Via drivers/pgbouncer: JDBC prepareThreshold=5 mirrors the same "5" idea;
-- PgBouncer transaction mode needs max_prepared_statements (1.21+) - see Q116. Not run.
```

---

## ⚠️ Common Mistake
```sql
-- ❌ Assuming a fast query stays fast forever: "it was 2 ms for the first 5 calls,
--    then 800 ms" -> the generic plan kicked in and uses an index/seq scan that is
--    wrong for the rare/common value you pass.
-- ❌ Using PREPARE with literals concatenated into the text -> no benefit, SQL injection risk.
-- ❌ Expecting prepared statements to be shared across connections: they are per-session,
--    so with a transaction pooler they can vanish or error ("prepared statement does not exist").
-- ✅ Diagnose with EXPLAIN (ANALYZE) EXECUTE ...; fix with plan_cache_mode = force_custom_plan
--    or better statistics (ALTER TABLE ... SET STATISTICS), not by removing parameters.
```

---

## 🎯 Interview Tip (1 line)
Say: "Prepared statements save parse/plan time but Postgres flips from custom to generic plans after five runs; with skewed columns I look for the sudden latency cliff and set plan_cache_mode=force_custom_plan, and I remember poolers in transaction mode break session-level prepares."

---

## 🔗 Related Questions
→ Q114 (Statistics / ANALYZE) | Q116 (PgBouncer) | Q112 (pg_stat_statements) | Q109 (Slow query diagnosis)
