---

# Q173. MySQL 8.0 Invisible Indexes
# Category: MySQL Specific
# Difficulty: ⭐⭐ Medium
# DB: MySQL (8.0+)

---

## ❓ Question
You suspect an index on `customers(city)` is unused and want to drop it, but dropping and rebuilding a big index is risky. How do invisible indexes let you test the removal safely? How do you verify it, and what are the limits?

---

## 💡 Quick Concept (2 lines only)
An invisible index is still maintained on every write but the optimizer ignores it. Flip it back to VISIBLE instantly (metadata-only) if queries regress — no rebuild.
हिंदी: Invisible index maintain होता रहता है पर optimizer उसे use नहीं करता, इसलिए drop से पहले safe test हो जाता है।

---

## ✅ Answer / Solution

```sql
-- ============================================
-- SETUP (verified on MySQL 9.1.0)
-- ============================================

CREATE TABLE customers (
  id         INT PRIMARY KEY,
  email      VARCHAR(100),
  city       VARCHAR(50),
  created_at DATETIME
);

-- 5000 rows via recursive CTE (default depth limit is 1000, so raise it)
SET SESSION cte_max_recursion_depth = 10000;
INSERT INTO customers
WITH RECURSIVE n AS (SELECT 1 AS i UNION ALL SELECT i + 1 FROM n WHERE i < 5000)
SELECT i, CONCAT('u', i, '@x.com'), CONCAT('city', i % 50), NOW() FROM n;

CREATE INDEX idx_city ON customers(city);
ANALYZE TABLE customers;

-- ============================================
-- SOLUTION
-- ============================================

-- Step 1: hide the index from the optimizer
ALTER TABLE customers ALTER INDEX idx_city INVISIBLE;

-- Step 2: check the plan -> full table scan now
EXPLAIN SELECT * FROM customers WHERE city = 'city7';
-- id | select_type | table     | type | possible_keys | key  | rows | filtered | Extra
-- 1  | SIMPLE      | customers | ALL  | NULL          | NULL | 5000 | 2.00     | Using where

-- Step 3: this one session can still "see" it (default is use_invisible_indexes=off)
SET SESSION optimizer_switch = 'use_invisible_indexes=on';
EXPLAIN SELECT * FROM customers WHERE city = 'city7';
-- 1  | SIMPLE      | customers | ref  | idx_city      | idx_city | rows 100 | 100.00 | NULL
SET SESSION optimizer_switch = 'use_invisible_indexes=off';

-- Step 4a: queries regressed? bring it back instantly
ALTER TABLE customers ALTER INDEX idx_city VISIBLE;
-- Step 4b: no regression after a full business cycle? then really drop it
-- DROP INDEX idx_city ON customers;

-- Inspect state
SELECT index_name, is_visible
FROM information_schema.statistics
WHERE table_schema = DATABASE() AND table_name = 'customers';
-- (with idx_city INVISIBLE; the Visible column of SHOW INDEX shows YES/NO as well)
-- INDEX_NAME | IS_VISIBLE
-- idx_city   | NO
-- PRIMARY    | YES

-- Create an index hidden from day one (test a NEW index without affecting plans):
CREATE INDEX idx_email ON customers(email) INVISIBLE;
```

---

## 🔍 Why This Works (3 lines max)
Visibility is just a flag in the data dictionary the optimizer checks; the B-tree is still updated on INSERT/UPDATE/DELETE so it is current when re-enabled. Toggling is a metadata-only change, unlike DROP + CREATE which rebuilds.
हिंदी: Visibility सिर्फ एक flag है, इसलिए ON/OFF तुरंत होता है, rebuild नहीं लगता।

---

## ⚡ Alternative Solution

```sql
-- PostgreSQL has no INVISIBLE indexes. Options:
--  * Test in a transaction:  BEGIN; DROP INDEX idx_city; EXPLAIN ...; ROLLBACK;
--    (takes ACCESS EXCLUSIVE lock on the table - risky on production)
--  * Check usage: SELECT relname, indexrelname, idx_scan FROM pg_stat_user_indexes;
--  * Hypothetical indexes via the hypopg extension (not run here).
-- MySQL: find unused indexes first via sys schema:
SELECT * FROM sys.schema_unused_indexes;   -- needs performance_schema; stats reset on restart!
```

---

## ⚠️ Common Mistake

```sql
-- ❌ Trying to hide the primary key (verified):
ALTER TABLE customers ALTER INDEX `PRIMARY` INVISIBLE;
-- ERROR 3522 (HY000): A primary key index cannot be invisible
-- (Also: an invisible index still enforces UNIQUE constraints and still costs write I/O.)

-- ❌ Assuming "invisible = free": it still slows writes and uses disk
-- ✅ Invisible is a TRIAL state: decide and drop, don't leave it forever

-- ❌ Forgetting FK needs: an index required by a foreign key can't be dropped, but can be hidden -
--    FK checks may silently become table scans / lock more rows
```

---

## 🎯 Interview Tip (1 line)
Say: "Before dropping an index I make it invisible, watch p95 latency and the slow log for a full cycle (month-end reports!), then drop; rollback is a one-second metadata change versus an hours-long rebuild."

---

## 🔗 Related Questions
→ Q178 (Slow query log analysis) | Q180 (max_connections) | Q172 (MySQL 8.0 CTEs)
