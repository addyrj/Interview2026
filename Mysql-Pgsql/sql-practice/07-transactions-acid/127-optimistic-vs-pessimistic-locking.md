---

# Q127. Optimistic vs Pessimistic Locking
# Category: Transactions & ACID
# Difficulty: ⭐⭐ Medium
# DB: Both (MySQL 8.0+ | PostgreSQL)

---

## ❓ Question
Two users edit the same product's stock at the same time. Show how to prevent a lost update with (1) pessimistic locking (`SELECT ... FOR UPDATE`) and (2) optimistic locking (a `version` column). When do you pick which?

---

## 💡 Quick Concept (2 lines only)
Pessimistic = lock the row first, then work (others wait). Optimistic = no lock, work freely, and at UPDATE time check the row has not changed (version/timestamp); if it has, retry.
हिंदी: Pessimistic = पहले lock, फिर काम। Optimistic = बिना lock काम, UPDATE के समय version check, मिसमैच पर retry।

---

## ✅ Answer / Solution

```sql
-- ============================================
-- SETUP (run this first) — MySQL and PostgreSQL
-- ============================================

CREATE TABLE products (
  id      INT PRIMARY KEY,
  name    VARCHAR(50),
  stock   INT,
  version INT NOT NULL DEFAULT 1      -- used only by the optimistic approach
);

INSERT INTO products VALUES (1, 'Keyboard', 10, 1);

-- ============================================
-- SOLUTION 1: PESSIMISTIC (row lock)
-- ============================================

START TRANSACTION;                    -- PostgreSQL: BEGIN;
-- Step 1: lock the row; a second session running this waits until we COMMIT
SELECT stock FROM products WHERE id = 1 FOR UPDATE;
-- Step 2: app checks stock >= 1, then decrements safely
UPDATE products SET stock = stock - 1 WHERE id = 1;
COMMIT;

-- ============================================
-- SOLUTION 2: OPTIMISTIC (version check)
-- ============================================

-- Step 1: read without locking; app remembers version = 1
SELECT stock, version FROM products WHERE id = 1;

-- Step 2: write only if nobody changed the row since we read it
UPDATE products
SET stock = 9, version = version + 1
WHERE id = 1 AND version = 1;         -- <- the whole trick
-- Step 3: check affected rows; 0 means we lost the race -> re-read and retry
--   MySQL: SELECT ROW_COUNT();  (drivers expose affectedRows)
--   PG:    command tag "UPDATE 0" (drivers expose rowCount)

-- Second writer with the stale version:
UPDATE products
SET stock = 8, version = version + 1
WHERE id = 1 AND version = 1;         -- matches nothing now

-- ============================================
-- EXPECTED OUTPUT (real MySQL 9.1 run)
-- ============================================
-- First optimistic UPDATE  -> rows_affected = 1
-- Stale optimistic UPDATE  -> rows_affected = 0   <- conflict detected, app must retry
-- SELECT * FROM products:
-- id | name     | stock | version
-- 1  | Keyboard | 9     | 2
-- (Numbers are from running the optimistic block alone, starting at stock=10, version=1.
--  The FOR UPDATE wait itself needs two sessions — see Q128 for a two-session run.)
```

---

## 🔍 Why This Works (3 lines max)
`FOR UPDATE` makes the database serialize writers on that row, which is safe but holds locks while the app thinks. The version check turns the UPDATE itself into a compare-and-swap, so no lock is held between read and write.
हिंदी: FOR UPDATE row को block रखता है; version column UPDATE को compare-and-swap बना देता है।

---

## ⚡ Alternative Solution

```sql
-- Single atomic statement: no read-modify-write gap at all (best when logic is simple)
UPDATE products SET stock = stock - 1 WHERE id = 1 AND stock > 0;   -- affected rows 0 => out of stock

-- Optimistic with a timestamp instead of an integer
-- MySQL:  updated_at TIMESTAMP(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6)
-- PG:     updated_at TIMESTAMPTZ NOT NULL DEFAULT now()   (needs a trigger to auto-update; integer version is simpler)
```

---

## ⚠️ Common Mistake

```sql
-- ❌ Wrong: read-modify-write with no lock and no version check
SELECT stock FROM products WHERE id = 1;          -- both sessions read 10
UPDATE products SET stock = 9 WHERE id = 1;       -- both write 9 -> one decrement is LOST

-- ❌ Wrong: optimistic update but ignoring affected rows = 0
-- The app thinks it saved; nothing changed. Always check the row count.

-- ✅ Use FOR UPDATE, or a version predicate, or a relative update (stock = stock - 1)
```

---

## 🎯 Interview Tip (1 line)
Say: "Optimistic when conflicts are rare and transactions span user think-time (web forms, ORMs with @Version); pessimistic when contention is high or the cost of a retry is big (inventory, seat booking) — and I keep pessimistic transactions short."

---

## 🔗 Related Questions
→ Q128 (FOR UPDATE vs FOR SHARE) | Q242 (How SELECT FOR UPDATE works) | Q017 (SELECT FOR UPDATE) | Q126 (Default isolation)
