---

# Q104. Using temporary — When + How to Fix
# Category: Query Optimization
# Difficulty: ⭐⭐ Medium
# DB: Both (MySQL 8.0+ | PostgreSQL)

---

## ❓ Question
`EXPLAIN` shows `Using temporary` for `GROUP BY` / `DISTINCT` queries. Why does MySQL build a temporary table, how do you avoid it, and how does PostgreSQL handle the same queries?

---

## 💡 Quick Concept (2 lines only)
MySQL materializes an internal temp table when it cannot get rows already grouped/distinct via an index (GROUP BY on an unindexed column, DISTINCT, ORDER BY on an aggregate, UNION). An index on the grouping columns lets it stream groups; PostgreSQL uses HashAggregate or Sort + GroupAggregate instead.
हिंदी: Group करने के लिए index का क्रम न मिले तो MySQL temp table बनाता है; GROUP BY column पर index लगाने से यह हट जाता है।

---

## ✅ Answer / Solution

```sql
-- ============================================
-- SETUP — MySQL (verified on MySQL 9.1.0)
-- ============================================

CREATE TABLE orders (
  id          INT PRIMARY KEY AUTO_INCREMENT,
  customer_id INT NOT NULL,
  status      VARCHAR(20) NOT NULL,
  amount      DECIMAL(10,2) NOT NULL,
  created_at  DATETIME NOT NULL
);
SET SESSION cte_max_recursion_depth = 100000;
INSERT INTO orders (customer_id, status, amount, created_at)
WITH RECURSIVE n AS (SELECT 1 i UNION ALL SELECT i+1 FROM n WHERE i < 100000)
SELECT i % 500 + 1, ELT(i % 4 + 1, 'delivered','shipped','pending','cancelled'),
       10 + (i % 490), TIMESTAMP('2024-01-01') + INTERVAL i MINUTE FROM n;
ANALYZE TABLE orders;

-- ============================================
-- SOLUTION
-- ============================================

-- Step 1: no index on the grouping column
EXPLAIN SELECT customer_id, COUNT(*), SUM(amount) FROM orders GROUP BY customer_id;
EXPLAIN SELECT DISTINCT status FROM orders;
EXPLAIN ANALYZE SELECT customer_id, SUM(amount) s FROM orders GROUP BY customer_id;

-- Step 2: index on (grouping column, aggregated column) -> ordered, covering
ALTER TABLE orders ADD KEY idx_customer_amount (customer_id, amount);
ANALYZE TABLE orders;
EXPLAIN SELECT customer_id, COUNT(*), SUM(amount) FROM orders GROUP BY customer_id;
EXPLAIN ANALYZE SELECT customer_id, SUM(amount) s FROM orders GROUP BY customer_id;

-- Step 3: DISTINCT / low-cardinality group column -> loose index scan
ALTER TABLE orders ADD KEY idx_status (status);
ANALYZE TABLE orders;
EXPLAIN SELECT DISTINCT status FROM orders;

-- Step 4: temp table still needed when ordering by the aggregate
EXPLAIN SELECT customer_id, SUM(amount) s FROM orders GROUP BY customer_id ORDER BY s DESC LIMIT 5;

-- ============================================
-- EXPECTED OUTPUT (real, MySQL 9.1.0)
-- ============================================
-- Step 1a: type=ALL, rows=99900, Extra: Using temporary
-- Step 1b: type=ALL, rows=99900, Extra: Using temporary
-- Step 1c ANALYZE: Table scan on <temporary> rows=500 <- Aggregate using temporary table (30.4 ms)
--                  <- Table scan on orders rows=100000
-- Step 2 : type=index, key=idx_customer_amount, rows=99900, Extra: Using index
--          ANALYZE: Group aggregate: sum(amount) (15.9 ms) <- Covering index scan ... rows=100000
-- Step 3 : type=range, key=idx_status, rows=4, Extra: Using index for group-by     <- loose index scan
-- Step 4 : Extra: Using index; Using temporary; Using filesort    <- ORDER BY an aggregate cannot use an index
```

```sql
-- ============================================
-- POSTGRESQL (verified on PGlite = PostgreSQL 18.6)
-- ============================================
-- Same table via generate_series:
EXPLAIN (ANALYZE, COSTS OFF, TIMING OFF) SELECT customer_id, COUNT(*), SUM(amount) FROM orders GROUP BY customer_id;
-- HashAggregate  Group Key: customer_id  Batches: 1  Memory Usage: 189kB  -> Seq Scan  (no temp table concept)
SET enable_hashagg = off;
-- GroupAggregate -> Sort (Sort Key: customer_id) -> Seq Scan
CREATE INDEX idx_customer_amount ON orders(customer_id) INCLUDE (amount);  ANALYZE orders;  VACUUM orders;
-- GroupAggregate -> Index Only Scan using idx_customer_amount     (sorted input, no Sort node)
RESET enable_hashagg;
-- with hashagg back on, PostgreSQL still preferred HashAggregate + Seq Scan: for 500 groups it is cheaper.
```

---

## 🔍 Why This Works (3 lines max)
Grouping needs equal keys adjacent; an index on the grouping column delivers that for free so MySQL aggregates on the fly (and covering columns avoid table lookups). The 4-value DISTINCT becomes a "loose index scan" that hops between distinct keys instead of reading 100k rows.
हिंदी: Index में same keys पास-पास होते हैं, इसलिए GROUP BY बिना temp table के चल जाता है।

---

## ⚡ Alternative Solution

```sql
-- Pre-aggregate in a summary table (best for dashboards over huge tables):
CREATE TABLE daily_customer_sales (day DATE, customer_id INT, total DECIMAL(14,2), PRIMARY KEY (day, customer_id));
-- MySQL: temp tables are in-memory (TempTable engine) until temptable_max_ram (1GB default), then spill to disk.
SHOW GLOBAL STATUS LIKE 'Created_tmp%tables';        -- Created_tmp_disk_tables climbing = tune/fix queries
-- PostgreSQL: increase work_mem for hash aggregates; check "Batches: >1" / "Disk:" in EXPLAIN ANALYZE.
```

---

## ⚠️ Common Mistake

```sql
-- ❌ "Using temporary" = always bad: a 500-group aggregate over 100k rows took ~30 ms; a covering index scan 16 ms
-- ❌ Index only on (customer_id) when the query also needs amount -> still a lookup per row
-- ❌ GROUP BY + ORDER BY different columns/aggregates -> temp table + filesort again (verified Step 4)
-- ✅ Index (group cols, then aggregated cols); remove redundant ORDER BY; summarize when data is huge.
```

---

## 🎯 Interview Tip (1 line)
Say: "Using temporary means the grouping isn't satisfied by an index order; I fix it with an index on the GROUP BY columns (covering the aggregates), and I watch Created_tmp_disk_tables rather than the flag itself."

---

## 🔗 Related Questions
→ Q103 (Using filesort) | Q084 (Covering index) | Q020 (UNION vs UNION ALL) | Q114 (Statistics / ANALYZE)
