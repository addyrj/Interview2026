---

# Q034. Computed / Generated Columns
# Category: Data Types & DDL
# Difficulty: ⭐⭐ Medium
# DB: Both (MySQL 5.7+/8.0 | PostgreSQL 12+ STORED, 18+ VIRTUAL)

---

## ❓ Question
Create `order_items` with a `line_total` that is always `unit_price * quantity * (1 - discount%)`, without app code or triggers. Explain STORED vs VIRTUAL, whether you can write to or index them, and the MySQL vs PostgreSQL differences.

---

## 💡 Quick Concept (2 lines only)
A generated column is computed by the database from other columns of the same row: STORED saves it on disk (computed at write), VIRTUAL computes it when read. You can never INSERT/UPDATE it directly.
हिंदी: Generated column DB खुद calculate करता है — STORED = disk पर save, VIRTUAL = पढ़ते समय calculate; direct value नहीं डाल सकते।

---

## ✅ Answer / Solution

```sql
-- ============================================
-- SETUP — MySQL 8.0+ (verified on 9.1.0)
-- ============================================

CREATE TABLE order_items (
  id           INT PRIMARY KEY,
  product_name VARCHAR(100) NOT NULL,
  unit_price   DECIMAL(10,2) NOT NULL,
  quantity     INT NOT NULL,
  discount_pct DECIMAL(5,2) NOT NULL DEFAULT 0,
  -- STORED: physically saved, computed on INSERT/UPDATE
  line_total   DECIMAL(12,2) GENERATED ALWAYS AS
               (ROUND(unit_price * quantity * (1 - discount_pct / 100), 2)) STORED,
  -- VIRTUAL: computed on read, takes no space
  name_upper   VARCHAR(100) GENERATED ALWAYS AS (UPPER(product_name)) VIRTUAL
);

INSERT INTO order_items (id, product_name, unit_price, quantity, discount_pct) VALUES
  (1,'Keyboard', 49.99, 2,  0),
  (2,'Monitor', 199.50, 1, 10),
  (3,'USB Cable', 5.25, 10, 5);

-- ============================================
-- SOLUTION
-- ============================================

SELECT id, product_name, line_total, name_upper FROM order_items ORDER BY id;

-- Updating an input column recomputes automatically:
UPDATE order_items SET quantity = 3 WHERE id = 1;
SELECT id, line_total FROM order_items WHERE id = 1;

-- Writing to a generated column is rejected:
INSERT INTO order_items (id, product_name, unit_price, quantity, line_total) VALUES (4,'X',1,1,99);
-- MySQL: ERROR 3105 (HY000): The value specified for generated column 'line_total' ... is not allowed.

-- Indexes: both STORED and VIRTUAL columns can be indexed in MySQL
CREATE INDEX idx_line_total ON order_items (line_total);
CREATE INDEX idx_upper      ON order_items (name_upper);
EXPLAIN SELECT id FROM order_items WHERE name_upper = 'MONITOR';   -- type=ref, key=idx_upper

-- ============================================
-- EXPECTED OUTPUT (MySQL 9.1.0)
-- ============================================

-- id | product_name | line_total | name_upper
-- 1  | Keyboard     | 99.98      | KEYBOARD
-- 2  | Monitor      | 179.55     | MONITOR
-- 3  | USB Cable    | 49.88      | USB CABLE
--
-- After UPDATE quantity=3 for id=1:  line_total = 149.97
-- SHOW COLUMNS Extra:  line_total -> "STORED GENERATED",  name_upper -> "VIRTUAL GENERATED"
```

---

## 🔍 Why This Works (3 lines max)
The expression is part of the table definition, so every write path (app, migration, manual SQL) gets the same value — no drift. STORED costs disk but reads are free and it is indexable everywhere; VIRTUAL saves disk but costs CPU on each read.
हिंदी: Expression table definition का हिस्सा है, इसलिए हर जगह से same value आती है, कभी mismatch नहीं।

---

## ⚡ Alternative Solution

```sql
-- PostgreSQL (verified on PGlite = PostgreSQL 18.6): same STORED syntax
CREATE TABLE order_items (
  id INT PRIMARY KEY, product_name VARCHAR(100) NOT NULL,
  unit_price NUMERIC(10,2) NOT NULL, quantity INT NOT NULL, discount_pct NUMERIC(5,2) NOT NULL DEFAULT 0,
  line_total NUMERIC(12,2) GENERATED ALWAYS AS
             (ROUND(unit_price * quantity * (1 - discount_pct / 100), 2)) STORED
);
-- Same results as MySQL (99.98 / 179.55 / 49.88, then 149.97 after the update).

INSERT INTO order_items (id, product_name, unit_price, quantity, line_total) VALUES (4,'X',1,1,99);
-- ERROR: cannot insert a non-DEFAULT value into column "line_total"
UPDATE order_items SET line_total = 5 WHERE id = 1;
-- ERROR: column "line_total" can only be updated to DEFAULT

-- Differences (all observed on PG 18.6 / MySQL 9.1):
--  * PG <= 17: STORED only. PG 18 adds VIRTUAL (accepted on PGlite 18.6).
--  * PG 18 VIRTUAL: CREATE INDEX on it -> ERROR: indexes on virtual generated columns are not supported
--    (MySQL allows it). For PG, index the STORED column, or use an expression index:
CREATE INDEX idx_lower ON order_items ((LOWER(product_name)));
--  * Expression must be IMMUTABLE: GENERATED ALWAYS AS (random()) STORED -> ERROR: generation expression is not immutable
--  * PG: a generated column cannot reference another generated column:
--    ... AS (line_total * 0.18) -> ERROR: cannot use generated column "line_total" in column generation expression
```

---

## ⚠️ Common Mistake
```sql
-- ❌ Wrong: trying to set the value yourself
INSERT INTO order_items (id, product_name, unit_price, quantity, line_total) VALUES (4,'X',1,1,99);   -- error on both DBs
-- ✅ Correct: omit it (or use DEFAULT) and let the DB compute it

-- ❌ Wrong: non-deterministic / volatile expression (NOW(), RAND(), random()) -> rejected
-- ❌ Wrong: using a generated column to hold data from OTHER tables (not allowed; use a view or trigger)
-- ❌ Wrong: ALTER ... ADD STORED column on a huge table assuming it's instant -> it rewrites the table (see Q032)
```

---

## 🎯 Interview Tip (1 line)
Say: "Generated columns keep derived data consistent at the schema level; I use STORED when I need to index or read it a lot, VIRTUAL for cheap derivations (MySQL), and an expression index on PostgreSQL when I only need fast lookup on `LOWER(email)` without storing anything."

---

## 🔗 Related Questions
→ Q032 (ADD COLUMN online vs offline) | Q037 (CHECK constraints) | Q033 (Index on large table) | Functional/expression indexes
