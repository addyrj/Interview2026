---

# Q225. ACID Properties — Real Example for Each
# Category: Interview Classics
# Difficulty: ⭐⭐ Medium
# DB: Both (MySQL + PostgreSQL)

---

## ❓ Question
Explain the four ACID properties with a concrete real-world banking/e-commerce example for each. What happens when each property is violated? Show the SQL to demonstrate.

---

## 💡 Quick Concept (2 lines only)
ACID = Atomicity (all or nothing), Consistency (rules always satisfied), Isolation (concurrent txns don't interfere), Durability (committed data survives crash). Without ACID, you get partial transfers, negative balances, lost updates, and data loss on crash.
हिंदी: ACID = Atomicity (सब हो या कुछ नहीं), Consistency (rules always follow हों), Isolation (concurrent transactions interfere न करें), Durability (commit के बाद crash पर भी data safe)।

---

## ✅ Answer / Solution

```sql
-- ============================================
-- SETUP — Bank account table
-- ============================================

CREATE TABLE accounts (
  id         INT PRIMARY KEY AUTO_INCREMENT,
  user_id    INT NOT NULL,
  name       VARCHAR(100) NOT NULL,
  balance    DECIMAL(12,2) NOT NULL DEFAULT 0.00,
  CHECK (balance >= 0)    -- ← enforces Consistency!
);

INSERT INTO accounts (user_id, name, balance) VALUES
  (1, 'Alice', 1000.00),
  (2, 'Bob',    500.00);

-- ============================================
-- A — ATOMICITY: ALL or NOTHING
-- ============================================
-- A transaction either completes fully or has zero effect.
-- No partial state.

-- Violation scenario (without atomicity):
--   Step 1: Debit Alice $200 ✅ (done)
--   App crashes here!
--   Step 2: Credit Bob $200  ❌ (never runs)
--   → Alice lost $200, Bob never received it. Money disappeared! ☠️

-- WITH atomicity (correct):
BEGIN;

  UPDATE accounts
  SET balance = balance - 200.00
  WHERE id = 1 AND balance >= 200.00;   -- debit Alice

  -- If app crashes HERE, transaction hasn't committed
  -- MySQL will ROLLBACK when connection drops (incomplete txn)

  UPDATE accounts
  SET balance = balance + 200.00
  WHERE id = 2;                          -- credit Bob

COMMIT;  -- BOTH changes happen only when COMMIT succeeds
-- If ANY error between BEGIN and COMMIT → ROLLBACK → no partial state

-- Node.js / Sequelize example (atomicity in code):
/*
await sequelize.transaction(async (t) => {
  await Account.decrement('balance', { by: 200, where: { id: 1 }, transaction: t });
  await Account.increment('balance', { by: 200, where: { id: 2 }, transaction: t });
  // If either throws → automatic rollback
});
*/

-- ============================================
-- C — CONSISTENCY: RULES ALWAYS SATISFIED
-- ============================================
-- Database never enters an invalid state.
-- Constraints, triggers, and business rules enforced.

-- Without consistency:
--   Alice has $100, tries to transfer $200
--   → balance becomes -$100 (violated CHECK constraint!)

-- WITH consistency (CHECK constraint prevents this):
BEGIN;
  UPDATE accounts
  SET balance = balance - 500.00
  WHERE id = 2;  -- Bob has $500, deduct $500+1 = -$1 → violates CHECK!

  -- PgSQL: CHECK constraint fires → ERROR: new row violates check constraint
  -- MySQL: also raises error if CHECK is enforced (MySQL 8.0.16+)
ROLLBACK;  -- Rolls back automatically on constraint violation

-- Application-level consistency check:
BEGIN;
  -- First verify sufficient balance:
  SELECT balance FROM accounts WHERE id = 2 FOR UPDATE;  -- lock the row
  -- Application checks: if balance < transfer_amount → ROLLBACK

  -- Then deduct:
  UPDATE accounts
  SET balance = balance - 200.00
  WHERE id = 2 AND balance >= 200.00;  -- double-check in SQL too

  -- Verify rows affected = 1 (not 0):
  -- If 0 rows affected → balance was insufficient → ROLLBACK in app
COMMIT;

-- ============================================
-- I — ISOLATION: CONCURRENT TXNS DON'T INTERFERE
-- ============================================
-- Concurrent transactions behave as if they ran sequentially.
-- Without isolation: dirty reads, non-repeatable reads, phantom reads.

-- ISOLATION LEVEL EXAMPLES:

-- 1. READ UNCOMMITTED (weakest) — DIRTY READ possible:
-- Transaction A: UPDATE accounts SET balance=9999 WHERE id=1;  (not yet committed)
-- Transaction B: SELECT balance FROM accounts WHERE id=1;
--   → Reads 9999! (dirty read — A might ROLLBACK!)
--   → Transaction B got an uncommitted value = unreliable

-- 2. READ COMMITTED (default in PgSQL):
-- Transaction A: BEGIN; UPDATE... (not committed)
-- Transaction B: SELECT → sees OLD value (no dirty read)
-- Transaction A: COMMIT
-- Transaction B: SELECT AGAIN → sees NEW value
--   → Non-repeatable read! Same query, different result within same txn.

-- 3. REPEATABLE READ (default in MySQL InnoDB):
SET TRANSACTION ISOLATION LEVEL REPEATABLE READ;
BEGIN;
  -- Transaction sees a SNAPSHOT of data as of transaction start
  SELECT balance FROM accounts WHERE id = 1;  -- → 1000
  -- Even if another transaction commits UPDATE during this txn:
  SELECT balance FROM accounts WHERE id = 1;  -- → 1000 (same snapshot!)
COMMIT;

-- 4. SERIALIZABLE (strictest):
SET TRANSACTION ISOLATION LEVEL SERIALIZABLE;
-- Transactions run as if serial — no anomalies but lowest concurrency

-- Isolation level in PgSQL:
SET TRANSACTION ISOLATION LEVEL READ COMMITTED;  -- per transaction
-- OR globally: SET default_transaction_isolation = 'read committed';

-- ============================================
-- D — DURABILITY: COMMITTED DATA SURVIVES CRASH
-- ============================================
-- Once COMMIT succeeds, data is permanent — even if server crashes immediately after.

-- How it works (WAL — Write-Ahead Log):
-- 1. Transaction writes to WAL (redo log) on disk FIRST
-- 2. COMMIT flushes WAL to disk (fsync)
-- 3. Only then: COMMIT returns success to application
-- 4. If server crashes: on restart, WAL is replayed → committed data recovered

-- Demonstration (you can't "show" this in SQL but concept):
BEGIN;
  UPDATE accounts SET balance = 2000.00 WHERE id = 1;
COMMIT;
-- ← Server crashes HERE, power cut
-- On restart: WAL shows the committed UPDATE
-- → MySQL InnoDB redo log replays it → Alice's balance = 2000 ✅

-- MySQL durability config (critical!):
-- innodb_flush_log_at_trx_commit = 1 (default, full durability)
--   = 0 → flush every second (risk: 1s data loss on crash)
--   = 2 → write to OS cache on commit (risk: loss on OS crash)
-- sync_binlog = 1 (sync binary log on each commit — replication durability)

-- PgSQL durability:
-- synchronous_commit = on (default, full durability)
--   = off → async commit (performance boost, ~10ms window of data loss risk)
--   = remote_write → for synchronous replication

-- ============================================
-- FULL TRANSFER WITH ALL ACID PROPERTIES
-- ============================================

-- Production-grade money transfer:
DELIMITER //  -- MySQL stored procedure
CREATE PROCEDURE transfer_money(
  IN from_account INT,
  IN to_account   INT,
  IN amount       DECIMAL(12,2)
)
BEGIN
  DECLARE EXIT HANDLER FOR SQLEXCEPTION   -- catch any error
  BEGIN
    ROLLBACK;                              -- A: atomic rollback
    RESIGNAL;                             -- re-throw error
  END;

  START TRANSACTION;

    -- Lock both rows (prevents concurrent transfers from same account):
    SELECT id, balance FROM accounts
    WHERE id IN (from_account, to_account)
    ORDER BY id                           -- always lock in same order → prevent deadlock
    FOR UPDATE;

    -- Check balance (C: consistency check):
    IF (SELECT balance FROM accounts WHERE id = from_account) < amount THEN
      SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Insufficient balance';
    END IF;

    -- Debit (A: part 1):
    UPDATE accounts SET balance = balance - amount WHERE id = from_account;

    -- Credit (A: part 2):
    UPDATE accounts SET balance = balance + amount WHERE id = to_account;

  COMMIT;  -- D: WAL flushed, durable now
END //
DELIMITER ;

CALL transfer_money(1, 2, 200.00);

-- After: Alice = 800.00, Bob = 700.00
-- SELECT * FROM accounts;
-- id | name  | balance
-- ---+-------+--------
--  1 | Alice | 800.00
--  2 | Bob   | 700.00
```

---

## 🔍 Why This Works (3 lines max)
Atomicity uses BEGIN/COMMIT/ROLLBACK to treat multiple operations as one unit. Consistency relies on CHECK constraints and application logic to keep data valid. Isolation and Durability are handled by the database engine — InnoDB uses MVCC for isolation and WAL (redo log) for durability.
हिंदी: BEGIN/COMMIT = Atomicity। CHECK constraints = Consistency। MVCC = Isolation। WAL (redo log) = Durability।

---

## ⚡ Alternative Solution

```sql
-- PostgreSQL — same transfer, cleaner syntax:
BEGIN;
  UPDATE accounts SET balance = balance - 200
  WHERE id = 1 AND balance >= 200
  RETURNING balance;     -- verify deduction happened (PgSQL RETURNING)

  UPDATE accounts SET balance = balance + 200
  WHERE id = 2;
COMMIT;

-- Node.js with Knex (transactional):
await knex.transaction(async (trx) => {
  const [deducted] = await trx('accounts')
    .where({ id: fromId })
    .where('balance', '>=', amount)
    .decrement('balance', amount);

  if (!deducted) throw new Error('Insufficient balance');  // auto rollback

  await trx('accounts').where({ id: toId }).increment('balance', amount);
});
```

---

## ⚠️ Common Mistake

```sql
-- ❌ Wrong: Reading balance then updating (TOCTOU race condition):
-- Session A: SELECT balance = 1000
-- Session B: SELECT balance = 1000
-- Session A: UPDATE SET balance = 1000 - 500 = 500
-- Session B: UPDATE SET balance = 1000 - 800 = 200 (used stale read!)
-- Result: Alice has 200 instead of -300 (data inconsistency!)

-- ✅ Correct: Use SELECT FOR UPDATE or atomic UPDATE with condition:
UPDATE accounts
SET balance = balance - 500
WHERE id = 1 AND balance >= 500;
-- If 0 rows affected → insufficient balance
-- Atomic — no race condition possible

-- ❌ Wrong: innodb_flush_log_at_trx_commit = 0 in production
-- → Up to 1 second of committed data can be lost on crash!
-- ✅ Always: innodb_flush_log_at_trx_commit = 1 for financial systems
```

---

## 🎯 Interview Tip (1 line)
Say: "For money transfers, I always use SELECT FOR UPDATE to lock rows, update atomically within a transaction, use CHECK constraint for non-negative balance (Consistency), and ensure `innodb_flush_log_at_trx_commit=1` for Durability — these together make the operation fully ACID-compliant."

---

## 🔗 Related Questions
→ Q121 (ACID overview) | Q127 (optimistic vs pessimistic) | Q129 (deadlock) | Q136 (SKIP LOCKED)
