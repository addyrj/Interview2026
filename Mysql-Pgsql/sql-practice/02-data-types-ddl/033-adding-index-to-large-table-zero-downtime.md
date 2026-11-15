---

# Q033. Adding an Index to a Large Table — Zero Downtime Approach
# Category: Data Types & DDL
# Difficulty: ⭐⭐⭐ Hard
# DB: Both (MySQL 8.0+ | PostgreSQL)

---

## ❓ Question
Your `orders` table has 500M rows and serves live traffic. How do you add an index on `(customer_id, created_at)` without blocking reads/writes? What can go wrong, and how do you check the index is valid?

---

## 💡 Quick Concept (2 lines only)
MySQL InnoDB builds secondary indexes online with `ALGORITHM=INPLACE, LOCK=NONE`; PostgreSQL needs `CREATE INDEX CONCURRENTLY` (plain CREATE INDEX blocks writes). Both still take brief metadata locks at start and end.
हिंदी: MySQL में INPLACE + LOCK=NONE, PostgreSQL में CREATE INDEX CONCURRENTLY — writes block नहीं होते।

---

## ✅ Answer / Solution

```sql
-- ============================================
-- SETUP (MySQL 8.0+; small demo data, the syntax is what matters)
-- ============================================

CREATE TABLE orders (
  id          INT AUTO_INCREMENT PRIMARY KEY,
  customer_id INT NOT NULL,
  status      VARCHAR(20) NOT NULL,
  created_at  DATETIME NOT NULL
);

INSERT INTO orders (customer_id, status, created_at) VALUES
  (42,'pending','2024-01-02 10:00:00'),
  (42,'shipped','2024-01-06 11:00:00'),
  (7, 'pending','2024-01-03 09:30:00');

-- ============================================
-- SOLUTION — MySQL
-- ============================================

-- Step 1: state intent explicitly; fails fast if an online build is impossible
ALTER TABLE orders
  ADD INDEX idx_orders_customer_created (customer_id, created_at),
  ALGORITHM=INPLACE, LOCK=NONE;

-- Step 2: confirm
SHOW INDEX FROM orders;
EXPLAIN SELECT id FROM orders WHERE customer_id = 42 AND created_at >= '2024-01-05';

-- Cases that are NOT fully online:
ALTER TABLE orders ADD INDEX idx_x (status), ALGORITHM=INSTANT;      -- ERROR 1845: INSTANT not supported for ADD INDEX
ALTER TABLE orders ADD FULLTEXT INDEX ft_s (status), LOCK=NONE;      -- ERROR 1846: Fulltext index creation requires a lock

-- ============================================
-- EXPECTED OUTPUT (MySQL 9.1.0)
-- ============================================

-- SHOW INDEX (key columns only):
-- Key_name                    | Seq_in_index | Column_name | Index_type
-- PRIMARY                     | 1            | id          | BTREE
-- idx_orders_customer_created | 1            | customer_id | BTREE
-- idx_orders_customer_created | 2            | created_at  | BTREE
--
-- EXPLAIN: key = idx_orders_customer_created, Extra = "Using where; Using index"
-- (observed on an EMPTY demo table: type=index, rows=1; plan on real data may differ, typically 'range')
```

---

## 🔍 Why This Works (3 lines max)
INPLACE builds the B-tree from a table scan while logging concurrent DML into a side buffer and replaying it, so the table stays readable/writable. PostgreSQL's CONCURRENTLY does two table scans and waits for old transactions, trading speed (2-3x slower) for no write lock.
हिंदी: Index build के दौरान आने वाले writes log होकर बाद में apply होते हैं, इसलिए table चालू रहती है।

---

## ⚡ Alternative Solution

```sql
-- PostgreSQL (verified on PGlite = PostgreSQL 18.6)
CREATE INDEX CONCURRENTLY idx_orders_customer_created ON orders (customer_id, created_at);

-- Rules: CANNOT run inside BEGIN...COMMIT:
--   ERROR: CREATE INDEX CONCURRENTLY cannot run inside a transaction block
-- If it fails (deadlock, duplicate in a UNIQUE build, cancel) it leaves an INVALID index behind:
CREATE UNIQUE INDEX CONCURRENTLY uq_dup ON orders (customer_id);   -- ERROR: could not create unique index (duplicates)
SELECT c.relname, i.indisvalid FROM pg_index i JOIN pg_class c ON c.oid = i.indexrelid
WHERE i.indrelid = 'orders'::regclass ORDER BY 1;
-- relname                     | indisvalid
-- idx_orders_customer_created | true
-- orders_pkey                 | true
-- uq_dup                      | false      <-- invalid leftover: still slows writes, never used by queries
DROP INDEX CONCURRENTLY uq_dup;            -- clean it up, fix data, retry

-- Large-table checklist (not run here):
--  * MySQL: gh-ost / pt-online-schema-change when INPLACE is not enough (e.g. changing PK or column type)
--  * Run off-peak; watch replica lag (MySQL replicas replay the ALTER; PG replicas replay index build WAL)
--  * PG: SET maintenance_work_mem higher for the session; MySQL: innodb_sort_buffer_size / innodb_ddl_threads (8.0.27+)
--  * Replace an index with no downtime: build new CONCURRENTLY, then DROP INDEX CONCURRENTLY the old one
```

---

## ⚠️ Common Mistake
```sql
-- ❌ Wrong (PgSQL): plain CREATE INDEX on a live table -> takes SHARE lock, blocks all INSERT/UPDATE/DELETE for the whole build
CREATE INDEX idx_orders_customer_created ON orders (customer_id, created_at);
-- ✅ Correct
CREATE INDEX CONCURRENTLY idx_orders_customer_created ON orders (customer_id, created_at);

-- ❌ Wrong: not checking indisvalid after a failed CONCURRENTLY build, leaving a zombie index
-- ❌ Wrong (MySQL): omitting ALGORITHM/LOCK so the server silently picks COPY on unsupported cases
-- ❌ Wrong: starting the build while a multi-hour transaction is open (PG CONCURRENTLY waits for it; MySQL waits for metadata lock)
```

---

## 🎯 Interview Tip (1 line)
Say: "MySQL: ALGORITHM=INPLACE, LOCK=NONE with the clause pinned so it fails fast; PostgreSQL: CREATE INDEX CONCURRENTLY outside a transaction, then verify `indisvalid` and drop any invalid leftover — and I watch for long-running transactions and replica lag, and use gh-ost/pt-osc if the change needs a table rebuild."

---

## 🔗 Related Questions
→ Q032 (ADD COLUMN online vs offline) | Q034 (Generated columns) | Q245 (Migrate 100M rows zero downtime) | Indexes cheatsheet
