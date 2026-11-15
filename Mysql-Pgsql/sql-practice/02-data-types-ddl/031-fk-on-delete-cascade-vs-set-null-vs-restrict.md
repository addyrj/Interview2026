---

# Q031. FOREIGN KEY — ON DELETE CASCADE vs SET NULL vs RESTRICT
# Category: Data Types & DDL
# Difficulty: ⭐⭐ Medium
# DB: Both (MySQL 8.0+ | PostgreSQL)

---

## ❓ Question
A parent row (`customers`) is deleted while child rows (`orders`) still reference it. Show what each referential action does: `ON DELETE CASCADE`, `ON DELETE SET NULL`, `ON DELETE RESTRICT` (and the default `NO ACTION`). Which one do you pick for orders, audit logs and optional references?

---

## 💡 Quick Concept (2 lines only)
The ON DELETE action tells the database what to do with child rows: CASCADE deletes them, SET NULL orphans them (column must be nullable), RESTRICT/NO ACTION blocks the parent delete.
हिंदी: Parent delete होने पर child का क्या हो — CASCADE = child भी delete, SET NULL = link हटाओ, RESTRICT = delete रोक दो।

---

## ✅ Answer / Solution

```sql
-- ============================================
-- SETUP (run this first) — same SQL on MySQL 8+/9 and PostgreSQL
-- ============================================

CREATE TABLE customers (
  id   INT PRIMARY KEY,
  name VARCHAR(100)
);

-- CASCADE: child dies with parent
CREATE TABLE orders_cascade (
  id INT PRIMARY KEY, customer_id INT,
  FOREIGN KEY (customer_id) REFERENCES customers(id) ON DELETE CASCADE
);
-- SET NULL: child survives, link removed (column MUST be nullable)
CREATE TABLE orders_setnull (
  id INT PRIMARY KEY, customer_id INT NULL,
  FOREIGN KEY (customer_id) REFERENCES customers(id) ON DELETE SET NULL
);
-- RESTRICT: parent delete is refused while children exist
CREATE TABLE orders_restrict (
  id INT PRIMARY KEY, customer_id INT NOT NULL,
  FOREIGN KEY (customer_id) REFERENCES customers(id) ON DELETE RESTRICT
);

INSERT INTO customers VALUES (1,'Asha'),(2,'Bilal'),(3,'Chen');
INSERT INTO orders_cascade  VALUES (10,1),(11,1),(12,2);
INSERT INTO orders_setnull  VALUES (20,1),(21,2),(22,3);
INSERT INTO orders_restrict VALUES (30,3);

-- ============================================
-- SOLUTION
-- ============================================

-- Step 1: delete Chen (id 3) -> RESTRICT table blocks it
DELETE FROM customers WHERE id = 3;
-- MySQL : ERROR 1451 (23000): Cannot delete or update a parent row: a foreign key constraint fails ...
-- PgSQL : ERROR: update or delete on table "customers" violates RESTRICT setting of foreign key constraint ...

-- Step 2: delete Asha (id 1) -> works, CASCADE + SET NULL fire
DELETE FROM customers WHERE id = 1;

SELECT * FROM orders_cascade ORDER BY id;
SELECT * FROM orders_setnull ORDER BY id;
SELECT * FROM customers ORDER BY id;

-- ============================================
-- EXPECTED OUTPUT (identical on MySQL 9.1 and PGlite/PostgreSQL 18)
-- ============================================

-- orders_cascade (Asha's orders 10, 11 are gone):
-- id | customer_id
-- 12 | 2

-- orders_setnull (order 20 kept, customer_id nulled):
-- id | customer_id
-- 20 | NULL
-- 21 | 2
-- 22 | 3

-- customers (Chen survived because RESTRICT blocked step 1):
-- id | name
-- 2  | Bilal
-- 3  | Chen
```

---

## 🔍 Why This Works (3 lines max)
The FK check runs when the parent row is deleted: CASCADE issues an implicit DELETE on children, SET NULL an implicit UPDATE, RESTRICT raises an error immediately. Step 1 failed as a whole statement, so nothing was removed for Chen.
हिंदी: FK action parent delete के समय child पर चलता है; RESTRICT error देकर पूरा statement रोक देता है।

---

## ⚡ Alternative Solution

```sql
-- Default action (no ON DELETE clause) = NO ACTION. Verified: delete is blocked.
CREATE TABLE orders_noaction (
  id INT PRIMARY KEY, customer_id INT,
  FOREIGN KEY (customer_id) REFERENCES customers(id)
);
INSERT INTO orders_noaction VALUES (40,2);
DELETE FROM customers WHERE id = 2;   -- ERROR on both engines

-- MySQL vs PgSQL difference:
--  MySQL (InnoDB): NO ACTION behaves exactly like RESTRICT (checked immediately).
--  PgSQL: NO ACTION can be DEFERRED to commit time (if constraint is DEFERRABLE, see Q038); RESTRICT never can.
--  PgSQL also supports ON DELETE SET DEFAULT; MySQL docs say InnoDB does not implement it (avoid; not exercised here).
```

---

## ⚠️ Common Mistake
```sql
-- ❌ Wrong: SET NULL on a NOT NULL column -> MySQL: CREATE TABLE fails (ERROR 1830); PgSQL: table is created, but the parent DELETE fails at runtime (not-null violation) — both verified
-- ❌ Wrong: CASCADE on financial rows -> one DELETE wipes invoices, payments, ledger entries silently
-- ❌ Wrong: no index on the child FK column -> every parent delete scans the whole child table
--           (PgSQL does NOT auto-index FK columns; MySQL InnoDB does)
-- ✅ Correct: CASCADE for pure ownership (order_items of an order), RESTRICT for money/legal data,
--             SET NULL for optional links (assigned_to), soft-delete (deleted_at) for users.
CREATE INDEX idx_orders_customer ON orders_cascade (customer_id);   -- needed on PgSQL
```

---

## 🎯 Interview Tip (1 line)
Say: "I use CASCADE only for strict parent-owned rows, RESTRICT for financial/audit data, SET NULL for optional references, and I always index the FK column — also, cascades are invisible to application code and don't fire application-level hooks/CDC the way you expect, so for big tables I prefer explicit batched deletes."

---

## 🔗 Related Questions
→ Q037 (CHECK constraints) | Q038 (DEFERRABLE constraints) | Q030 (PRIMARY KEY / UNIQUE) | Q245 (migrate 100M rows)
