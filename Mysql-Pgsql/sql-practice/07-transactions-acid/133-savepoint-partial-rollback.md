---

# Q133. SAVEPOINT — Partial Rollback
# Category: Transactions & ACID
# Difficulty: ⭐⭐ Medium
# DB: Both (MySQL 8.0+ | PostgreSQL) — verified on MySQL 9.1.0 and PGlite (Postgres)

---

## ❓ Question
A money-transfer transaction has several steps. If an optional step (e.g. loyalty bonus) fails, you want to undo only that step and still commit the rest. How do you do a partial rollback inside one transaction? What happens to a PostgreSQL transaction after an error, and what silently destroys savepoints in MySQL?

---

## 💡 Quick Concept (2 lines only)
SAVEPOINT marks a point inside a transaction; ROLLBACK TO SAVEPOINT undoes only the work after that mark while the transaction stays open. RELEASE SAVEPOINT just forgets the mark (nothing is committed).
हिंदी: SAVEPOINT transaction के अंदर एक checkpoint है; ROLLBACK TO से सिर्फ उसके बाद का काम undo होता है, पूरा transaction नहीं।

---

## ✅ Answer / Solution

```sql
-- ============================================
-- SETUP (run this first)
-- ============================================

CREATE TABLE accounts (
  id      INT PRIMARY KEY,
  holder  VARCHAR(50),
  balance DECIMAL(10,2)       -- PgSQL: NUMERIC(10,2) (DECIMAL also works)
);

INSERT INTO accounts VALUES
  (1, 'Asha', 1000.00),
  (2, 'Ravi',  500.00);

-- ============================================
-- SOLUTION (MySQL)
-- ============================================

-- Step 1: open transaction, do the mandatory debit
-- Step 2: set a savepoint BEFORE the risky/optional step
-- Step 3: optional step does nothing useful -> roll back only to savepoint
-- Step 4: continue and COMMIT; the debit survives

BEGIN;                                                    -- MySQL: BEGIN or START TRANSACTION
UPDATE accounts SET balance = balance - 100 WHERE id = 1; -- mandatory debit
SAVEPOINT after_debit;
UPDATE accounts SET balance = balance + 100 WHERE id = 99; -- optional step, wrong id -> 0 rows
SELECT ROW_COUNT() AS rows_hit;                           -- MySQL only; app checks this
ROLLBACK TO SAVEPOINT after_debit;                        -- undo only the optional step
SELECT * FROM accounts ORDER BY id;

SAVEPOINT s2;
UPDATE accounts SET balance = balance + 100 WHERE id = 2; -- credit the receiver
RELEASE SAVEPOINT s2;                                     -- drop the mark, work is kept
COMMIT;
SELECT * FROM accounts ORDER BY id;

-- ============================================
-- EXPECTED OUTPUT (real MySQL 9.1.0 output)
-- ============================================

-- rows_hit
-- --------
-- 0
--
-- After ROLLBACK TO SAVEPOINT (debit still pending, inside txn):
-- id | holder | balance
-- ---+--------+--------
-- 1  | Asha   | 900.00
-- 2  | Ravi   | 500.00
--
-- After COMMIT:
-- id | holder | balance
-- ---+--------+--------
-- 1  | Asha   | 900.00
-- 2  | Ravi   | 600.00
```

---

## 🔍 Why This Works (3 lines max)
Savepoints form a stack inside one transaction; ROLLBACK TO undoes changes made after that mark and discards later savepoints, but the transaction (and locks held so far) stay alive. Only the final COMMIT makes anything durable.
हिंदी: Savepoint stack की तरह काम करते हैं; ROLLBACK TO के बाद transaction चालू रहता है और आख़िर में COMMIT ही सब durable करता है।

---

## ⚡ Alternative Solution

```sql
-- PostgreSQL: a failed statement ABORTS the whole transaction.
-- A savepoint is the only way to "catch" the error and continue.
-- (Run on PGlite / Postgres; errors shown are the real messages.)

BEGIN;
UPDATE accounts SET balance = balance - 100 WHERE id = 1;
SAVEPOINT after_debit;
INSERT INTO accounts VALUES (1, 'Dup', 0);   -- ERROR: duplicate key value violates unique constraint "accounts_pkey"
ROLLBACK TO SAVEPOINT after_debit;           -- transaction is healthy again
SELECT * FROM accounts ORDER BY id;          -- Asha 900.00, Ravi 500.00
COMMIT;

-- Without the savepoint (PostgreSQL):
BEGIN;
INSERT INTO accounts VALUES (1, 'Dup', 0);   -- ERROR: duplicate key ...
SELECT 1;                                    -- ERROR: current transaction is aborted,
                                             --        commands ignored until end of transaction block
ROLLBACK;

-- MySQL differs: a failed statement only rolls back THAT statement; the
-- transaction stays usable without any savepoint.
-- Savepoint names are case-insensitive in MySQL; PgSQL also allows reuse of a name
-- (the newer one shadows the older).

-- Application note: ORMs (Sequelize/Prisma/Django/psycopg) implement "nested
-- transactions" using SAVEPOINT sp_1, sp_2, ... under the hood.
```

---

## ⚠️ Common Mistake

```sql
-- ❌ Wrong: DDL inside a MySQL transaction, then rolling back to a savepoint
BEGIN;
UPDATE accounts SET balance = 0 WHERE id = 1;
SAVEPOINT sp1;
CREATE TABLE tmp_x (a INT);          -- DDL = implicit COMMIT in MySQL!
ROLLBACK TO SAVEPOINT sp1;           -- ERROR 1305: SAVEPOINT sp1 does not exist
-- The balance = 0 update was already COMMITTED (we verified: Asha's balance stayed 0.00).

-- ✅ Correct: keep DDL outside the transaction. (PgSQL has transactional DDL,
--    so CREATE TABLE can be rolled back there - one of PgSQL's big advantages.)

-- ❌ Also wrong: thinking RELEASE SAVEPOINT commits the work.
-- ✅ RELEASE only removes the marker; data is durable only after COMMIT.
```

---

## 🎯 Interview Tip (1 line)
Say: "In PostgreSQL an error poisons the whole transaction, so I wrap risky statements in a savepoint (that's how ORM nested transactions work); in MySQL I remember that DDL causes an implicit commit and wipes savepoints, and that savepoints don't release locks already taken."

---

## 🔗 Related Questions
→ Q121 (Isolation levels) | Q129 (Deadlock example) | Q134 (MVCC) | Q140 (Transactions in Node.js ORMs)
