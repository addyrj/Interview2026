---

# Q017. SELECT FOR UPDATE — What Does It Do?
# Category: Fundamentals (Locking)
# Difficulty: ⭐⭐ Medium
# DB: Both (MySQL 8.0+ InnoDB | PostgreSQL)

---

## ❓ Question
What does `SELECT ... FOR UPDATE` do? Show how it blocks a concurrent writer, how `NOWAIT` and `SKIP LOCKED` change the behaviour, and when you would use each (e.g. money transfer, job queue).

---

## 💡 Quick Concept (2 lines only)
`FOR UPDATE` takes row-level exclusive locks on the rows the SELECT returns until COMMIT/ROLLBACK, so other sessions cannot update/delete/`FOR UPDATE` them (plain non-locking reads still work). It turns "read, then write" into a safe critical section.
हिंदी: FOR UPDATE selected rows पर exclusive lock लगाता है, transaction खत्म होने तक कोई दूसरा उन्हें बदल नहीं सकता।

---

## ✅ Answer / Solution

```sql
-- ============================================
-- SETUP (run this first; works on MySQL and PostgreSQL)
-- ============================================

CREATE TABLE accounts (
  id      INT PRIMARY KEY,
  holder  VARCHAR(50),
  balance DECIMAL(12,2)          -- PgSQL: DECIMAL == NUMERIC
);

INSERT INTO accounts VALUES (1, 'Asha', 5000), (2, 'Bala', 3000), (3, 'Chitra', 1000);

-- ============================================
-- SOLUTION  (needs TWO sessions: A and B)
-- ============================================

-- Session A: lock row 1 and hold it
START TRANSACTION;                          -- PgSQL also accepts BEGIN
SELECT id, balance FROM accounts WHERE id = 1 FOR UPDATE;
-- id | balance
-- 1  | 5000.00
-- ... A is still working (e.g. app computes new balance) ...

-- Session B (while A is open):

-- (a) plain read -> NOT blocked (InnoDB/Postgres use MVCC snapshots)
SELECT * FROM accounts WHERE id = 1;
-- 1 | Asha | 5000.00

-- (b) another FOR UPDATE / UPDATE on row 1 -> BLOCKS until A commits
SELECT * FROM accounts WHERE id = 1 FOR UPDATE;
-- MySQL after innodb_lock_wait_timeout (default 50s):
-- ERROR 1205 (HY000): Lock wait timeout exceeded; try restarting transaction
-- PgSQL: waits indefinitely unless lock_timeout is set

-- (c) NOWAIT -> fail immediately instead of waiting
SELECT * FROM accounts WHERE id = 1 FOR UPDATE NOWAIT;
-- MySQL:  ERROR 3572 (HY000): Statement aborted because lock(s) could not be acquired immediately and NOWAIT is set.
-- PgSQL:  ERROR: could not obtain lock on row in relation "accounts"   (SQLSTATE 55P03)

-- (d) SKIP LOCKED -> silently skip rows locked by others
SELECT * FROM accounts FOR UPDATE SKIP LOCKED;
-- id | holder | balance
-- 2  | Bala   | 3000.00
-- 3  | Chitra | 1000.00          <- row 1 skipped because A holds it

-- Session A finishes:
UPDATE accounts SET balance = balance - 500 WHERE id = 1;
COMMIT;                                    -- locks released, B (b) now proceeds

SELECT * FROM accounts WHERE id = 1;
-- 1 | Asha | 4500.00

-- ============================================
-- EXPECTED OUTPUT
-- ============================================
-- MySQL 9.1.0 run with two real sessions: (a) returned 5000.00 while A held the lock,
-- (b) with innodb_lock_wait_timeout=2 gave ERROR 1205, (c) gave ERROR 3572,
-- (d) returned only ids 2 and 3, final balance 4500.00.
-- PostgreSQL (PGlite is single-connection): syntax of FOR UPDATE / SKIP LOCKED / NOWAIT /
-- FOR SHARE / FOR NO KEY UPDATE was run and returns rows when uncontended;
-- the blocking/error behaviour in the PgSQL lines above is NOT verified here.
```

---

## 🔍 Why This Works (3 lines max)
The lock is stored on the index records/tuples that matched the WHERE; other writers queue behind it. Plain SELECTs read an MVCC snapshot so they never block. Always lock by PRIMARY KEY or an indexed column — in InnoDB an unindexed WHERE locks every row scanned.
हिंदी: Lock matched rows पर रहता है, normal SELECT block नहीं होता; WHERE में index जरूर रखो।

---

## ⚡ Alternative Solution

```sql
-- Job queue: many workers, each grabs ONE unclaimed job without blocking the others
CREATE TABLE jobs (
  id      INT PRIMARY KEY AUTO_INCREMENT,   -- PgSQL: id SERIAL PRIMARY KEY
  payload VARCHAR(30),
  status  VARCHAR(10) DEFAULT 'queued'
);

START TRANSACTION;
SELECT id, payload FROM jobs
WHERE status = 'queued'
ORDER BY id
LIMIT 1
FOR UPDATE SKIP LOCKED;                      -- MySQL 8.0+, PgSQL 9.5+
-- ... process, then:
UPDATE jobs SET status = 'done' WHERE id = 1;
COMMIT;

-- PgSQL-only lock strengths:
SELECT * FROM accounts WHERE id = 2 FOR NO KEY UPDATE;  -- weaker: does not block FK inserts referencing the row
SELECT * FROM accounts WHERE id = 2 FOR SHARE;          -- shared lock (MySQL 8: FOR SHARE; older: LOCK IN SHARE MODE)
SELECT * FROM accounts FOR UPDATE OF accounts;          -- with joins: lock only the named table

-- Optimistic alternative: no lock, check a version column
UPDATE accounts SET balance = 4500, version = version + 1 WHERE id = 1 AND version = 7;  -- 0 rows => retry
```

---

## ⚠️ Common Mistake

```sql
-- ❌ Wrong: FOR UPDATE in autocommit mode — lock is released immediately after the statement
SELECT balance FROM accounts WHERE id = 1 FOR UPDATE;   -- no BEGIN => no protection
UPDATE accounts SET balance = 4500 WHERE id = 1;        -- race with another session

-- ❌ Wrong: unindexed WHERE in InnoDB locks many rows / gaps (REPEATABLE READ gap locks => deadlocks)
SELECT * FROM accounts WHERE holder = 'Asha' FOR UPDATE;   -- no index on holder

-- ✅ Correct: BEGIN; SELECT ... WHERE <pk or indexed col> FOR UPDATE; UPDATE; COMMIT;
--    and lock rows in a consistent order (ORDER BY id) to avoid deadlocks.
```

---

## 🎯 Interview Tip (1 line)
Say: "I use FOR UPDATE for read-modify-write on hot rows, always inside a short transaction on an indexed key with consistent lock ordering; SKIP LOCKED for work queues, NOWAIT for fail-fast, and I prefer optimistic versioning when contention is low."

---

## 🔗 Related Questions
→ Q016 (RETURNING) | Q018 (CTE) | Q011 (Keyset pagination) | Isolation levels / deadlocks questions in the transactions section
