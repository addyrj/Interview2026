---

# Q242. How Does SELECT FOR UPDATE Work?
# Category: Interview Classics
# Difficulty: ⭐⭐⭐ Hard
# DB: Both (MySQL 8.0+ for NOWAIT / SKIP LOCKED | PostgreSQL 9.5+)

---

## ❓ Question
How does SELECT ... FOR UPDATE work? Show a safe money transfer, what a second session sees (block, NOWAIT, SKIP LOCKED), and the job-queue pattern.

---

## 💡 Quick Concept (2 lines only)
FOR UPDATE takes row-level write locks on the selected rows until COMMIT/ROLLBACK, so other writers or other FOR UPDATE readers wait. It prevents lost updates in read-modify-write logic; NOWAIT errors immediately and SKIP LOCKED ignores locked rows.
हिंदी: FOR UPDATE चुनी हुई rows को transaction ख़त्म होने तक lock कर देता है; दूसरा session wait, error या skip करता है।

---

## ✅ Answer / Solution

```sql
-- ============================================
-- SETUP (MySQL; PostgreSQL: SERIAL instead of AUTO_INCREMENT, NUMERIC instead of DECIMAL)
-- ============================================

CREATE TABLE accounts (id INT PRIMARY KEY, owner VARCHAR(50), balance DECIMAL(10,2));
INSERT INTO accounts VALUES (1,'Asha',1000.00),(2,'Ravi',500.00);

CREATE TABLE jobs (id INT PRIMARY KEY AUTO_INCREMENT, payload VARCHAR(50), status VARCHAR(20));
INSERT INTO jobs (payload,status) VALUES ('send-email-1','queued'),('send-email-2','queued'),('send-email-3','queued');

-- ============================================
-- SOLUTION
-- ============================================

-- Step 1: SESSION A - lock the row, then read-modify-write safely
START TRANSACTION;                                    -- PostgreSQL: BEGIN;
SELECT id, balance FROM accounts WHERE id = 1 FOR UPDATE;   -- row 1 locked until COMMIT
-- ... app checks balance >= 100 ...
UPDATE accounts SET balance = balance - 100 WHERE id = 1;
COMMIT;

-- Step 2: SESSION B, started while A still holds the lock on id=1 (observed on MySQL 9.1, two clients):
SET SESSION innodb_lock_wait_timeout = 2;
START TRANSACTION;
SELECT id, balance FROM accounts WHERE id = 2 FOR UPDATE;               -- other row: instant
-- id | balance
-- 2  | 500.00

SELECT id, balance FROM accounts WHERE id = 1 FOR UPDATE NOWAIT;
-- ERROR 3572 (HY000): Statement aborted because lock(s) could not be acquired immediately and NOWAIT is set.

SELECT id, balance FROM accounts WHERE id = 1 FOR UPDATE SKIP LOCKED;   -- empty set, locked row skipped

SELECT id, balance FROM accounts WHERE id = 1 FOR UPDATE;               -- plain: waits...
-- ERROR 1205 (HY000): Lock wait timeout exceeded; try restarting transaction
-- (without the timeout it would just block until A commits, then return the NEW balance 900.00)
ROLLBACK;

-- Final state after A committed:  id=1 balance 900.00 | id=2 balance 500.00

-- Step 3: queue pattern - 2 workers never take the same job (observed, MySQL 9.1)
-- Worker 1:
START TRANSACTION;
SELECT id FROM jobs WHERE status = 'queued' ORDER BY id LIMIT 1 FOR UPDATE;   -- gets job 1
UPDATE jobs SET status = 'running' WHERE id = 1;
-- Worker 2 (while worker 1 is still open):
START TRANSACTION;
SELECT id, payload FROM jobs WHERE status = 'queued' ORDER BY id LIMIT 1 FOR UPDATE SKIP LOCKED;
-- id | payload
-- 2  | send-email-2          <- skipped locked job 1, took job 2, no waiting

-- PostgreSQL atomic claim in one statement (RETURNING; run on PGlite, single connection, so
-- the concurrent behaviour itself was NOT verified there, only the syntax and result):
UPDATE jobs SET status = 'running'
WHERE id = (SELECT id FROM jobs WHERE status = 'queued' ORDER BY id LIMIT 1 FOR UPDATE SKIP LOCKED)
RETURNING id, payload, status;
-- id | payload      | status
-- 1  | send-email-1 | running

-- PostgreSQL lock strengths: FOR UPDATE | FOR NO KEY UPDATE | FOR SHARE | FOR KEY SHARE
-- (FOR NO KEY UPDATE does not block FK checks from child inserts; use it when you don't change keys.)
```

---

## 🔍 Why This Works (3 lines max)
The lock is held by the transaction, so any competing FOR UPDATE/UPDATE/DELETE on those rows queues behind it; after the first commits, the waiter re-reads the fresh value, which kills the lost-update race. SKIP LOCKED turns the table into a concurrent work queue.
हिंदी: Lock transaction के अंत तक रहता है, इसलिए दूसरा session पुराना balance पढ़कर overwrite नहीं कर सकता।

---

## ⚡ Alternative Solution

```sql
-- Atomic single statement - no explicit lock needed for simple arithmetic:
UPDATE accounts SET balance = balance - 100 WHERE id = 1 AND balance >= 100;   -- check affected rows = 1

-- Optimistic locking (no DB lock held, retry on conflict):
-- ALTER TABLE accounts ADD COLUMN version INT NOT NULL DEFAULT 0;
-- UPDATE accounts SET balance = ?, version = version + 1 WHERE id = ? AND version = ?;  -- 0 rows = retry

-- MySQL vs PgSQL differences:
-- * MySQL: locks depend on index used; under REPEATABLE READ range scans take gap/next-key locks (can block inserts, deadlocks).
-- * PostgreSQL: row locks only (no gap locks); locking writes a mark on the row (may dirty pages); use FOR UPDATE OF tbl in joins.
-- * Both: always lock rows in a consistent order (id ASC) to avoid deadlocks.
-- * MySQL error 1205 = lock wait timeout (innodb_lock_wait_timeout, default 50s); PG uses lock_timeout.
```

---

## ⚠️ Common Mistake

```sql
-- ❌ FOR UPDATE outside a transaction (autocommit): lock is released immediately after the statement
SELECT balance FROM accounts WHERE id = 1 FOR UPDATE;   -- useless in autocommit mode

-- ❌ Unindexed WHERE: MySQL can lock many/all rows or the whole range
SELECT * FROM accounts WHERE owner = 'Asha' FOR UPDATE;  -- no index on owner -> scans + locks widely

-- ❌ Holding the lock while calling an external API -> pile-ups
-- ✅ Index the lookup column, keep the transaction short, lock in a fixed order
```

---

## 🎯 Interview Tip (1 line)
Say: "FOR UPDATE is pessimistic row locking inside a transaction; I keep it short and indexed, lock in a consistent order to avoid deadlocks, use NOWAIT/SKIP LOCKED for queues, and prefer atomic UPDATEs or optimistic version columns when contention is low."

---

## 🔗 Related Questions
→ Q225 (ACID real examples) | Q017 (SELECT FOR UPDATE basics) | Q228 (N+1 problem) | Q245 (Zero-downtime migration)
