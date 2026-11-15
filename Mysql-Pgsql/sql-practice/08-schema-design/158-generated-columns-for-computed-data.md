---

# Q158. Generated Columns for Computed Data
# Category: Schema Design
# Difficulty: ⭐⭐ Medium
# DB: Both (MySQL 8.0+ VIRTUAL/STORED | PostgreSQL 12+ STORED only)

---

## ❓ Question
How do you store a derived value such as `line_total = qty * unit_price` (or a price band) so it can never go out of sync and can be indexed? What is the difference between VIRTUAL and STORED?

---

## 💡 Quick Concept (2 lines only)
A generated column's value is computed by the DB from other columns of the same row; you cannot write to it. STORED is computed on write and takes disk; VIRTUAL (MySQL only) is computed on read, takes no space, and can still be indexed.
हिंदी: Generated column DB खुद calculate करता है, manually insert नहीं कर सकते; STORED disk लेता है, VIRTUAL नहीं।

---

## ✅ Answer / Solution

```sql
-- ============================================
-- SETUP (MySQL 9.1.0 verified)
-- ============================================

CREATE TABLE order_items (
  id         INT PRIMARY KEY,
  qty        INT,
  unit_price DECIMAL(10,2),
  line_total DECIMAL(12,2) GENERATED ALWAYS AS (qty * unit_price) STORED,
  price_band VARCHAR(10)   GENERATED ALWAYS AS
             (CASE WHEN qty * unit_price >= 500 THEN 'HIGH' ELSE 'LOW' END) VIRTUAL,
  KEY idx_lt   (line_total),
  KEY idx_band (price_band)               -- index on a VIRTUAL column is allowed (value stored in the index)
);

INSERT INTO order_items (id, qty, unit_price) VALUES (1,2,100),(2,5,150),(3,1,20);

-- ============================================
-- SOLUTION
-- ============================================
-- Step 1: select - derived values appear automatically
SELECT * FROM order_items;

-- Step 2: direct write is rejected
INSERT INTO order_items (id, qty, unit_price, line_total) VALUES (4,1,1,5);
-- ERROR 3105 (HY000): The value specified for generated column 'line_total' in table 'order_items' is not allowed.

-- Step 3: filter uses the index
EXPLAIN SELECT id FROM order_items WHERE line_total >= 500;
-- type=range, key=idx_lt, Extra=Using where; Using index

-- Step 4: updating source columns recomputes
UPDATE order_items SET qty = 10 WHERE id = 1;
SELECT id, line_total, price_band FROM order_items WHERE id = 1;

-- ============================================
-- EXPECTED OUTPUT (real run)
-- ============================================
-- Step 1:
-- id | qty | unit_price | line_total | price_band
-- 1  | 2   | 100.00     | 200.00     | LOW
-- 2  | 5   | 150.00     | 750.00     | HIGH
-- 3  | 1   | 20.00      | 20.00      | LOW
-- Step 4:
-- id | line_total | price_band
-- 1  | 1000.00    | HIGH
```

---

## 🔍 Why This Works (3 lines max)
The expression is part of the table definition, so every INSERT/UPDATE recomputes it - no trigger, no drift. Indexing the generated column makes expression predicates (JSON path, LOWER(email), qty*price) sargable.
हिंदी: Expression table definition में है, इसलिए data कभी out-of-sync नहीं होता और उस पर index भी बन सकता है।

---

## ⚡ Alternative Solution

```sql
-- PostgreSQL 12+: only STORED is supported (newer PG releases may add VIRTUAL; not verified here)
CREATE TABLE order_items (
  id INT PRIMARY KEY, qty INT, unit_price NUMERIC(10,2),
  line_total NUMERIC(12,2) GENERATED ALWAYS AS (qty * unit_price) STORED
);
INSERT INTO order_items (id, qty, unit_price) VALUES (1,2,100),(2,5,150),(3,1,20);   -- verified: 200.00 / 750.00 / 20.00
INSERT INTO order_items (id, qty, unit_price, line_total) VALUES (4,1,1,5);
-- ERROR: cannot insert a non-DEFAULT value into column "line_total"

-- PgSQL alternative for "virtual": expression index
CREATE INDEX idx_lt_expr ON order_items ((qty * unit_price));
-- MySQL 8.0 also has functional indexes: KEY ((qty * unit_price)) - no extra column needed.
```

---

## ⚠️ Common Mistake

```sql
-- ❌ Maintaining the value with app code or triggers - drifts when someone updates via SQL
UPDATE order_items SET qty = 10;     -- app forgot to recompute line_total
-- ❌ Referencing another generated column that is defined LATER, or using non-deterministic functions (NOW(), RAND()) - not allowed
-- ✅ Use GENERATED columns; choose STORED when the expression is heavy and read often, VIRTUAL when cheap
--    (note: adding a STORED column to a big table rebuilds it; adding VIRTUAL is INSTANT in MySQL)
```

---

## 🎯 Interview Tip (1 line)
Say: "Generated columns keep derived data consistent without triggers; I use VIRTUAL plus an index for JSON paths or normalized search keys in MySQL, and STORED (or an expression index) in PostgreSQL."

---

## 🔗 Related Questions
→ Q168 (MySQL JSON - indexing via generated column) | Q159 (Check constraints) | Q157 (Migrations)
