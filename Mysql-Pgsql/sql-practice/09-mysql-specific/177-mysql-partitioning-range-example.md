---

# Q177. MySQL Partitioning — RANGE Example
# Category: MySQL Specific
# Difficulty: ⭐⭐⭐ Hard
# DB: MySQL (8.0+ / 9.x, InnoDB)

---

## ❓ Question
Partition an `orders` table by year using RANGE partitioning. Show partition pruning in EXPLAIN, how to drop old data instantly, how to add a new year, and the restrictions (primary key rule, no foreign keys).

---

## 💡 Quick Concept (2 lines only)
RANGE partitioning splits one logical table into physical sub-tables by value ranges; the optimizer skips partitions that cannot match (pruning), and `DROP PARTITION` removes a whole year instantly instead of a slow `DELETE`. Every unique key (including the PK) must contain the partitioning column.
हिंदी: RANGE partition table को value ranges में बाँटता है; pruning से बेकार partitions skip होते हैं और पुराना data DROP PARTITION से तुरंत हटता है।

---

## ✅ Answer / Solution

```sql
-- ============================================
-- SETUP (verified on MySQL 9.1.0)
-- ============================================

CREATE TABLE orders_part (
  id          BIGINT NOT NULL AUTO_INCREMENT,
  customer_id INT NOT NULL,
  amount      DECIMAL(10,2) NOT NULL,
  created_at  DATE NOT NULL,
  PRIMARY KEY (id, created_at)          -- partition column MUST be part of every unique key
) PARTITION BY RANGE (YEAR(created_at)) (
  PARTITION p2022 VALUES LESS THAN (2023),
  PARTITION p2023 VALUES LESS THAN (2024),
  PARTITION p2024 VALUES LESS THAN (2025),
  PARTITION pmax  VALUES LESS THAN MAXVALUE   -- catch-all so inserts never fail
);

INSERT INTO orders_part (customer_id, amount, created_at) VALUES
 (1,100.00,'2022-03-10'),(2,250.50,'2022-11-02'),(1,75.00,'2023-01-15'),
 (3,310.00,'2023-06-30'),(2,40.00,'2023-12-31'),(4,500.00,'2024-02-14'),
 (1,60.00,'2024-08-08'),(5,900.00,'2025-01-05');

-- ============================================
-- SOLUTION
-- ============================================

-- Step 1: where did the rows land?
SELECT PARTITION_NAME, PARTITION_DESCRIPTION, TABLE_ROWS
FROM information_schema.PARTITIONS
WHERE TABLE_SCHEMA = 't' AND TABLE_NAME = 'orders_part'
ORDER BY PARTITION_ORDINAL_POSITION;

-- Result (real; TABLE_ROWS is an estimate):
-- PARTITION_NAME | PARTITION_DESCRIPTION | TABLE_ROWS
-- p2022          | 2023                  | 2
-- p2023          | 2024                  | 3
-- p2024          | 2025                  | 2
-- pmax           | MAXVALUE              | 1

-- Step 2: pruning with a plain range on the column
EXPLAIN SELECT * FROM orders_part
WHERE created_at >= '2023-01-01' AND created_at < '2024-01-01'\G
-- partitions: p2023     <- only ONE partition touched
-- type: ALL, rows: 3    <- full scan INSIDE that partition (no secondary index yet)

-- Step 3: the same logic written with the function
EXPLAIN SELECT * FROM orders_part WHERE YEAR(created_at) = 2023\G
-- partitions: p2022,p2023,p2024,pmax   <- NO pruning on MySQL 9.1.0 (observed)
-- Always filter on the raw column with a range, not YEAR(col) = x.

-- Step 4: retire a whole year instantly (metadata + file drop, no row-by-row delete)
ALTER TABLE orders_part DROP PARTITION p2022;
SELECT COUNT(*) FROM orders_part;
-- COUNT(*) = 6   (the 2 rows from 2022 are gone)

-- Step 5: carve a new year out of the catch-all partition
ALTER TABLE orders_part REORGANIZE PARTITION pmax INTO (
  PARTITION p2025 VALUES LESS THAN (2026),
  PARTITION pmax  VALUES LESS THAN MAXVALUE
);
SELECT PARTITION_NAME, TABLE_ROWS FROM information_schema.PARTITIONS
WHERE TABLE_SCHEMA='t' AND TABLE_NAME='orders_part' ORDER BY PARTITION_ORDINAL_POSITION;
-- p2023 | p2024 | p2025 | pmax   <- new layout (TABLE_ROWS showed 0 right after reorganize:
--                                    stale stats; run ANALYZE TABLE to refresh. Data itself was intact.)

-- ============================================
-- RESTRICTION: PK must include the partition column
-- ============================================
CREATE TABLE bad (id INT PRIMARY KEY, d DATE)
PARTITION BY RANGE (YEAR(d)) (PARTITION p0 VALUES LESS THAN (2030));
-- ERROR 1503 (HY000): A PRIMARY KEY must include all columns in the table's partitioning function
```

---

## 🔍 Why This Works (3 lines max)
Each partition is its own InnoDB tablespace segment, so dropping or truncating one is a cheap file operation and queries with a range on the partition expression read only the matching partitions. The PK-must-contain-the-partition-key rule exists because uniqueness is enforced per partition, not globally. Partitioning helps data lifecycle and scans; it does not make every query faster.
हिंदी: हर partition अलग segment है, इसलिए DROP सस्ता है; uniqueness per-partition चेक होती है, इसलिए PK में partition column ज़रूरी है।

---

## ⚡ Alternative Solution

```sql
-- RANGE COLUMNS: partition directly on DATE (no function -> reliable pruning, readable bounds)
CREATE TABLE orders_rc (
  id BIGINT NOT NULL AUTO_INCREMENT, created_at DATE NOT NULL, amount DECIMAL(10,2),
  PRIMARY KEY (id, created_at)
) PARTITION BY RANGE COLUMNS (created_at) (
  PARTITION p2024q1 VALUES LESS THAN ('2024-04-01'),
  PARTITION p2024q2 VALUES LESS THAN ('2024-07-01'),
  PARTITION pmax    VALUES LESS THAN (MAXVALUE)
);
-- Not executed in my run; same engine rules as above.

-- Query only specific partitions explicitly:
SELECT * FROM orders_part PARTITION (p2023, p2024);

-- PostgreSQL equivalent (declarative, Q189):
--   CREATE TABLE orders (...) PARTITION BY RANGE (created_at);
--   CREATE TABLE orders_2024 PARTITION OF orders FOR VALUES FROM ('2024-01-01') TO ('2025-01-01');
-- Differences: PgSQL partitions are real tables (can ATTACH/DETACH), supports FKs; MySQL InnoDB partitioned tables cannot have foreign keys.
```

---

## ⚠️ Common Mistake

```sql
-- ❌ Expecting partitioning to speed up queries that do not filter on the partition key
SELECT * FROM orders_part WHERE customer_id = 1;   -- scans ALL partitions
-- ✅ Add a secondary index (customer_id) AND/OR filter on created_at too.

-- ❌ Wrapping the column in a function in WHERE
WHERE YEAR(created_at) = 2023       -- observed: all 4 partitions scanned
-- ✅ WHERE created_at >= '2023-01-01' AND created_at < '2024-01-01'   -- 1 partition

-- ❌ No MAXVALUE partition -> INSERT of a 2026 row fails with
--    ERROR 1526 (HY000): Table has no partition for value 2031   (verified)
-- ✅ Keep a catch-all and REORGANIZE it before the new year arrives (cron job).

-- ❌ Planning foreign keys on a partitioned InnoDB table -> not supported in MySQL.
```

---

## 🎯 Interview Tip (1 line)
Say: "I partition for data lifecycle (drop a month in milliseconds) and pruning, always filter on the raw partition column, keep a MAXVALUE partition, and accept that the PK must include the key and FKs are unsupported; otherwise a good index beats partitioning."

---

## 🔗 Related Questions
→ Q189 (PgSQL declarative partitioning) | Q178 (Slow query log) | Q162 (Buffer pool) | Q241 (Sharding)
