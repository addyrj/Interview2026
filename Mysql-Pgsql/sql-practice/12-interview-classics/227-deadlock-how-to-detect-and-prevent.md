---

# Q227. Deadlock — How to Detect and Prevent
# Category: Interview Classics
# Difficulty: ⭐⭐⭐ Hard
# DB: Both (MySQL InnoDB + PostgreSQL)

---

## ❓ Question
What is a deadlock? Reproduce one with two money-transfer transactions that update the same two rows in opposite order, show how the database detects it, and explain how to prevent it and handle it in the application.

---

## 💡 Quick Concept (2 lines only)
A deadlock is a cycle: T1 holds row A and waits for B, T2 holds B and waits for A. The engine detects the cycle, kills one transaction (the victim) with an error, and the other proceeds; prevent it by always locking rows in a consistent order and keeping transactions short.
हिंदी: दो transactions एक-दूसरे का lock मांगते हैं तो cycle बनती है; database एक को मार देता है, इसलिए हमेशा same order में lock लो।

---

## ✅ Answer / Solution

```sql
-- ============================================
-- SETUP (MySQL 9.1 InnoDB; PostgreSQL: use NUMERIC and drop ENGINE)
-- ============================================

CREATE TABLE wallets (
  id      INT PRIMARY KEY,
  owner   VARCHAR(30) NOT NULL,
  balance DECIMAL(10,2) NOT NULL
) ENGINE=InnoDB;

INSERT INTO wallets VALUES (1, 'Alice', 1000), (2, 'Bob', 1000);

-- ============================================
-- SOLUTION 1 — reproduce the deadlock (two sessions; real MySQL 9.1 run, timed with SLEEP)
-- ============================================

-- Session A (Alice -> Bob 100):                      -- Session B (Bob -> Alice 50), started 0.5 s later:
START TRANSACTION;                                     START TRANSACTION;
UPDATE wallets SET balance = balance - 100 WHERE id=1; -- A locks row 1
                                                       UPDATE wallets SET balance = balance - 50 WHERE id=2;  -- B locks row 2
UPDATE wallets SET balance = balance + 100 WHERE id=2; -- A waits for row 2 (held by B)
                                                       UPDATE wallets SET balance = balance + 50 WHERE id=1;  -- B waits for row 1 -> CYCLE
-- Result (observed):
--   Session A: succeeds, COMMIT ok
--   Session B: ERROR 1213 (40001): Deadlock found when trying to get lock; try restarting transaction
-- Final table (only A's transfer survived; B was rolled back):
-- id | owner | balance
-- 1  | Alice | 900.00
-- 2  | Bob   | 1100.00
-- (Which session is the victim is chosen by the engine: InnoDB prefers the transaction that changed fewer rows.)

-- ============================================
-- SOLUTION 2 — detect / diagnose
-- ============================================

-- MySQL: last deadlock with both statements, held and waited locks
SHOW ENGINE INNODB STATUS\G
-- Section "LATEST DETECTED DEADLOCK" (excerpt from the run above):
--   *** (1) TRANSACTION: ... UPDATE wallets SET balance=balance+100 WHERE id=2
--   *** (1) HOLDS THE LOCK(S): RECORD LOCKS ... index PRIMARY of table `t227`.`wallets` lock_mode X locks rec but not gap
--   *** (1) WAITING FOR THIS LOCK TO BE GRANTED: ... (row id=2)
--   *** (2) TRANSACTION: ... UPDATE wallets SET balance=balance+50 WHERE id=1
--   *** (2) HOLDS ... row id=2 ; WAITING FOR ... row id=1
--   *** WE ROLL BACK TRANSACTION (2)
-- Log every deadlock to the error log (not just the latest):
SET GLOBAL innodb_print_all_deadlocks = ON;
-- Related settings seen: innodb_deadlock_detect = 1 (ON), innodb_lock_wait_timeout = 50 seconds
-- (a plain lock WAIT, not a cycle, errors with 1205 after the timeout)

-- PostgreSQL (same two sessions; NOT RUN here - PGlite has a single connection):
--   ERROR:  deadlock detected
--   DETAIL: Process 123 waits for ShareLock on transaction 456; blocked by process 789.
--           Process 789 waits for ShareLock on transaction 123; blocked by process 123.
--   HINT:   See server log for query details.
-- PostgreSQL checks only after deadlock_timeout (default 1s), then aborts one session.
-- Config: log_lock_waits = on;  deadlock_timeout = '1s';
-- Live view: SELECT * FROM pg_locks WHERE NOT granted;  /  pg_blocking_pids(pid)

-- ============================================
-- SOLUTION 3 — prevent: lock rows in a fixed order (same two sessions, verified)
-- ============================================

START TRANSACTION;
SELECT id FROM wallets WHERE id IN (1, 2) ORDER BY id FOR UPDATE;   -- always lowest id first
UPDATE wallets SET balance = balance - 100 WHERE id = 1;
UPDATE wallets SET balance = balance + 100 WHERE id = 2;
COMMIT;
-- Run as both A (100 from Alice) and B (50 from Bob), overlapping in time:
-- Result: both commit, NO error. B simply waited for A. Final: Alice 950.00, Bob 1050.00 (both transfers applied).
-- Works in PostgreSQL identically (SELECT ... ORDER BY id FOR UPDATE).
```

---

## 🔍 Why This Works (3 lines max)
A deadlock needs a circular wait; if every transaction acquires locks in the same global order (e.g. ascending id), a cycle is impossible and the second transaction just waits. Detection is automatic (wait-for graph in InnoDB, timeout-triggered check in PostgreSQL), so the application's job is to retry.
हिंदी: Lock का order सबके लिए same हो तो cycle बन ही नहीं सकती; फिर भी deadlock आए तो transaction retry करो।

---

## ⚡ Alternative Solution

```sql
-- 1) Application retry on error 1213 (MySQL) / SQLSTATE 40P01 (PostgreSQL), 40001 serialization failures:
--    retry the WHOLE transaction 2-3 times with small random backoff.

-- 2) Single-statement atomic update, no read-then-write:
UPDATE wallets SET balance = balance - 100 WHERE id = 1 AND balance >= 100;   -- check rows affected

-- 3) Skip contended rows (queues/workers): MySQL 8.0+ and PostgreSQL 9.5+
SELECT * FROM wallets WHERE id = 1 FOR UPDATE SKIP LOCKED;
-- (verified in MySQL: returns the row when unlocked; returns empty set if another txn holds it)
SELECT * FROM wallets WHERE id = 1 FOR UPDATE NOWAIT;    -- fail immediately instead of waiting

-- 4) Other causes to hunt: missing index on the WHERE column (InnoDB locks every scanned row/gap),
--    gap locks under REPEATABLE READ (READ COMMITTED reduces them), foreign-key checks, big batch updates.
-- 5) Keep transactions short; do no network calls or user waits inside a transaction.
```

---

## ⚠️ Common Mistake

```sql
-- ❌ Wrong: "turn off deadlock detection / increase timeout to fix it" -> hangs instead of failing fast
-- ❌ Wrong: no retry logic: user sees a 500 for an error the database considers normal and retryable
-- ❌ Wrong: updating rows in whatever order the code path happens to use (transfer A->B vs B->A)
-- ❌ Wrong: UPDATE ... WHERE non_indexed_col = ... -> locks many more rows, more collisions
-- ✅ Correct: consistent lock order, indexed predicates, short transactions, retry on 1213 / 40P01
```

---

## 🎯 Interview Tip (1 line)
Say: "Deadlocks are normal under concurrency, not a bug to eliminate entirely — I detect them with SHOW ENGINE INNODB STATUS / log_lock_waits, prevent most with consistent lock ordering, indexed predicates and short transactions, and always make the application retry the whole transaction on error 1213 or 40P01."

---

## 🔗 Related Questions
→ Q226 (MVCC) | Q017 (SELECT FOR UPDATE) | Q225 (ACID real examples) | Q234 (connection pooling)
