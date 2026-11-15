---

# Q095. Index Hint — FORCE INDEX, USE INDEX
# Category: Indexes
# Difficulty: ⭐⭐ Medium
# DB: MySQL (PostgreSQL has no index hints)

---

## ❓ Question
The optimizer picks an index you think is wrong for a query on `orders`. How do you override it with `USE INDEX`, `FORCE INDEX`, `IGNORE INDEX`? When is that justified, and what is the PostgreSQL equivalent?

---

## 💡 Quick Concept (2 lines only)
Index hints tell MySQL's optimizer which indexes to consider: USE = "only consider these", FORCE = "table scan is treated as very expensive, use this", IGNORE = "never consider this". PostgreSQL has no hints; you fix statistics, add an index, or tweak `enable_*` / `pg_hint_plan` (extension).
हिंदी: Index hint optimizer को बताता है कौन सा index use करना है; PostgreSQL में hints नहीं होते, वहाँ statistics/index ठीक करते हैं।

---

## ✅ Answer / Solution

```sql
-- ============================================
-- SETUP (run this first) — verified on MySQL 9.1.0
-- ============================================

CREATE TABLE orders (
  id          INT PRIMARY KEY AUTO_INCREMENT,
  customer_id INT NOT NULL,
  status      VARCHAR(20) NOT NULL,
  amount      DECIMAL(10,2) NOT NULL,
  created_at  DATETIME NOT NULL,
  KEY idx_status   (status),
  KEY idx_created  (created_at),
  KEY idx_customer (customer_id)
) ENGINE=InnoDB;

SET SESSION cte_max_recursion_depth = 20000;
INSERT INTO orders (customer_id, status, amount, created_at)
WITH RECURSIVE n AS (SELECT 1 AS i UNION ALL SELECT i+1 FROM n WHERE i < 20000)
SELECT i % 500 + 1,
       CASE WHEN i % 100 < 70 THEN 'delivered' WHEN i % 100 < 95 THEN 'shipped' ELSE 'pending' END,
       10 + (i % 90),
       TIMESTAMP('2024-01-01') + INTERVAL i MINUTE
FROM n;
ANALYZE TABLE orders;   -- refresh statistics so EXPLAIN is stable

-- ============================================
-- SOLUTION
-- ============================================

-- Step 1: baseline — let the optimizer choose
EXPLAIN SELECT * FROM orders
WHERE status = 'delivered' AND created_at >= '2024-01-05' AND created_at < '2024-01-06';

-- Step 2: FORCE INDEX on the (worse) status index
EXPLAIN SELECT * FROM orders FORCE INDEX (idx_status)
WHERE status = 'delivered' AND created_at >= '2024-01-05' AND created_at < '2024-01-06';

-- Step 3: USE INDEX / IGNORE INDEX
EXPLAIN SELECT * FROM orders USE INDEX (idx_created)
WHERE status = 'delivered' AND created_at >= '2024-01-05' AND created_at < '2024-01-06';
EXPLAIN SELECT * FROM orders IGNORE INDEX (idx_created)
WHERE status = 'delivered' AND created_at >= '2024-01-05' AND created_at < '2024-01-06';

-- Step 4: scope a hint to one clause only (JOIN / ORDER BY / GROUP BY)
EXPLAIN SELECT * FROM orders FORCE INDEX FOR ORDER BY (idx_created)
WHERE status = 'pending' ORDER BY created_at LIMIT 5;

-- ============================================
-- EXPECTED OUTPUT (real, MySQL 9.1.0; rows are optimizer estimates)
-- ============================================

-- Step 1 (baseline):
-- type  | possible_keys           | key         | rows | filtered | Extra
-- range | idx_status,idx_created  | idx_created | 1440 | 50.00    | Using index condition; Using where
--
-- Step 2 (FORCE INDEX idx_status): optimizer obeys, reads many more rows
-- ref   | idx_status              | idx_status  | 6672 | 11.11    | Using where
--
-- Step 3a (USE INDEX idx_created):
-- range | idx_created             | idx_created | 1440 | 33.33    | Using index condition; Using where
-- Step 3b (IGNORE INDEX idx_created): falls back to the weaker index
-- ref   | idx_status              | idx_status  | 10008| 11.11    | Using where
--
-- Step 4: key = idx_created, type = index, rows = 100 (same plan the optimizer chose on its own)
-- Naming a nonexistent index:
-- ERROR 1176 (42000): Key 'idx_nope' doesn't exist in table 'orders'
```

---

## 🔍 Why This Works (3 lines max)
USE INDEX narrows the candidate list but the optimizer may still scan; FORCE INDEX makes a table scan "infinitely costly" so the named index wins whenever it is usable. In Step 2 the forced plan reads ~4.6x more rows than the default - proof that hints can make things worse when data shifts.
हिंदी: FORCE INDEX optimizer को मजबूर करता है, पर data बदलने पर वही hint query को धीमा भी कर सकता है।

---

## ⚡ Alternative Solution

```sql
-- Prefer fixing the cause over hinting:
ANALYZE TABLE orders;                                   -- MySQL: refresh stats
ALTER TABLE orders ADD KEY idx_status_created (status, created_at);  -- right composite index

-- MySQL 8.0+: optimizer hints (comment syntax, per query, survives index renames less well)
SELECT /*+ INDEX(orders idx_created) */ * FROM orders WHERE created_at >= '2024-01-05';
SELECT /*+ NO_INDEX(orders idx_status) */ * FROM orders WHERE status = 'pending';

-- PostgreSQL: no USE/FORCE INDEX. Options:
ANALYZE orders;                                         -- fix stale stats first
SET enable_seqscan = off;                               -- session-level, DIAGNOSTIC only
-- or the pg_hint_plan extension:  /*+ IndexScan(orders idx_created) */  (not core, not run here)
```

---

## ⚠️ Common Mistake

```sql
-- ❌ Hardcoding FORCE INDEX in application SQL "because it was faster once"
SELECT * FROM orders FORCE INDEX (idx_status) WHERE status = 'delivered' AND created_at >= '2024-01-05';
-- Data distribution changes, index is dropped/renamed -> error 1176 or a silent slow plan.

-- ❌ Expecting USE INDEX to guarantee usage: optimizer may still choose a full scan
-- ✅ Diagnose first (EXPLAIN, ANALYZE TABLE, histograms), hint last, and leave a comment + monitoring.
```

---

## 🎯 Interview Tip (1 line)
Say: "Hints are a last resort - I first run ANALYZE TABLE / add the correct composite index, and if I must hint I prefer 8.0 optimizer hints on one query, documented, and revisit them when data shape changes; Postgres deliberately has no hints."

---

## 🔗 Related Questions
→ Q083 (Composite index order) | Q086 (EXPLAIN output) | Q088 (When MySQL doesn't use an index) | Q101 (EXPLAIN key columns)
