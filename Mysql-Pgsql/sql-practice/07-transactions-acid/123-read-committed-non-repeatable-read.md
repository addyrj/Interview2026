---

# Q123. READ COMMITTED — Non-Repeatable Read
# Category: Transactions & ACID
# Difficulty: ⭐⭐ Medium
# DB: Both

---

## ❓ Question
Show a non-repeatable read: within one transaction the same `SELECT` returns different values because another transaction committed in between. Compare READ COMMITTED with REPEATABLE READ and explain the default level of each database.

---

## 💡 Quick Concept (2 lines only)
At READ COMMITTED every statement gets a fresh snapshot of committed data, so re-reading a row inside one transaction can return a new value. REPEATABLE READ takes one snapshot at the first read and keeps it for the whole transaction.
हिंदी: READ COMMITTED में हर statement को नया snapshot मिलता है, इसलिए एक ही transaction में वही row दो बार पढ़ने पर अलग value आ सकती है; REPEATABLE READ में snapshot एक ही रहता है।

---

## ✅ Answer / Solution

```sql
-- Verified on MySQL 9.1.0 with two real parallel client sessions (SLEEP used for ordering).
-- PostgreSQL: statements/syntax checked on PGlite, but PGlite has ONE connection, so the two-session
-- result for PostgreSQL is documented behaviour and was NOT run.

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

-- Timeline (A = reader, B = writer)
--   A: SET SESSION TRANSACTION ISOLATION LEVEL READ COMMITTED;
--   A: START TRANSACTION;
--   A: SELECT balance FROM accounts WHERE id = 1;          -- read #1  -> 1000.00
--   B: START TRANSACTION;
--   B: UPDATE accounts SET balance = balance - 300 WHERE id = 1;
--   B: COMMIT;
--   A: SELECT balance FROM accounts WHERE id = 1;          -- read #2  -> different!
--   A: COMMIT;

-- Session A script (run in the first terminal; Session B runs its part ~1 sec later):
SET SESSION TRANSACTION ISOLATION LEVEL READ COMMITTED;     -- PostgreSQL: BEGIN ISOLATION LEVEL READ COMMITTED;
START TRANSACTION;
SELECT 'A read 1' AS step, balance FROM accounts WHERE id = 1;
SELECT SLEEP(2);                                            -- window for B to commit
SELECT 'A read 2' AS step, balance FROM accounts WHERE id = 1;
COMMIT;
SELECT 'A after commit' AS step, balance FROM accounts WHERE id = 1;

-- Session B script:
START TRANSACTION;
UPDATE accounts SET balance = balance - 300 WHERE id = 1;
COMMIT;

-- Repeat with: SET SESSION TRANSACTION ISOLATION LEVEL REPEATABLE READ;  for the comparison.

-- ============================================
-- EXPECTED OUTPUT
-- ============================================

-- READ COMMITTED (real):                 -- REPEATABLE READ (real):
-- A read 1       | 1000.00               -- A read 1       | 1000.00
-- A read 2       |  700.00   <- changed  -- A read 2       | 1000.00   <- same snapshot
-- A after commit |  700.00               -- A after commit |  700.00   <- new transaction sees it
```

---

## 🔍 Why This Works (3 lines max)
READ COMMITTED builds a new read view for each statement, so B's committed change becomes visible to A's second SELECT. REPEATABLE READ builds the read view once (at A's first consistent read) and reuses it until A commits.
हिंदी: READ COMMITTED हर statement पर नया read view बनाता है, REPEATABLE READ पूरी transaction में पहला view ही रखता है।

---

## ⚡ Alternative Solution

```sql
-- Defaults:  MySQL/InnoDB = REPEATABLE READ (verified: @@transaction_isolation = REPEATABLE-READ)
--            PostgreSQL   = READ COMMITTED  (verified: SHOW default_transaction_isolation -> read committed)

-- Why a non-repeatable read is dangerous: check-then-act logic
--   A: SELECT balance FROM accounts WHERE id = 1;     -- 1000, "enough for 800 withdrawal"
--   B: commits a 300 debit
--   A: UPDATE accounts SET balance = balance - 800 ... -- negative balance if no guard
-- Fix 1: guard in the write itself
UPDATE accounts SET balance = balance - 800 WHERE id = 1 AND balance >= 800;   -- check ROW_COUNT()
-- Fix 2: lock the row when you read it
SELECT balance FROM accounts WHERE id = 1 FOR UPDATE;    -- works in both databases
-- Fix 3: use REPEATABLE READ / SERIALIZABLE (PostgreSQL: expect "could not serialize access" errors, retry)

-- PostgreSQL syntax verified: BEGIN ISOLATION LEVEL REPEATABLE READ READ ONLY; SHOW transaction_isolation;
-- -> repeatable read
-- Change server-wide default:  SET default_transaction_isolation = 'repeatable read';  (PgSQL)
--                              transaction_isolation = READ-COMMITTED in my.cnf        (MySQL)
```

---

## ⚠️ Common Mistake
```sql
-- ❌ Computing a report across several SELECTs at READ COMMITTED: totals from query 1 and
--    query 2 come from different moments, so they do not add up.
-- ✅ Run the whole report in one REPEATABLE READ (read-only) transaction, or in a single SQL statement.

-- ❌ "UPDATE ... balance = <value read earlier in app>" (lost update).
-- ✅ UPDATE accounts SET balance = balance - 300 WHERE id = 1;     -- atomic, based on current row

-- ❌ Assuming that PostgreSQL REPEATABLE READ behaves like MySQL's: PostgreSQL gives snapshot
--    isolation for ALL statements (and errors on write conflict), while MySQL plain SELECT uses
--    the snapshot but UPDATE/SELECT FOR UPDATE read the LATEST committed data (see Q124).
```

---

## 🎯 Interview Tip (1 line)
Say: "READ COMMITTED prevents dirty reads but allows non-repeatable reads and phantoms; I accept that for most OLTP and protect check-then-act logic with atomic UPDATEs, SELECT ... FOR UPDATE, or optimistic version columns instead of raising the isolation level globally."

---

## 🔗 Related Questions
→ Q121 (Isolation levels) | Q122 (Dirty read) | Q124 (Phantom read) | Q129 (Deadlock example)
