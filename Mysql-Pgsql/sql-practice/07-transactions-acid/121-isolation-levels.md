---

# Q121. Transaction Isolation Levels — All 4 with Real Examples
# Category: Transactions & ACID
# Difficulty: ⭐⭐⭐ Hard
# DB: Both (MySQL + PostgreSQL)

---

## ❓ Question
Explain all 4 isolation levels with concrete examples of dirty reads, non-repeatable reads, and phantom reads. What are the defaults for MySQL and PostgreSQL? When do you change isolation levels in production?

---

## 💡 Quick Concept (2 lines only)
4 levels from weakest to strongest: READ UNCOMMITTED → READ COMMITTED → REPEATABLE READ → SERIALIZABLE. Each level prevents more anomalies. MySQL default = REPEATABLE READ. PostgreSQL default = READ COMMITTED.
हिंदी: 4 levels (weakest → strongest): READ UNCOMMITTED → READ COMMITTED → REPEATABLE READ → SERIALIZABLE। MySQL default = REPEATABLE READ, PgSQL default = READ COMMITTED।

---

## ✅ Answer / Solution

```sql
-- ============================================
-- SETUP
-- ============================================

CREATE TABLE accounts (
  id      INT PRIMARY KEY,
  name    VARCHAR(50),
  balance DECIMAL(10,2)
);

INSERT INTO accounts VALUES (1, 'Alice', 1000.00), (2, 'Bob', 500.00);

-- ============================================
-- THE 3 READ ANOMALIES (What isolation levels prevent)
-- ============================================

/*
1. DIRTY READ
   → Reading uncommitted data from another transaction
   → "Dirty" because the other transaction might ROLLBACK!

   Timeline:
   T1: UPDATE accounts SET balance = 9999 WHERE id = 1;  -- not committed yet
   T2: SELECT balance FROM accounts WHERE id = 1;        -- reads 9999! (dirty)
   T1: ROLLBACK;  -- 9999 was never real!
   T2 acted on data that never existed.

2. NON-REPEATABLE READ
   → Same query in same transaction returns different values (committed change by another tx)

   Timeline:
   T1: SELECT balance FROM accounts WHERE id = 1;  -- reads 1000
       ... (doing some logic) ...
   T2: UPDATE accounts SET balance = 500 WHERE id = 1; COMMIT;
   T1: SELECT balance FROM accounts WHERE id = 1;  -- reads 500! (changed)
   T1 sees different result for same query within same transaction.

3. PHANTOM READ
   → Same range query returns different ROWS (not different values — new rows appeared)

   Timeline:
   T1: SELECT COUNT(*) FROM accounts;  -- returns 2
       ... (doing some logic) ...
   T2: INSERT INTO accounts VALUES (3, 'Charlie', 200); COMMIT;
   T1: SELECT COUNT(*) FROM accounts;  -- returns 3! (new row appeared = "phantom")
   T1 sees a row that wasn't there at transaction start.
*/

-- ============================================
-- LEVEL 1: READ UNCOMMITTED (weakest)
-- ============================================

-- MySQL:
SET SESSION TRANSACTION ISOLATION LEVEL READ UNCOMMITTED;
-- PgSQL: PostgreSQL doesn't actually allow dirty reads even in READ UNCOMMITTED
-- (it falls back to READ COMMITTED behavior — PgSQL doc explicitly says this)

/*
Prevents: nothing
Allows:   ✅ Dirty reads, non-repeatable reads, phantom reads

Use case:
  - Analytics approximations where absolute accuracy isn't critical
  - "What's the rough total revenue right now?" — close enough
  - Almost NEVER used in production

Example of dirty read:
  Session A: BEGIN; UPDATE accounts SET balance = 5000 WHERE id = 1;
  Session B: (READ UNCOMMITTED) SELECT balance FROM accounts WHERE id = 1;
  -- Session B sees 5000! (uncommitted)
  Session A: ROLLBACK;  -- 5000 never existed
*/

-- ============================================
-- LEVEL 2: READ COMMITTED
-- ============================================

-- MySQL:
SET SESSION TRANSACTION ISOLATION LEVEL READ COMMITTED;
-- PgSQL default! No need to set.

/*
Prevents: ✅ Dirty reads (only reads committed data)
Allows:   Non-repeatable reads, phantom reads

Each statement sees a fresh snapshot of committed data.
Query in same transaction can return different values if another tx commits between queries.

Example of non-repeatable read:
  Session A: BEGIN;
    SELECT balance FROM accounts WHERE id = 1;  -- returns 1000
  Session B: UPDATE accounts SET balance = 800 WHERE id = 1; COMMIT;
  Session A:
    SELECT balance FROM accounts WHERE id = 1;  -- returns 800 now!
    -- Same transaction, same query, different result!
  Session A: COMMIT;

Use case:
  - Default for most OLTP applications (PgSQL default)
  - Acceptable when transactions are short (a few statements)
  - Reporting queries that are OK with seeing live committed data
*/

-- ============================================
-- LEVEL 3: REPEATABLE READ
-- ============================================

-- MySQL default!
SET SESSION TRANSACTION ISOLATION LEVEL REPEATABLE READ;
-- PgSQL:
SET TRANSACTION ISOLATION LEVEL REPEATABLE READ;

/*
Prevents: ✅ Dirty reads, ✅ non-repeatable reads
Allows:   Phantom reads (theoretically — MySQL InnoDB actually prevents these too!)

Once a transaction starts, it sees a CONSISTENT SNAPSHOT of the database.
All reads within the transaction see the data as it was at transaction start.

Example showing non-repeatable read IS PREVENTED:
  Session A: BEGIN;
    SELECT balance FROM accounts WHERE id = 1;  -- returns 1000
  Session B: UPDATE accounts SET balance = 800 WHERE id = 1; COMMIT;
  Session A:
    SELECT balance FROM accounts WHERE id = 1;  -- STILL returns 1000! (snapshot!)
  Session A: COMMIT;
  -- After Session A commits, future reads would see 800.

MySQL InnoDB REPEATABLE READ quirk:
  - Prevents phantom reads for CONSISTENT (non-locking) reads via MVCC snapshot
  - BUT: SELECT FOR UPDATE and locking reads CAN still see new rows (phantoms!)

PgSQL REPEATABLE READ:
  - Full snapshot isolation — phantoms prevented for all reads
  - Transaction gets snapshot at first statement
  - Serialization failure possible: "ERROR: could not serialize access"
  → Application must retry transaction on serialization failure

Use case:
  - Financial calculations where consistency across multiple reads matters
  - Report generation (all rows from same "point in time")
  - MySQL default for exactly this reason
*/

-- ============================================
-- LEVEL 4: SERIALIZABLE (strongest)
-- ============================================

SET SESSION TRANSACTION ISOLATION LEVEL SERIALIZABLE;

/*
Prevents: ✅ Dirty reads, ✅ non-repeatable reads, ✅ phantom reads
Guarantees: transactions execute as if they ran serially (one after another)

Most restrictive → lowest concurrency. Uses predicate locks (PgSQL) or
gap locks (MySQL InnoDB) to prevent even phantom reads.

PgSQL: Serializable Snapshot Isolation (SSI) — detects conflicts optimistically
  → may abort transactions with: ERROR 40001 (serialization failure)
  → Application MUST retry on 40001!

MySQL InnoDB: uses gap locks and next-key locks
  → More deadlocks possible
  → Less starvation (different mechanism than PgSQL's SSI)

Example preventing phantom read:
  Session A: (SERIALIZABLE)
    SELECT COUNT(*) FROM accounts;  -- returns 2
  Session B: INSERT INTO accounts VALUES (3, 'Charlie', 200); COMMIT;
  Session A:
    SELECT COUNT(*) FROM accounts;  -- STILL returns 2! (no phantom)
  Session A: COMMIT;

Use case:
  - Critical financial operations (double-spend prevention)
  - Inventory systems (prevent overselling)
  - Audit trail systems
  - Any "check-then-act" pattern requiring serializability
*/

-- ============================================
-- COMPARISON TABLE
-- ============================================

/*
Level             | Dirty | Non-rep | Phantom | MySQL  | PgSQL
──────────────────┼───────┼─────────┼─────────┼────────┼──────────
READ UNCOMMITTED  |  ✅   |   ✅    |   ✅    | Allows | Falls back to RC
READ COMMITTED    |  ❌   |   ✅    |   ✅    |        | DEFAULT
REPEATABLE READ   |  ❌   |   ❌    |  ❌*   | DEFAULT|
SERIALIZABLE      |  ❌   |   ❌    |   ❌    |        |

* MySQL InnoDB prevents phantoms for non-locking reads via MVCC.
  PgSQL: fully prevents phantoms in REPEATABLE READ.

✅ = anomaly CAN occur | ❌ = anomaly prevented
*/

-- ============================================
-- SETTING ISOLATION LEVEL — SCOPE
-- ============================================

-- MySQL: Per session (affects all transactions in this connection):
SET SESSION TRANSACTION ISOLATION LEVEL REPEATABLE READ;
-- or per next transaction only:
SET TRANSACTION ISOLATION LEVEL READ COMMITTED;  -- next transaction only

-- PgSQL: Per transaction:
BEGIN;
SET TRANSACTION ISOLATION LEVEL REPEATABLE READ;
-- ... queries ...
COMMIT;

-- PgSQL: Per session:
SET SESSION CHARACTERISTICS AS TRANSACTION ISOLATION LEVEL SERIALIZABLE;

-- PgSQL: Per database default:
ALTER DATABASE myapp SET default_transaction_isolation TO 'read committed';

-- ============================================
-- WHEN TO CHANGE ISOLATION LEVEL IN PRODUCTION
-- ============================================

/*
READ COMMITTED (weaker than default on MySQL):
  Use when: reporting queries on MySQL that don't need REPEATABLE READ
  Benefit: avoids long-held read snapshots (reduces undo log growth in MySQL)
  Code: SET SESSION TRANSACTION ISOLATION LEVEL READ COMMITTED;
  Scenario: analytics dashboard queries that don't update data

REPEATABLE READ (PgSQL — stronger than default):
  Use when: report generation that reads multiple tables and needs consistency
  Code: BEGIN; SET TRANSACTION ISOLATION LEVEL REPEATABLE READ; ...

SERIALIZABLE:
  Use when: critical financial transactions (bank transfers, inventory updates)
  Must handle: serialization failures (error 40001 / ER_LOCK_DEADLOCK)
  Pattern:
*/

-- Node.js: retry on serialization failure:
/*
async function serializableTransfer(fromId, toId, amount, maxRetries = 3) {
  for (let attempt = 0; attempt < maxRetries; attempt++) {
    try {
      await db.transaction(async (trx) => {
        await trx.raw('SET TRANSACTION ISOLATION LEVEL SERIALIZABLE');
        const [from] = await trx('accounts').where('id', fromId).forUpdate();
        if (from.balance < amount) throw new Error('Insufficient funds');
        await trx('accounts').where('id', fromId).decrement('balance', amount);
        await trx('accounts').where('id', toId).increment('balance', amount);
      });
      return;
    } catch (err) {
      const isSerializationFailure =
        err.code === '40001' ||           // PgSQL serialization failure
        err.code === 'ER_LOCK_DEADLOCK';  // MySQL deadlock
      if (isSerializationFailure && attempt < maxRetries - 1) {
        await new Promise(r => setTimeout(r, Math.pow(2, attempt) * 50));
        continue;
      }
      throw err;
    }
  }
}
*/

-- ============================================
-- MVCC: HOW REPEATABLE READ WORKS INTERNALLY
-- ============================================

/*
PostgreSQL MVCC (Multi-Version Concurrency Control):
  - Each row has xmin (created by transaction ID) and xmax (deleted by transaction ID)
  - At transaction start: record the current transaction ID as the "snapshot horizon"
  - Only read rows where: xmin <= snapshot_id AND (xmax = 0 OR xmax > snapshot_id)
  - Reads see rows "before" transaction started — concurrent writes don't affect you
  - Write conflicts: detected by checking if your target row was modified after your snapshot
  - On conflict in SERIALIZABLE: abort with error 40001 → application retries

MySQL InnoDB MVCC:
  - Uses undo log: stores old versions of rows
  - Read view created at transaction start (REPEATABLE READ) or each statement (READ COMMITTED)
  - Consistent read follows row header to undo log to find the version visible to this view
*/
```

---

## 🔍 Why This Works (3 lines max)
Each isolation level adds more "guardrails": READ COMMITTED sees only committed data (no dirty reads); REPEATABLE READ creates a snapshot at transaction start so the same query returns the same data; SERIALIZABLE ensures the entire execution is equivalent to some serial order. MVCC enables high concurrency — readers don't block writers and vice versa at all levels except SERIALIZABLE under heavy write conflict.
हिंदी: READ COMMITTED = dirty reads नहीं। REPEATABLE READ = snapshot at start, same query same result। SERIALIZABLE = serial execution guarantee। MVCC = readers writers को block नहीं करते।

---

## ⚡ Alternative Solution

```sql
-- Advisory locks for application-level serializability (PgSQL):
-- When SERIALIZABLE is too aggressive:
BEGIN;
  SELECT pg_advisory_xact_lock(42);   -- lock "resource 42" for this transaction
  -- Only one transaction can hold this lock at a time
  -- Other transactions wait here until lock released (on COMMIT/ROLLBACK)
  SELECT balance FROM accounts WHERE id = 1;
  UPDATE accounts SET balance = balance - 100 WHERE id = 1;
COMMIT;
-- pg_advisory_xact_lock: released automatically at transaction end
-- More granular than SERIALIZABLE (lock specific resources, not whole table)
```

---

## ⚠️ Common Mistake

```sql
-- ❌ Wrong: Using SERIALIZABLE without retry logic
BEGIN;
  SET TRANSACTION ISOLATION LEVEL SERIALIZABLE;
  SELECT balance FROM accounts WHERE id = 1;
  UPDATE accounts SET balance = balance - 100 WHERE id = 1;
COMMIT;
-- PgSQL may throw: ERROR: could not serialize access due to concurrent update
-- Without retry: user sees an error, money not transferred!
-- ✅ Always wrap SERIALIZABLE transactions in a retry loop

-- ❌ Wrong: Thinking MySQL REPEATABLE READ prevents ALL phantoms
BEGIN;
  SELECT * FROM accounts WHERE balance > 500;  -- 2 rows
-- Another session inserts account with balance = 600
  SELECT * FROM accounts WHERE balance > 500 FOR UPDATE;  -- NOW sees 3 rows (phantom!)
-- FOR UPDATE takes a current read snapshot, not the transaction's MVCC snapshot!
-- ✅ Use SERIALIZABLE to guarantee no phantoms with locking reads in MySQL

-- ❌ Wrong: Long-running transactions in READ COMMITTED (MySQL):
-- MySQL READ COMMITTED: generates an undo log entry for every statement
-- 10-minute transaction with thousands of statements = huge undo log growth!
-- ✅ Keep transactions short regardless of isolation level
```

---

## 🎯 Interview Tip (1 line)
Say: "MySQL defaults to REPEATABLE READ — each transaction gets a MVCC snapshot at start, preventing dirty and non-repeatable reads. PgSQL defaults to READ COMMITTED — stricter than MySQL's default would suggest for PgSQL. I use SERIALIZABLE for critical financial operations (bank transfers, inventory) with a retry loop to handle serialization failures (error 40001 in PgSQL)."

---

## 🔗 Related Questions
→ Q129 (deadlock) | Q127 (optimistic vs pessimistic locking) | Q134 (MVCC internals) | Q125 (ACID overview)
