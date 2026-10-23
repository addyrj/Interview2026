---

# Q221. DELETE vs TRUNCATE vs DROP
# Category: Interview Classics
# Difficulty: ⭐ Easy
# DB: Both (MySQL + PostgreSQL)

---

## ❓ Question
What is the difference between DELETE, TRUNCATE, and DROP? When would you use each? What happens with foreign keys, triggers, and transactions for each?

---

## 💡 Quick Concept (2 lines only)
DELETE removes rows (filterable, logged, triggers fire, rollbackable). TRUNCATE removes ALL rows fast (minimal logging, no triggers, hard to rollback in MySQL). DROP removes the entire table structure + data permanently.
हिंदी: DELETE = rows हटाओ (filter + rollback possible). TRUNCATE = सब rows तेज़ी से हटाओ (triggers नहीं). DROP = पूरी table ही हटाओ।

---

## ✅ Answer / Solution

```sql
-- ============================================
-- SETUP
-- ============================================

CREATE TABLE orders (
  id        INT PRIMARY KEY AUTO_INCREMENT,
  user_id   INT NOT NULL,
  amount    DECIMAL(10,2),
  status    VARCHAR(20),
  created_at DATETIME DEFAULT NOW()
);

INSERT INTO orders (user_id, amount, status) VALUES
  (1, 100.00, 'pending'),
  (2, 200.00, 'completed'),
  (3, 150.00, 'pending'),
  (4, 300.00, 'cancelled');

-- ============================================
-- DELETE — Remove specific rows
-- ============================================

-- DML (Data Manipulation Language)
-- Rows removed one by one (each deletion logged in transaction log)
-- WHERE clause supported → partial delete
-- Triggers FIRE on each row
-- Can be ROLLED BACK (within a transaction)
-- Slower on large tables (row-by-row)
-- AUTO_INCREMENT counter NOT reset

BEGIN;
  DELETE FROM orders WHERE status = 'cancelled';
  -- Only status='cancelled' row removed
  -- ROLLBACK possible here!
ROLLBACK;  -- or COMMIT;

-- With JOIN (MySQL syntax):
DELETE o FROM orders o
JOIN users u ON o.user_id = u.id
WHERE u.is_banned = 1;

-- PgSQL syntax:
DELETE FROM orders o
USING users u
WHERE o.user_id = u.id
AND u.is_banned = true;

-- DELETE with RETURNING (PgSQL only — returns deleted rows):
DELETE FROM orders WHERE status = 'cancelled'
RETURNING id, user_id, amount;
-- Returns: the rows that were deleted (useful!)

-- ============================================
-- TRUNCATE — Remove ALL rows fast
-- ============================================

-- DDL (Data Definition Language)
-- Deallocates data pages — much faster than DELETE for large tables
-- NO WHERE clause — ALL rows removed
-- Triggers DO NOT FIRE (except TRUNCATE triggers in PgSQL)
-- AUTO_INCREMENT / SEQUENCE reset to 1
-- In MySQL: auto-commits even inside a transaction (implicit commit!)
-- In PgSQL: CAN be rolled back (transactional DDL!)
-- Resets table statistics

TRUNCATE TABLE orders;
-- All rows gone, AUTO_INCREMENT reset to 1

-- MySQL: TRUNCATE cannot be rolled back easily (auto-commit)
-- PgSQL: TRUNCATE IS transactional
BEGIN;
  TRUNCATE orders;
  ROLLBACK;  -- In PgSQL: this WORKS, rows restored!
             -- In MySQL: TRUNCATE commits immediately — ROLLBACK has no effect!

-- TRUNCATE with foreign key constraint:
-- MySQL: ERROR if other tables reference orders with FK
-- Must disable FK checks first:
SET FOREIGN_KEY_CHECKS = 0;
TRUNCATE orders;
SET FOREIGN_KEY_CHECKS = 1;

-- PgSQL: TRUNCATE ... CASCADE
TRUNCATE orders CASCADE;  -- also truncates dependent tables

-- ============================================
-- DROP — Remove the entire table
-- ============================================

-- DDL
-- Removes table structure + all data + all indexes + all triggers
-- Cannot be rolled back (in MySQL — DDL auto-commits)
-- PgSQL: CAN be rolled back (transactional DDL)
-- Removes all associated permissions/grants

DROP TABLE orders;
-- Table is gone! Structure, data, indexes, triggers — everything.

DROP TABLE IF EXISTS orders;  -- no error if doesn't exist

DROP TABLE orders CASCADE;    -- PgSQL: also drops dependent views, FKs
DROP TABLE orders RESTRICT;   -- PgSQL: error if anything depends on it (default)

-- ============================================
-- COMPARISON TABLE
-- ============================================

/*
Feature                  | DELETE        | TRUNCATE        | DROP
─────────────────────────┼───────────────┼─────────────────┼──────────────────
Type                     | DML           | DDL             | DDL
Remove rows?             | Selective     | ALL rows        | ALL + structure
Remove structure?        | No            | No              | YES
WHERE clause?            | YES           | No              | No
Rollbackable?            | YES           | PgSQL YES       | PgSQL YES
                         |               | MySQL NO        | MySQL NO
Triggers fire?           | YES           | NO (MySQL)      | No
                         |               | TRUNCATE trigger| (table gone)
                         |               | in PgSQL        |
Auto-increment reset?    | No            | YES             | N/A (gone)
Speed on large table     | Slow (row/row)| Very fast       | Fast
FK constraint check?     | YES           | YES (MySQL)     | YES (unless CASCADE)
Transaction safe?        | YES           | PgSQL only      | PgSQL only
Logs?                    | Full row log  | Minimal         | Minimal
Recover data?            | ROLLBACK      | Hard (MySQL)    | Very hard
When to use?             | Specific rows | Clear all + keep| Remove table entirely
                         |               | structure       |
*/
```

---

## 🔍 Why This Works (3 lines max)
DELETE logs every row deletion for MVCC and triggers — it's fully transactional but slower. TRUNCATE works at the page/extent level (marks data pages as free) — much faster but at the cost of triggers and rollback safety in MySQL. DROP removes the table's metadata from the catalog — once committed, the table definition is gone.
हिंदी: DELETE row-by-row log करता है (slow लेकिन rollback possible)। TRUNCATE pages deallocate करता है (fast, MySQL में rollback नहीं)। DROP पूरा table metadata हटाता है।

---

## ⚡ Alternative Solution

```sql
-- Fast "delete all" with partition swap (advanced zero-downtime technique):
-- Instead of TRUNCATE (which locks):
-- 1. Create empty orders_new table
-- 2. Rename orders → orders_old, orders_new → orders  (atomic)
-- 3. Drop orders_old (background)
-- This approach avoids long locks on large tables.

-- PgSQL TRUNCATE with RESTART IDENTITY:
TRUNCATE orders RESTART IDENTITY;  -- also resets the sequence
TRUNCATE orders RESTART IDENTITY CASCADE;  -- + cascade to dependent tables
```

---

## ⚠️ Common Mistake

```sql
-- ❌ Wrong: Using DELETE to clear a 100M row table in production
DELETE FROM orders;  -- runs for hours, fills transaction log!

-- ✅ Correct: TRUNCATE for full clear (or batched DELETE with limit)
TRUNCATE TABLE orders;  -- milliseconds!

-- ❌ Wrong: Expecting TRUNCATE to fire triggers (e.g., audit log)
TRUNCATE orders;  -- Your BeforeDelete trigger does NOT fire!
-- ✅ Correct: Use DELETE if triggers must fire (audit trail required)
DELETE FROM orders;  -- triggers fire on each row

-- ❌ Wrong: TRUNCATE inside MySQL transaction expecting rollback
BEGIN;
TRUNCATE orders;  -- MySQL: this auto-commits! Can't rollback!
ROLLBACK;         -- Orders are already gone ☠️

-- ✅ Correct in MySQL: don't rely on TRUNCATE being transactional
-- Use PgSQL if you need transactional DDL
```

---

## 🎯 Interview Tip (1 line)
Say: "DELETE is transactional and selective — I use it for business-logic row removal. TRUNCATE is for clearing test data or resetting tables — fast but fires no triggers. I always note that MySQL TRUNCATE auto-commits, so it can't be rolled back in a transaction unlike PostgreSQL where DDL is fully transactional."

---

## 🔗 Related Questions
→ Q015 (soft delete design) | Q145 (soft delete schema) | Q031 (ON DELETE CASCADE) | Q139 (transaction auto-commit)
