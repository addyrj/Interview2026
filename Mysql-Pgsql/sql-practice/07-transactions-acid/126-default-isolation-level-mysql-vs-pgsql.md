---

# Q126. Default Isolation Level — MySQL vs PgSQL
# Category: Transactions & ACID
# Difficulty: ⭐⭐ Medium
# DB: Both (MySQL 8.0+ | PostgreSQL)

---

## ❓ Question
What is the default transaction isolation level in MySQL (InnoDB) and in PostgreSQL? Show how to check it, change it, and demonstrate the practical difference with a non-repeatable read on an `accounts` table.

---

## 💡 Quick Concept (2 lines only)
MySQL InnoDB defaults to REPEATABLE READ (one snapshot per transaction); PostgreSQL defaults to READ COMMITTED (new snapshot per statement). Same app code can therefore see different data in the two databases.
हिंदी: MySQL का default REPEATABLE READ है, PostgreSQL का READ COMMITTED — इसलिए same code दोनों में अलग data देख सकता है।

---

## ✅ Answer / Solution

```sql
-- ============================================
-- SETUP (run this first) — works in MySQL and PostgreSQL
-- ============================================

CREATE TABLE accounts (
  id      INT PRIMARY KEY,
  owner   VARCHAR(50),
  balance DECIMAL(10,2)
);

INSERT INTO accounts VALUES (1, 'Alice', 1000), (2, 'Bob', 500);

-- ============================================
-- SOLUTION
-- ============================================

-- Step 1: check the current default
-- MySQL 8.0+ (older 5.7 used @@tx_isolation):
SELECT @@transaction_isolation;      -- global default is also @@global.transaction_isolation
-- PostgreSQL:
SHOW default_transaction_isolation;  -- or SHOW transaction_isolation inside a txn

-- Result:
-- MySQL      -> REPEATABLE-READ      (real output, MySQL 9.1)
-- PostgreSQL -> read committed       (real output, PGlite = PostgreSQL 18)

-- Step 2: change it — ONLY before the first statement of the transaction
-- MySQL (applies to the NEXT transaction of this session):
SET SESSION TRANSACTION ISOLATION LEVEL READ COMMITTED;
-- PostgreSQL (inside the transaction, before any query):
--   BEGIN ISOLATION LEVEL REPEATABLE READ;      -- verified: SHOW transaction_isolation -> repeatable read

-- Step 3: demo with TWO sessions (A and B), default levels
-- Session A: START TRANSACTION;  SELECT balance FROM accounts WHERE id = 1;   -- 1000.00
-- Session B: UPDATE accounts SET balance = 900 WHERE id = 1;  COMMIT;
-- Session A: SELECT balance FROM accounts WHERE id = 1;
--
-- ============================================
-- EXPECTED OUTPUT
-- ============================================
-- MySQL default (REPEATABLE READ), second read in A:   1000.00   <- same snapshot (verified)
-- MySQL after SET ... READ COMMITTED, second read in A: new value (900.00 -> 800.00 in my run) (verified)
-- PostgreSQL default (READ COMMITTED), second read in A: 900.00  <- sees B's commit
--   (PG two-session demo NOT run here: PGlite is a single connection. Behaviour is documented PG semantics.)
-- Isolation level names accepted by both: READ UNCOMMITTED, READ COMMITTED, REPEATABLE READ, SERIALIZABLE
-- (PG treats READ UNCOMMITTED as READ COMMITTED — there are no dirty reads in PG)
```

---

## 🔍 Why This Works (3 lines max)
InnoDB takes its read snapshot at the first consistent read of the transaction and reuses it; PostgreSQL takes a fresh snapshot for every statement at READ COMMITTED. PG's REPEATABLE READ is snapshot isolation and also prevents phantoms; MySQL's uses gap locks only for locking reads.
हिंदी: InnoDB पूरे transaction के लिए एक snapshot रखता है, PostgreSQL हर statement पर नया snapshot लेता है।

---

## ⚡ Alternative Solution

```sql
-- Change the default for ALL new sessions
-- MySQL (my.cnf):  transaction-isolation = READ-COMMITTED
-- MySQL runtime:   SET GLOBAL transaction_isolation = 'READ-COMMITTED';  (needs privilege, new sessions only)
-- PostgreSQL:      ALTER DATABASE shop SET default_transaction_isolation = 'repeatable read';
--                  (or default_transaction_isolation in postgresql.conf)

-- Per-transaction, one-shot, both databases accept this:
START TRANSACTION ISOLATION LEVEL SERIALIZABLE;   -- MySQL
BEGIN ISOLATION LEVEL SERIALIZABLE;               -- PostgreSQL
```

---

## ⚠️ Common Mistake

```sql
-- ❌ Wrong: setting isolation AFTER the transaction has started
START TRANSACTION;
SET TRANSACTION ISOLATION LEVEL SERIALIZABLE;
-- MySQL: ERROR 1568: Transaction characteristics can't be changed while a transaction is in progress (seen via mysql2)
-- PG:    ERROR: SET TRANSACTION ISOLATION LEVEL must be called before any query (seen in PGlite)

-- ❌ Wrong: assuming SERIALIZABLE just works the same everywhere
-- MySQL SERIALIZABLE turns plain SELECT into SELECT ... FOR SHARE (blocking);
-- PG SERIALIZABLE (SSI) never blocks reads but can abort with error 40001 -> app MUST retry.
-- ✅ Set the level first, and write retry logic for serialization failures / deadlocks.
```

---

## 🎯 Interview Tip (1 line)
Say: "MySQL defaults to REPEATABLE READ and PG to READ COMMITTED, so when we migrate I re-test read-modify-write code paths, and I use SELECT ... FOR UPDATE or SERIALIZABLE-with-retry for anything where lost updates matter."

---

## 🔗 Related Questions
→ Q121 (Isolation levels) | Q127 (Optimistic vs pessimistic) | Q134 (MVCC) | Q129 (Deadlock example)
