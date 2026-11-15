---

# Q013. INSERT with ON DUPLICATE KEY (MySQL) vs ON CONFLICT (PgSQL)
# Category: Fundamentals
# Difficulty: ⭐⭐ Medium
# DB: Both (MySQL + PostgreSQL)

---

## ❓ Question
Load a stock feed into `product_stock`: insert new SKUs, update existing ones, never fail on duplicates. Write the upsert for MySQL and PostgreSQL, add to the existing quantity instead of overwriting it, skip duplicates silently, and explain what `ROW_COUNT()` returns and why `REPLACE INTO` is dangerous.

---

## 💡 Quick Concept (2 lines only)
An upsert is atomic "insert, or update if the key already exists". MySQL: `INSERT ... ON DUPLICATE KEY UPDATE` (fires on ANY unique key); PostgreSQL: `INSERT ... ON CONFLICT (key) DO UPDATE / DO NOTHING` with the new row available as `EXCLUDED`.
हिंदी: Upsert = "insert करो, key पहले से हो तो update करो"; MySQL में ON DUPLICATE KEY UPDATE, PostgreSQL में ON CONFLICT ... DO UPDATE (नई row = EXCLUDED)।

---

## ✅ Answer / Solution

```sql
-- ============================================
-- SETUP (run this first - works on both engines)
-- ============================================

CREATE TABLE product_stock (
  sku        VARCHAR(20) PRIMARY KEY,
  qty        INT NOT NULL,
  price      DECIMAL(10,2),
  updated_by VARCHAR(20),
  hits       INT DEFAULT 0
);

INSERT INTO product_stock (sku, qty, price, updated_by) VALUES
  ('A-100', 10, 99.00, 'seed'),
  ('B-200',  5, 49.00, 'seed');

-- ============================================
-- SOLUTION: MySQL (8.0.19+ row alias; verified on 9.1.0)
-- ============================================

-- Existing SKU A-100 -> update; "AS new" gives the incoming row an alias
INSERT INTO product_stock (sku, qty, price, updated_by)
VALUES ('A-100', 25, 105.00, 'import') AS new
ON DUPLICATE KEY UPDATE
  qty = new.qty, price = new.price, updated_by = new.updated_by,
  hits = hits + 1;                         -- plain column name = the EXISTING row's value
SELECT ROW_COUNT();                        -- 2  (2 = existing row updated)

-- New SKU C-300 -> plain insert
INSERT INTO product_stock (sku, qty, price, updated_by)
VALUES ('C-300', 7, 15.00, 'import') AS new
ON DUPLICATE KEY UPDATE qty = new.qty;
SELECT ROW_COUNT();                        -- 1  (1 = new row inserted)

-- ============================================
-- SOLUTION: PostgreSQL (9.5+; verified in PGlite)
-- ============================================

INSERT INTO product_stock (sku, qty, price, updated_by)
VALUES ('A-100', 25, 105.00, 'import')
ON CONFLICT (sku)                           -- conflict target is REQUIRED for DO UPDATE
DO UPDATE SET
  qty = EXCLUDED.qty, price = EXCLUDED.price, updated_by = EXCLUDED.updated_by,
  hits = product_stock.hits + 1             -- table name = existing row, EXCLUDED = incoming row
RETURNING sku, qty, price, hits;

-- ============================================
-- EXPECTED OUTPUT
-- ============================================

-- MySQL ROW_COUNT(): 2 for the update of A-100, 1 for the insert of C-300
-- PostgreSQL RETURNING: sku=A-100 | qty=25 | price=105.00 | hits=1
-- Final table on both engines after both upserts:
-- sku   | qty | price  | updated_by | hits
-- A-100 |  25 | 105.00 | import     | 1
-- B-200 |   5 | 49.00  | seed       | 0
-- C-300 |   7 | 15.00  | import     | 0
```

---

## 🔍 Why This Works (3 lines max)
The engine checks the unique index and, instead of raising a duplicate-key error, runs the UPDATE on the conflicting row inside the same atomic statement - no race between a SELECT and an INSERT. In MySQL the row count is 1 for insert, 2 for update, 0 if nothing actually changed. PostgreSQL's `RETURNING` hands back the final row either way.
हिंदी: Engine unique index देखता है और duplicate पर error की जगह उसी statement में UPDATE चला देता है, इसलिए SELECT-फिर-INSERT की race नहीं होती।

---

## ⚡ Alternative Solution

```sql
-- Add to existing qty (stock top-up) instead of overwrite:
-- MySQL:      INSERT ... VALUES ('B-200', 6, 50.00, 'import')
--             ON DUPLICATE KEY UPDATE qty = qty + VALUES(qty);   -- VALUES() works but is deprecated since 8.0.20
-- PostgreSQL: INSERT ... VALUES ('B-200', 6, 50.00, 'import')
--             ON CONFLICT (sku) DO UPDATE SET qty = product_stock.qty + EXCLUDED.qty;
-- Both gave B-200 qty = 11 when run on top of the seed data (5 + 6).

-- Skip duplicates silently:
-- MySQL:      INSERT IGNORE INTO product_stock (...) VALUES (...);   -- also swallows OTHER errors/truncation warnings
-- PostgreSQL: INSERT ... ON CONFLICT DO NOTHING;                     -- PGlite: 1 row inserted for a new key, 0 for a dup
-- PostgreSQL with RETURNING + DO NOTHING returns NO row for the skipped duplicate (verified).

-- Distinguish insert vs update in PostgreSQL (trick, relies on a system column):
-- RETURNING sku, (xmax = 0) AS inserted   -> A-100: false (updated), C-300: true (inserted)  (verified)

-- MySQL REPLACE INTO = DELETE + INSERT. It resets every column you did not list:
REPLACE INTO product_stock (sku, qty) VALUES ('A-100', 1);
-- MySQL result for A-100: qty 1 | price NULL | updated_by NULL | hits 0   <- data lost!
-- PostgreSQL has no REPLACE statement.
```

---

## ⚠️ Common Mistake

```sql
-- ❌ Wrong: MySQL syntax on PostgreSQL (and vice versa) - both fail instantly:
-- PGlite:  INSERT ... ON DUPLICATE KEY UPDATE ...  -> ERROR: syntax error at or near "DUPLICATE"
-- MySQL:   INSERT ... ON CONFLICT (sku) DO NOTHING -> ERROR 1064 syntax error near 'CONFLICT'

-- ❌ Wrong: PostgreSQL, same key twice in ONE statement
INSERT INTO product_stock (sku, qty, price) VALUES ('A-100', 1, 1), ('A-100', 2, 2)
ON CONFLICT (sku) DO UPDATE SET qty = EXCLUDED.qty;
-- ERROR: ON CONFLICT DO UPDATE command cannot affect row a second time
-- ✅ De-duplicate the batch first (e.g. DISTINCT ON / GROUP BY)

-- ❌ Wrong: relying on ON DUPLICATE KEY when the table has several unique keys -
--    MySQL fires on whichever unique key conflicts first, possibly updating the wrong row.
-- ❌ Wrong: SELECT-then-INSERT in app code (race condition between two workers)
```

---

## 🎯 Interview Tip (1 line)
Say: "I use a single atomic upsert backed by a unique index, never SELECT-then-INSERT, and I avoid REPLACE INTO because it deletes and re-inserts - losing unlisted columns and firing delete triggers/cascades."

---

## 🔗 Related Questions
→ Q239 (Find duplicates, unique constraint + upsert) | Q014 (UPDATE with JOIN) | Q015 (DELETE vs TRUNCATE vs DROP) | Q242 (SELECT FOR UPDATE)
