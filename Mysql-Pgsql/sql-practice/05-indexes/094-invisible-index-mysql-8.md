---

# Q094. Invisible Index (MySQL 8+)
# Category: Indexes
# Difficulty: ⭐⭐ Medium
# DB: MySQL 8.0+ (PostgreSQL workaround shown)

---

## ❓ Question
How can you test whether an index is safe to drop without actually dropping it? Explain MySQL 8 invisible indexes, how to toggle and test them, and what PostgreSQL offers instead.

---

## 💡 Quick Concept (2 lines only)
An invisible index is still maintained on every write but ignored by the optimizer, so you can "soft-drop" it, watch for regressions, and re-enable it instantly (a metadata-only change) instead of a slow rebuild. PostgreSQL has no such feature.
हिंदी: Invisible index लिखते समय update होता रहता है पर optimizer उसे ignore करता है; drop से पहले सुरक्षित test के लिए, और वापस VISIBLE करना तुरंत होता है।

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
  amount      DECIMAL(10,2),
  INDEX idx_customer (customer_id),
  INDEX idx_status   (status)
);

INSERT INTO orders
SELECT n, 1 + n % 500, ELT(1 + n % 3, 'pending', 'shipped', 'delivered'), n % 1000
FROM (WITH RECURSIVE s AS (SELECT 1 AS n UNION ALL SELECT n + 1 FROM s WHERE n < 20000)
      SELECT n FROM s) x;
ANALYZE TABLE orders;

-- ============================================
-- SOLUTION
-- ============================================

-- Step 1: baseline - optimizer uses the index
EXPLAIN SELECT * FROM orders WHERE customer_id = 42;

-- Step 2: hide it (instant, metadata only; writes still maintain it)
ALTER TABLE orders ALTER INDEX idx_customer INVISIBLE;
SELECT index_name, is_visible FROM information_schema.statistics
WHERE table_name = 'orders' AND index_name LIKE 'idx%';

-- Step 3: same query without the index
EXPLAIN SELECT * FROM orders WHERE customer_id = 42;

-- Step 4: session-level override to test with hidden indexes
SET SESSION optimizer_switch = 'use_invisible_indexes=on';
EXPLAIN SELECT * FROM orders WHERE customer_id = 42;
SET SESSION optimizer_switch = 'use_invisible_indexes=off';

-- Step 5: roll back instantly if queries got slower (or DROP INDEX if nothing complained)
ALTER TABLE orders ALTER INDEX idx_customer VISIBLE;

-- Create a new index hidden first, enable once validated:
CREATE INDEX idx_amount ON orders (amount) INVISIBLE;

-- ============================================
-- EXPECTED OUTPUT (verified on MySQL 9.1)
-- ============================================

-- Step 1: type=ref  key=idx_customer rows=40
-- Step 2: index_name   | is_visible
--         idx_customer | NO
--         idx_status   | YES
-- Step 3: type=ALL  key=NULL rows=19653      <- full table scan; hint: the app would now be slow
-- Step 4: type=ref  key=idx_customer rows=40 <- optimizer_switch makes it usable again (this session only)
-- Step 5: EXPLAIN again -> type=ref key=idx_customer
-- SHOW CREATE TABLE shows:  KEY `idx_amount` (`amount`) /*!80000 INVISIBLE */
```

---

## 🔍 Why This Works (3 lines max)
The index stays in the storage engine and is updated on every write, but the optimizer excludes it from plan choices, so dropping and recreating a big index (hours on a large table) is replaced by a metadata flip. Side effects of keeping it: write overhead and disk space remain until you really drop it.
हिंदी: Index मौजूद रहता है और अपडेट होता है, पर optimizer उसे नहीं चुनता; इसलिए drop की जगह सिर्फ metadata बदलकर सुरक्षित test होता है।

---

## ⚡ Alternative Solution

```sql
-- Find drop candidates first (MySQL, sys schema; needs performance_schema usage stats since last restart):
SELECT * FROM sys.schema_unused_indexes WHERE object_schema = 'your_db';
-- (on the fresh test server it listed idx_customer, idx_status and idx_amount because nothing had run yet - judge only
--  after a representative production period)

-- Constraints (verified): FORCE INDEX on an invisible index fails:
--   ERROR 1176 (42000): Key 'idx_customer' doesn't exist in table 'orders'
-- The PRIMARY KEY cannot be made invisible (verified): ERROR 3522 (HY000): A primary key index cannot be invisible
-- An invisible UNIQUE index still enforces uniqueness (visibility affects only the optimizer; documented, not tested here).

-- PostgreSQL: no INVISIBLE keyword. Options:
-- 1) DDL is transactional - test the plan with the index dropped, then roll back (verified on PGlite):
BEGIN;
DROP INDEX idx_customer;
EXPLAIN SELECT * FROM orders WHERE customer_id = 42;     -- Seq Scan on orders (Filter: customer_id = 42)
ROLLBACK;                                                 -- index is back (EXPLAIN again -> Bitmap Index Scan on idx_customer)
--    Caveat: DROP INDEX takes an ACCESS EXCLUSIVE lock until ROLLBACK - do this on a staging copy, not a busy primary.
-- 2) Check usage: SELECT relname, indexrelname, idx_scan FROM pg_stat_user_indexes ORDER BY idx_scan;  (idx_scan = 0 over a long window)
-- 3) HypoPG extension offers hypothetical (what-if) indexes, the opposite direction - extension, not run here.
```

---

## ⚠️ Common Mistake

```sql
-- ❌ Wrong: assuming an invisible index is "free" - writes still maintain it (INSERT/UPDATE cost + disk).
-- ✅ Use it as a short observation window, then DROP INDEX or make VISIBLE again.

-- ❌ Wrong: testing for a few minutes on a quiet system and dropping
-- Month-end reports, batch jobs and rarely-run queries may depend on the index.
-- ✅ Keep it invisible across a full business cycle and review slow logs / performance_schema.

-- ❌ Wrong: using FORCE INDEX / index hints in app code and then hiding that index -> those queries error with 1176.
-- ✅ grep the code base and ORM hints before hiding.

-- ❌ Wrong: relying on sys.schema_unused_indexes right after a restart (counters reset).
```

---

## 🎯 Interview Tip (1 line)
Say: "Before dropping a suspicious index in MySQL 8 I mark it INVISIBLE, watch latency and slow logs over a full business cycle, flip it back instantly if anything regresses, and only then DROP it; in PostgreSQL I'd check pg_stat_user_indexes.idx_scan and test the drop inside a rolled-back transaction on a replica or staging."

---

## 🔗 Related Questions
→ Q081 (B-Tree index internals) | Q084 (Covering index) | Q086 (EXPLAIN output) | Q088 (When MySQL does NOT use an index)
