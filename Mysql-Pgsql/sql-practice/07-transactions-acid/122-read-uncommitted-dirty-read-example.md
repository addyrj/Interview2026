---

# Q122. READ UNCOMMITTED — Dirty Read Example
# Category: Transactions & ACID
# Difficulty: ⭐⭐ Medium
# DB: Both (behaviour differs: PostgreSQL has no dirty reads)

---

## ❓ Question
Demonstrate a dirty read with two sessions: Session B debits an account but has not committed (and later rolls back), while Session A at READ UNCOMMITTED reads the debited balance. What does PostgreSQL do with the same setting?

---

## 💡 Quick Concept (2 lines only)
READ UNCOMMITTED is the lowest isolation level: a transaction can see changes other transactions have not yet committed (a "dirty read"). If the writer rolls back, the reader has acted on data that never existed.
हिंदी: READ UNCOMMITTED में दूसरी transaction का uncommitted data भी दिख जाता है; writer rollback करे तो आपने ऐसे data पर काम किया जो कभी था ही नहीं।

---

## ✅ Answer / Solution

```sql
-- Verified on MySQL 9.1.0 with TWO real client sessions (A and B started in parallel, timed with SLEEP).
-- PostgreSQL: only the syntax/semantics of the setting were checked on PGlite (single connection),
-- so the two-session PostgreSQL behaviour below is from documentation, NOT run.

-- ============================================
-- SETUP (run this first)
-- ============================================

CREATE TABLE accounts (
  id      INT PRIMARY KEY,
  holder  VARCHAR(50),
  balance DECIMAL(10,2)
) ENGINE=InnoDB;

INSERT INTO accounts VALUES (1, 'Asha', 1000.00), (2, 'Ravi', 500.00);

-- ============================================
-- SOLUTION
-- ============================================

-- ---- Session B (writer) ----                    -- ---- Session A (reader) ----
-- t0: START TRANSACTION;
--     UPDATE accounts SET balance = balance - 900 WHERE id = 1;     -- NOT committed
--                                                  -- t1:
--                                                  SET SESSION TRANSACTION ISOLATION LEVEL READ UNCOMMITTED;
--                                                  START TRANSACTION;
--                                                  SELECT balance FROM accounts WHERE id = 1;   -- DIRTY READ
-- t2: ROLLBACK;
--                                                  -- t3:
--                                                  SELECT balance FROM accounts WHERE id = 1;   -- back to normal
--                                                  COMMIT;

-- Exact scripts that were run (A sleeps 1s, reads, sleeps 2s, reads; B updates, sleeps 2s, rolls back):
SET SESSION TRANSACTION ISOLATION LEVEL READ UNCOMMITTED;   -- must be set BEFORE START TRANSACTION
START TRANSACTION;
SELECT 'A reads (B uncommitted)' AS step, balance FROM accounts WHERE id = 1;

-- Check the current level:
SELECT @@transaction_isolation;      -- MySQL 8.0+ (older: @@tx_isolation)

-- ============================================
-- EXPECTED OUTPUT
-- ============================================

-- A reads (B uncommitted) | 100.00      <- dirty: 1000 - 900, B had NOT committed
-- A reads (B rolled back) | 1000.00     <- the 100.00 never officially existed
-- Server default (real): @@transaction_isolation = REPEATABLE-READ
--
-- PostgreSQL (verified on PGlite): BEGIN ISOLATION LEVEL READ UNCOMMITTED; SHOW transaction_isolation;
-- -> read uncommitted     (accepted, but it behaves exactly like READ COMMITTED: dirty reads impossible)
```

---

## 🔍 Why This Works (3 lines max)
InnoDB at READ UNCOMMITTED reads the latest row version in the page without checking whether its transaction has committed, so B's in-flight UPDATE is visible. PostgreSQL's MVCC always filters by commit status, so it maps READ UNCOMMITTED up to READ COMMITTED.
हिंदी: MySQL latest row version बिना commit check किए पढ़ता है; PostgreSQL MVCC में dirty read संभव ही नहीं, वहाँ यह level READ COMMITTED जैसा चलता है।

---

## ⚡ Alternative Solution

```sql
-- Control experiment (MySQL, verified earlier in the same setup): at READ COMMITTED the same
-- reader would see 1000.00 at t1 (committed value) - no dirty read.
SET SESSION TRANSACTION ISOLATION LEVEL READ COMMITTED;

-- Per-transaction (applies to the NEXT transaction only):
SET TRANSACTION ISOLATION LEVEL READ UNCOMMITTED;
START TRANSACTION;
-- ...
COMMIT;

-- PostgreSQL syntax (inside the transaction block):
BEGIN ISOLATION LEVEL READ UNCOMMITTED;     -- same as READ COMMITTED in practice
-- or: BEGIN; SET TRANSACTION ISOLATION LEVEL READ COMMITTED;

-- Legit use of READ UNCOMMITTED: rough monitoring/approximate counts on huge tables where an
-- off-by-a-few number is acceptable and you must not take any read locks (rare, MySQL only).
```

---

## ⚠️ Common Mistake
```sql
-- ❌ Setting the level AFTER the transaction started (MySQL):
START TRANSACTION;
SET TRANSACTION ISOLATION LEVEL READ UNCOMMITTED;   -- ERROR 1568: Transaction characteristics can't be changed while a transaction is in progress
-- ✅ Set it first: SET SESSION TRANSACTION ISOLATION LEVEL ...; then START TRANSACTION;

-- ❌ Using READ UNCOMMITTED for money/inventory/permission checks: you can approve an order
--    against a balance that gets rolled back a moment later.
-- ❌ Believing it removes locking cost for writes: writers still take row locks; only plain
--    SELECTs skip the snapshot/consistency work.
-- ✅ Default to READ COMMITTED (PostgreSQL default) or REPEATABLE READ (MySQL default).
```

---

## 🎯 Interview Tip (1 line)
Say: "Dirty reads only exist at READ UNCOMMITTED in MySQL/InnoDB; PostgreSQL silently upgrades it to READ COMMITTED, and I would almost never use it except for throwaway monitoring queries."

---

## 🔗 Related Questions
→ Q121 (Isolation levels) | Q123 (READ COMMITTED non-repeatable read) | Q124 (Phantom read) | Q125 (SERIALIZABLE cost)
