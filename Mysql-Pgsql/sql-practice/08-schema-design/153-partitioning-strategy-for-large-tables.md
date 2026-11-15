---

# Q153. Partitioning Strategy for Large Tables
# Category: Schema Design
# Difficulty: ⭐⭐⭐ Hard
# DB: Both (MySQL 8.0+ | PostgreSQL) — verified on MySQL 9.1 and PGlite

---

## ❓ Question
An `orders_log` table grows 50M rows a month. How do you partition it (range by date), how do you confirm partition pruning works, how do you drop old data, and what restrictions does partitioning impose on keys?

---

## 💡 Quick Concept (2 lines only)
Partitioning splits one logical table into physical pieces by RANGE / LIST / HASH; the optimizer skips partitions that cannot match (pruning). Its biggest win is cheap retention (drop a partition), not magic query speed.
हिंदी: Partitioning = एक बड़ी table को date जैसे key से टुकड़ों में बांटना; pruning से बेकार टुकड़े skip होते हैं, और पुराना data partition drop से हटता है।

---

## ✅ Answer / Solution

```sql
-- ============================================
-- SETUP (MySQL)
-- ============================================

CREATE TABLE orders_log (
  id         BIGINT NOT NULL AUTO_INCREMENT,
  user_id    INT NOT NULL,
  amount     DECIMAL(10,2) NOT NULL,
  created_at DATE NOT NULL,
  PRIMARY KEY (id, created_at)          -- partition column MUST be part of every unique key
)
PARTITION BY RANGE COLUMNS (created_at) (
  PARTITION p2024_01 VALUES LESS THAN ('2024-02-01'),
  PARTITION p2024_02 VALUES LESS THAN ('2024-03-01'),
  PARTITION p2024_03 VALUES LESS THAN ('2024-04-01'),
  PARTITION pmax     VALUES LESS THAN (MAXVALUE)    -- catch-all so inserts never fail
);

INSERT INTO orders_log (user_id, amount, created_at) VALUES
  (1, 100, '2024-01-10'), (2, 250, '2024-01-25'), (1, 75, '2024-02-05'),
  (3, 300, '2024-02-20'), (2, 50, '2024-03-15'), (4, 500, '2024-05-01');

-- ============================================
-- SOLUTION
-- ============================================

-- Step 1: where did the rows land?
SELECT PARTITION_NAME, TABLE_ROWS FROM information_schema.PARTITIONS
WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'orders_log' ORDER BY PARTITION_ORDINAL_POSITION;
-- p2024_01 | 2
-- p2024_02 | 2
-- p2024_03 | 1
-- pmax     | 1        (TABLE_ROWS is an estimate; right after DDL it can show 0 until stats refresh)

-- Step 2: pruning — filter on the partition key
EXPLAIN SELECT * FROM orders_log WHERE created_at >= '2024-02-01' AND created_at < '2024-03-01';
-- partitions = p2024_02   (only 1 of 4 touched)   type=ALL on that partition, rows=2

-- No partition key in WHERE -> every partition scanned
EXPLAIN SELECT * FROM orders_log WHERE user_id = 1;
-- partitions = p2024_01,p2024_02,p2024_03,pmax

-- Step 3: key restriction
CREATE TABLE bad_part (id BIGINT PRIMARY KEY, created_at DATE NOT NULL)
PARTITION BY RANGE COLUMNS (created_at) (PARTITION p0 VALUES LESS THAN (MAXVALUE));
-- ERROR 1503: A PRIMARY KEY must include all columns in the table's partitioning function

-- Step 4: retention — instant, no row-by-row delete
ALTER TABLE orders_log DROP PARTITION p2024_01;
SELECT COUNT(*) AS rows_left FROM orders_log;      -- 4

-- Step 5: add the next month by splitting the catch-all partition
ALTER TABLE orders_log REORGANIZE PARTITION pmax INTO (
  PARTITION p2024_04 VALUES LESS THAN ('2024-05-01'),
  PARTITION pmax     VALUES LESS THAN (MAXVALUE)
);
SELECT COUNT(*) AS in_p2024_02 FROM orders_log PARTITION (p2024_02);   -- 2
SELECT COUNT(*) AS in_pmax     FROM orders_log PARTITION (pmax);       -- 1  (the May row)
```

---

## 🔍 Why This Works (3 lines max)
The optimizer maps the WHERE range on `created_at` to partition boundaries and skips the rest, so scans and index trees stay small. DROP/DETACH PARTITION removes a whole file/table instead of deleting rows, which avoids undo, locks and replication lag. Unique keys must contain the partition column because each partition has its own local index.
हिंदी: WHERE में partition key हो तो बाकी partitions skip होते हैं। पुराना data DROP PARTITION से तुरंत जाता है। Unique key में partition column ज़रूरी है।

---

## ⚡ Alternative Solution

```sql
-- PostgreSQL declarative partitioning (verified on PGlite)
CREATE TABLE orders_log (
  id BIGINT GENERATED ALWAYS AS IDENTITY, user_id INT NOT NULL,
  amount NUMERIC(10,2) NOT NULL, created_at DATE NOT NULL,
  PRIMARY KEY (id, created_at)
) PARTITION BY RANGE (created_at);

CREATE TABLE orders_log_2024_01 PARTITION OF orders_log FOR VALUES FROM ('2024-01-01') TO ('2024-02-01');
CREATE TABLE orders_log_2024_02 PARTITION OF orders_log FOR VALUES FROM ('2024-02-01') TO ('2024-03-01');
CREATE TABLE orders_log_2024_03 PARTITION OF orders_log FOR VALUES FROM ('2024-03-01') TO ('2024-04-01');
CREATE TABLE orders_log_default PARTITION OF orders_log DEFAULT;   -- catch-all

SELECT tableoid::regclass AS partition, COUNT(*) FROM orders_log GROUP BY 1 ORDER BY 1;
-- orders_log_2024_01 | 2
-- orders_log_2024_02 | 2
-- orders_log_2024_03 | 1
-- orders_log_default | 1

EXPLAIN SELECT * FROM orders_log WHERE created_at >= '2024-02-01' AND created_at < '2024-03-01';
-- Seq Scan on orders_log_2024_02 orders_log   (only that child is scanned)

-- Same restriction: PRIMARY KEY (id) alone fails ->
-- ERROR: unique constraint on partitioned table must include all partitioning columns

-- Retention: ALTER TABLE orders_log DETACH PARTITION orders_log_2024_01;  then DROP TABLE orders_log_2024_01;
-- Automate partition creation with pg_partman (extension, not run) or a monthly cron job.
-- Other schemes: LIST (by region/tenant), HASH (spread writes evenly, no retention benefit).
```

---

## ⚠️ Common Mistake

```sql
-- ❌ Wrong: partitioning "to make queries faster" when queries don't filter on the partition key
SELECT * FROM orders_log WHERE user_id = 1;        -- touches ALL partitions: slower than one big indexed table
-- ✅ Partition on the column that appears in WHERE and drives retention (usually created_at)

-- ❌ Wrong: wrapping the key in a function — blocks pruning
WHERE DATE_FORMAT(created_at, '%Y-%m') = '2024-02'
-- ✅ WHERE created_at >= '2024-02-01' AND created_at < '2024-03-01'

-- ❌ Wrong: thousands of tiny partitions (planning/open-file overhead); aim for dozens to a few hundred
-- ❌ Wrong: forgetting the catch-all / next-month partition -> inserts fail at midnight on the 1st
```

---

## 🎯 Interview Tip (1 line)
Say: "I partition by time only when I need pruning or cheap retention, make sure queries filter on the partition key, remember the PK/unique-key must include it, and automate creating future partitions and dropping old ones — and I try indexes first because partitioning adds operational complexity."

---

## 🔗 Related Questions
→ Q148 (Time-series design) | Q154 (Sharding) | Q245 (Zero-downtime migration) | Q160 (UUID vs BIGINT)
