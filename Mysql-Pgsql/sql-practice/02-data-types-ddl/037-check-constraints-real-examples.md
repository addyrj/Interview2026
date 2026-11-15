---

# Q037. CHECK Constraints — Real Examples
# Category: Data Types & DDL
# Difficulty: ⭐⭐ Medium
# DB: Both (MySQL 8.0.16+ | PostgreSQL)

---

## ❓ Question
Use CHECK constraints to enforce real business rules on a `products` table: positive price, sale price below price, non-negative stock, allowed status values, SKU format, and a valid date range. How does NULL interact with CHECK, and how do you add one to an existing big table?

---

## 💡 Quick Concept (2 lines only)
A CHECK rejects a row only when its expression evaluates to FALSE; TRUE and NULL (unknown) both pass. MySQL enforces CHECK only from 8.0.16 (earlier versions parsed and ignored it).
हिंदी: CHECK सिर्फ FALSE पर reject करता है; NULL पास हो जाता है — इसलिए NOT NULL अलग से लगाओ।

---

## ✅ Answer / Solution

```sql
-- ============================================
-- SETUP — MySQL 8.0.16+ (verified on 9.1.0). PgSQL differences below.
-- ============================================

CREATE TABLE products (
  id         INT PRIMARY KEY,
  name       VARCHAR(100)  NOT NULL,
  price      DECIMAL(10,2) NOT NULL,
  sale_price DECIMAL(10,2) NULL,
  stock      INT           NOT NULL DEFAULT 0,
  status     VARCHAR(10)   NOT NULL DEFAULT 'draft',
  sku        VARCHAR(20)   NOT NULL,
  valid_from DATE          NOT NULL,
  valid_to   DATE          NULL,
  CONSTRAINT chk_price_positive CHECK (price > 0),
  CONSTRAINT chk_sale_lt_price  CHECK (sale_price IS NULL OR sale_price < price),
  CONSTRAINT chk_stock_nonneg   CHECK (stock >= 0),
  CONSTRAINT chk_status         CHECK (status IN ('draft','active','archived')),
  CONSTRAINT chk_sku_format     CHECK (sku REGEXP '^[A-Z]{3}-[0-9]{4}$'),   -- PgSQL: sku ~ '^[A-Z]{3}-[0-9]{4}$'
  CONSTRAINT chk_date_range     CHECK (valid_to IS NULL OR valid_to >= valid_from)
);

-- ============================================
-- SOLUTION
-- ============================================

INSERT INTO products VALUES (1,'Laptop',55000,49999,10,'active','LAP-0001','2024-01-01',NULL);   -- OK
INSERT INTO products VALUES (2,'Mouse',-5,NULL,10,'active','MOU-0001','2024-01-01',NULL);        -- violates chk_price_positive
INSERT INTO products VALUES (3,'Cable',100,150,10,'active','CAB-0001','2024-01-01',NULL);        -- violates chk_sale_lt_price
INSERT INTO products VALUES (4,'Pen',10,NULL,-1,'active','PEN-0001','2024-01-01',NULL);          -- violates chk_stock_nonneg
INSERT INTO products VALUES (5,'Pad',10,NULL,1,'deleted','PAD-0001','2024-01-01',NULL);          -- violates chk_status
INSERT INTO products VALUES (6,'Bag',10,NULL,1,'active','bag-1','2024-01-01',NULL);              -- violates chk_sku_format
INSERT INTO products VALUES (7,'Cap',10,NULL,1,'active','CAP-0001','2024-06-01','2024-01-01');   -- violates chk_date_range
INSERT INTO products VALUES (8,'Hat',10,NULL,1,'active','HAT-0001','2024-06-01',NULL);           -- OK (NULL sale_price/valid_to pass)
UPDATE products SET price = 0 WHERE id = 1;                                                     -- violates chk_price_positive

SELECT id, name, price, sale_price FROM products ORDER BY id;

-- ============================================
-- EXPECTED OUTPUT
-- ============================================

-- MySQL error text:  ERROR 3819 (HY000): Check constraint 'chk_price_positive' is violated.
-- PgSQL error text:  ERROR: new row for relation "products" violates check constraint "chk_price_positive"
-- (inserts 2-7 and the UPDATE each fail with their own constraint name; verified on both engines)
--
-- id | name   | price    | sale_price
-- 1  | Laptop | 55000.00 | 49999.00
-- 8  | Hat    | 10.00    | NULL
```

---

## 🔍 Why This Works (3 lines max)
The engine evaluates every CHECK on INSERT and UPDATE; FALSE aborts the statement. Rules like `sale_price IS NULL OR sale_price < price` handle NULL explicitly, and named constraints give readable errors that your API can map to messages.
हिंदी: हर INSERT/UPDATE पर CHECK evaluate होता है; constraint को नाम दो ताकि error साफ़ दिखे।

---

## ⚡ Alternative Solution

```sql
-- PostgreSQL: same table, only the regex operator changes (verified on PGlite 18.6)
--   CHECK (sku ~ '^[A-Z]{3}-[0-9]{4}$')     NUMERIC instead of DECIMAL is the same type

-- Adding a CHECK to an EXISTING big table
-- PgSQL: NOT VALID = enforced for new writes immediately, existing rows verified later (light lock)
INSERT INTO products VALUES (9,'Old',10,NULL,1,'active','OLD-0001','2024-01-01',NULL);   -- legacy short name already present
ALTER TABLE products ADD CONSTRAINT chk_name_len CHECK (char_length(name) >= 4) NOT VALID;   -- accepted despite 'Old'
INSERT INTO products VALUES (10,'Abc',10,NULL,1,'active','ABC-0001','2024-01-01',NULL);   -- still rejected
ALTER TABLE products VALIDATE CONSTRAINT chk_name_len;   -- fails while a short name (e.g. 'Old') exists; passes after cleanup
-- (pg_constraint.convalidated = false until validated)

-- MySQL 8.0.16+: no NOT VALID; use NOT ENFORCED to add it without enforcing, then ENFORCE later
ALTER TABLE products ADD CONSTRAINT chk_name_len CHECK (CHAR_LENGTH(name) >= 3) NOT ENFORCED;
INSERT INTO products VALUES (9,'AB',10,NULL,1,'active','ABC-0001','2024-01-01',NULL);     -- succeeds (not enforced)
-- information_schema.check_constraints / table_constraints shows ENFORCED = NO for chk_name_len
-- ALTER TABLE products ALTER CONSTRAINT chk_name_len ENFORCED;   -- would validate existing rows (not run)
```

---

## ⚠️ Common Mistake
```sql
-- ❌ Wrong: CHECK (sale_price < price) and expecting NULL sale_price to be rejected -> NULL passes
-- ✅ Correct: add NOT NULL if the column is mandatory; CHECK is for "if present, then valid"

-- ❌ Wrong: relying on CHECK in MySQL 5.7 / MariaDB < 10.2 -> accepted but ignored
-- ❌ Wrong: CHECK referencing other rows/tables (subquery) -> not allowed; use trigger/FK/exclusion constraint
-- ❌ Wrong: ADD CONSTRAINT ... CHECK on a huge PG table without NOT VALID -> full scan under ACCESS EXCLUSIVE lock
```

---

## 🎯 Interview Tip (1 line)
Say: "CHECKs are my last line of defence for invariants that must hold regardless of which service writes; I name them, handle NULL explicitly, and on PostgreSQL I add them NOT VALID then VALIDATE to avoid long locks."

---

## 🔗 Related Questions
→ Q031 (Foreign keys) | Q034 (Generated columns) | Q038 (DEFERRABLE) | Q032 (ADD COLUMN online)
