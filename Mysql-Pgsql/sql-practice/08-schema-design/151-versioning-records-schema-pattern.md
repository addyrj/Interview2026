---

# Q151. Versioning Records — Schema Pattern
# Category: Schema Design
# Difficulty: ⭐⭐ Medium
# DB: Both (MySQL 8.0+ | PostgreSQL) — verified on MySQL 9.1 and PGlite

---

## ❓ Question
Keep full history of a product's price/name changes so you can answer "what was the price on 15 April?" and still have a fast "current row" lookup. Also prevent two admins from overwriting each other's edits.

---

## 💡 Quick Concept (2 lines only)
Keep the current row in the main table and every version in a history table with valid_from / valid_to (valid_to NULL = current). Use a version column in the UPDATE's WHERE clause for optimistic locking.
हिंदी: Main table में current row, history table में हर version (valid_from/valid_to)। UPDATE में version check = optimistic lock।

---

## ✅ Answer / Solution

```sql
-- ============================================
-- SETUP
-- ============================================

CREATE TABLE products (
  id            INT PRIMARY KEY,
  name          VARCHAR(100) NOT NULL,
  current_price DECIMAL(10,2) NOT NULL,
  version       INT NOT NULL DEFAULT 1
);

CREATE TABLE product_versions (
  product_id INT NOT NULL,
  version    INT NOT NULL,
  name       VARCHAR(100) NOT NULL,
  price      DECIMAL(10,2) NOT NULL,
  valid_from DATETIME NOT NULL,
  valid_to   DATETIME NULL,            -- NULL = still current
  changed_by VARCHAR(50),
  PRIMARY KEY (product_id, version)
);

INSERT INTO products VALUES (1, 'Wireless Mouse', 799.00, 3);
INSERT INTO product_versions VALUES
  (1, 1, 'Wireless Mouse', 999.00, '2024-01-01 00:00:00', '2024-03-01 00:00:00', 'admin'),
  (1, 2, 'Wireless Mouse', 899.00, '2024-03-01 00:00:00', '2024-06-01 00:00:00', 'pricing-bot'),
  (1, 3, 'Wireless Mouse', 799.00, '2024-06-01 00:00:00', NULL,                  'pricing-bot');

-- ============================================
-- SOLUTION
-- ============================================

-- Step 1: current version
SELECT product_id, version, price FROM product_versions WHERE product_id = 1 AND valid_to IS NULL;
-- product_id | version | price
-- 1          | 3       | 799.00

-- Step 2: point-in-time ("as of 15 April 2024")
SELECT product_id, version, price
FROM product_versions
WHERE product_id = 1
  AND valid_from <= '2024-04-15 12:00:00'
  AND (valid_to IS NULL OR valid_to > '2024-04-15 12:00:00');   -- half-open interval [from, to)
-- 1 | 2 | 899.00

-- Step 3: write a new version atomically
START TRANSACTION;                       -- PgSQL: BEGIN;
UPDATE product_versions SET valid_to = '2024-09-01 00:00:00'
 WHERE product_id = 1 AND valid_to IS NULL;                     -- close the current version
INSERT INTO product_versions VALUES
  (1, 4, 'Wireless Mouse', 849.00, '2024-09-01 00:00:00', NULL, 'admin');
UPDATE products SET current_price = 849.00, version = 4
 WHERE id = 1 AND version = 3;                                  -- optimistic lock: expects version 3
SELECT ROW_COUNT() AS rows_hit;          -- MySQL; in PgSQL check the driver's affected-row count
COMMIT;
-- rows_hit = 1  (if 0 -> someone else changed it first: ROLLBACK and retry)

SELECT version, price, valid_from, valid_to FROM product_versions WHERE product_id = 1 ORDER BY version;
-- version | price  | valid_from          | valid_to
-- 1       | 999.00 | 2024-01-01 00:00:00 | 2024-03-01 00:00:00
-- 2       | 899.00 | 2024-03-01 00:00:00 | 2024-06-01 00:00:00
-- 3       | 799.00 | 2024-06-01 00:00:00 | 2024-09-01 00:00:00
-- 4       | 849.00 | 2024-09-01 00:00:00 | NULL

-- Step 4: a stale writer (still thinks version = 3) is rejected
UPDATE products SET current_price = 700.00, version = 4 WHERE id = 1 AND version = 3;
SELECT ROW_COUNT() AS rows_hit_stale;
-- rows_hit_stale = 0   -> the app must reload and retry
```

---

## 🔍 Why This Works (3 lines max)
The products table stays small and fast for current reads; history lives separately and is only queried for audits. Closing the old row and inserting the new one in a single transaction keeps intervals gap-free. `WHERE version = ?` turns a lost update into a detectable 0-rows-affected result.
हिंदी: Current data छोटी table में, history अलग। एक transaction में पुराना row बंद + नया insert। version check = lost update detect।

---

## ⚡ Alternative Solution

```sql
-- PostgreSQL: range type makes "as of" a one-liner (verified on PGlite)
CREATE TABLE pv (
  product_id INT NOT NULL, version INT NOT NULL, price NUMERIC(10,2),
  valid_during TSTZRANGE NOT NULL, PRIMARY KEY (product_id, version)
);
INSERT INTO pv VALUES (1,1,999,'[2024-01-01,2024-03-01)'),(1,2,899,'[2024-03-01,)');
SELECT version, price FROM pv
WHERE product_id = 1 AND valid_during @> '2024-04-15 12:00:00+00'::timestamptz;
-- version | price
-- 2       | 899.00

-- Add overlap protection (NOT run: needs the btree_gist extension, which PGlite did not have):
--   EXCLUDE USING gist (product_id WITH =, valid_during WITH &&)

-- MySQL 8.0 has system-versioned tables? No (that is MariaDB: WITH SYSTEM VERSIONING).
-- In MySQL use a history table written by the app or by AFTER UPDATE triggers.
-- SQL Server / MariaDB / PgSQL extension (temporal_tables) offer built-in temporal tables.
```

---

## ⚠️ Common Mistake

```sql
-- ❌ Wrong: BETWEEN on closed intervals -> a timestamp equal to valid_to matches two versions
WHERE '2024-03-01 00:00:00' BETWEEN valid_from AND valid_to;   -- matches version 1 AND version 2
-- ✅ Use half-open: valid_from <= t AND (valid_to IS NULL OR valid_to > t)

-- ❌ Wrong: closing the old row and inserting the new one in separate transactions (gap/overlap on crash)
-- ❌ Wrong: UPDATE products SET ... WHERE id = 1;   -- no version check, last writer silently wins
-- ❌ Wrong: copying the entire row set into history on every change of a 200-column table
--    (store only the changed columns or a JSON diff if rows are wide)
```

---

## 🎯 Interview Tip (1 line)
Say: "I separate the hot current table from an append-only history table with half-open validity intervals, write both in one transaction, and use a version column for optimistic concurrency — I'd choose range types with an exclusion constraint on Postgres to make overlaps impossible."

---

## 🔗 Related Questions
→ Q150 (Event sourcing) | Q159 (CHECK constraints) | Q017 / Q242 (SELECT FOR UPDATE) | Q013 (UPSERT)
