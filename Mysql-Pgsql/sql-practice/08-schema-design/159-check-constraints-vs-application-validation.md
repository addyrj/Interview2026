---

# Q159. Check Constraints vs Application Validation
# Category: Schema Design
# Difficulty: ⭐⭐ Medium
# DB: Both (MySQL 8.0.16+ | PostgreSQL)

---

## ❓ Question
Should rules like `price > 0` and `discount between 0 and 100` live in the database as CHECK constraints or only in application code? How do CHECKs treat NULL, and what changed in MySQL 8.0.16?

---

## 💡 Quick Concept (2 lines only)
A CHECK constraint is enforced by the DB for every writer (app, scripts, migrations, other services); app validation gives friendly errors but can be bypassed. Use both: app for UX, DB as the last line of defence.
हिंदी: CHECK constraint हर writer पर लागू होता है; app validation bypass हो सकती है, इसलिए दोनों रखो।

---

## ✅ Answer / Solution

```sql
-- ============================================
-- SETUP (MySQL 9.1.0 verified)
-- ============================================

CREATE TABLE products (
  id           INT PRIMARY KEY,
  name         VARCHAR(50),
  price        DECIMAL(10,2),
  discount_pct TINYINT UNSIGNED,
  CONSTRAINT chk_price CHECK (price > 0),
  CONSTRAINT chk_disc  CHECK (discount_pct BETWEEN 0 AND 100)
);

-- ============================================
-- SOLUTION
-- ============================================

INSERT INTO products VALUES (1, 'Pen', 10, 5);               -- OK
INSERT INTO products VALUES (2, 'Bad', -1, 5);               -- rejected
-- ERROR 3819 (HY000): Check constraint 'chk_price' is violated.
INSERT INTO products VALUES (3, 'Bad2', 10, 150);            -- rejected
-- ERROR 3819 (HY000): Check constraint 'chk_disc' is violated.
UPDATE products SET price = 0 WHERE id = 1;                  -- UPDATE is checked too
-- ERROR 3819 (HY000): Check constraint 'chk_price' is violated.

-- NULL passes a CHECK (the condition evaluates to UNKNOWN, not FALSE):
INSERT INTO products VALUES (4, 'Null', NULL, NULL);          -- OK!
-- Add NOT NULL to the column if NULL must be blocked.

-- ============================================
-- EXPECTED OUTPUT (real run)
-- ============================================
-- SELECT * FROM products;
-- id | name | price | discount_pct
-- 1  | Pen  | 10.00 | 5
-- 4  | Null | NULL  | NULL
```

---

## 🔍 Why This Works (3 lines max)
The DB evaluates the predicate on every INSERT/UPDATE and rejects rows where it is FALSE; UNKNOWN (from NULL) passes. This protects data from bugs, ad-hoc SQL, and other services writing to the table.
हिंदी: Predicate FALSE हो तो row reject; NULL पर UNKNOWN आता है इसलिए वो pass हो जाता है।

---

## ⚡ Alternative Solution

```sql
-- Adding a CHECK to an existing table (MySQL): validates ALL existing rows, may be slow/fails on bad data
ALTER TABLE products ADD CONSTRAINT chk_name CHECK (CHAR_LENGTH(name) >= 3);
-- Add without enforcing yet, clean data, then enforce (verified):
ALTER TABLE products ADD CONSTRAINT chk_name CHECK (CHAR_LENGTH(name) >= 3) NOT ENFORCED;
-- SELECT constraint_name, enforced FROM information_schema.table_constraints WHERE constraint_type='CHECK';
--   chk_disc YES | chk_name NO | chk_price YES
INSERT INTO products VALUES (5, 'ab', 10, 1);                -- accepted while NOT ENFORCED
ALTER TABLE products ALTER CHECK chk_name ENFORCED;
-- ERROR 3819: Check constraint 'chk_name' is violated.   (existing bad row blocks enforcement)

-- PostgreSQL (verified in PGlite): same inline syntax, plus a zero-downtime way for big tables
CREATE TABLE products (
  id INT PRIMARY KEY, name TEXT,
  price NUMERIC(10,2) CONSTRAINT chk_price CHECK (price > 0),
  discount_pct SMALLINT CONSTRAINT chk_disc CHECK (discount_pct BETWEEN 0 AND 100)
);
-- PgSQL error text: new row for relation "products" violates check constraint "chk_price"
ALTER TABLE products ADD CONSTRAINT chk_big CHECK (price < 1000000) NOT VALID;   -- new rows only
ALTER TABLE products VALIDATE CONSTRAINT chk_big;                                -- scan later, light lock

-- MySQL before 8.0.16 (e.g. 5.7) parsed CHECK but SILENTLY IGNORED it - always test on your version.
```

---

## ⚠️ Common Mistake

```sql
-- ❌ Only validating in the app: a one-off script or second service inserts price = -1 and reports break
-- ❌ Putting cross-row/cross-table rules in CHECK (e.g. "total of items = order total", or subqueries):
--    not allowed / not reliable - use FK, unique index, or triggers for those
-- ❌ Using a non-deterministic function (NOW(), RAND()) in CHECK - rejected by MySQL
-- ✅ Simple row-level invariants -> CHECK; business workflows and nice messages -> app; relationships -> FK
```

---

## 🎯 Interview Tip (1 line)
Say: "I put row-level invariants in the DB as named CHECK constraints so every writer is covered, keep rich validation in the app for UX, remember NULL passes a CHECK, and on PostgreSQL I add big-table checks as NOT VALID then VALIDATE."

---

## 🔗 Related Questions
→ Q158 (Generated columns) | Q157 (Zero-downtime migrations) | Q167 (ENUM pitfalls)
