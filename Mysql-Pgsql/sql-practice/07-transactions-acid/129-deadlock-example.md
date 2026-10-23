---

# Q129. Deadlock — Classic Example + Detection + Fix
# Category: Transactions & ACID
# Difficulty: ⭐⭐⭐ Hard
# DB: Both (MySQL + PostgreSQL)

---

## ❓ Question
Show a classic deadlock scenario with SQL. How does the database detect and resolve it? How do you prevent deadlocks in application code? Show three prevention strategies.

---

## 💡 Quick Concept (2 lines only)
Deadlock = Transaction A holds lock X and waits for lock Y. Transaction B holds lock Y and waits for lock X. Neither can proceed — circular wait. Database detects this and kills one transaction (the "victim") to break the cycle.
हिंदी: Deadlock = A, X hold करके Y का wait करे। B, Y hold करके X का wait करे। Circular wait = database एक transaction kill करके cycle break करता है।

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
-- CLASSIC DEADLOCK SCENARIO
-- (Two sessions running simultaneously)
-- ============================================

/*
Timeline of events:

TIME | TRANSACTION A (Alice → Bob)       | TRANSACTION B (Bob → Alice)
─────┼────────────────────────────────────┼────────────────────────────────
t=1  | BEGIN;                             |
t=2  |                                    | BEGIN;
t=3  | SELECT * FROM accounts             |
     | WHERE id = 1 FOR UPDATE;           |
     | ← Acquires ROW LOCK on id=1 ✅    |
t=4  |                                    | SELECT * FROM accounts
     |                                    | WHERE id = 2 FOR UPDATE;
     |                                    | ← Acquires ROW LOCK on id=2 ✅
t=5  | UPDATE accounts                    |
     | SET balance = balance - 200        |
     | WHERE id = 2;                      |
     | ← WAITING for lock on id=2 ⏳     |
     | (held by Transaction B)            |
t=6  |                                    | UPDATE accounts
     |                                    | SET balance = balance - 100
     |                                    | WHERE id = 1;
     |                                    | ← WAITING for lock on id=1 ⏳
     |                                    | (held by Transaction A)
t=7  | ← DEADLOCK DETECTED!              | ← DEADLOCK DETECTED!
     | DB picks "victim" (usually         |
     | transaction with less undo)        |
     | → Transaction A gets ERROR:        |
     |   "Deadlock found, try again"      |
     | → Transaction A ROLLED BACK       |
t=8  |                                    | Lock on id=1 released
     |                                    | UPDATE succeeds ✅
     |                                    | COMMIT ✅

CIRCULAR WAIT (the deadlock):
  TxA has lock(id=1) → waits for lock(id=2)
  TxB has lock(id=2) → waits for lock(id=1)
  → Neither can proceed!

MySQL error:
  ERROR 1213 (40001): Deadlock found when trying to get lock;
  try restarting transaction

PgSQL error:
  ERROR: deadlock detected
  DETAIL: Process 12345 waits for ShareLock on transaction 67890
*/

-- ============================================
-- SOLUTION 1: ALWAYS LOCK IN SAME ORDER
-- (Most effective prevention!)
-- ============================================

-- Both transactions always lock in ascending id order:
-- Transaction A (Transfer 1→2):
BEGIN;
  SELECT * FROM accounts
  WHERE id IN (1, 2)
  ORDER BY id ASC           -- ← always lock id=1 first, then id=2
  FOR UPDATE;
  UPDATE accounts SET balance = balance - 200 WHERE id = 1;
  UPDATE accounts SET balance = balance + 200 WHERE id = 2;
COMMIT;

-- Transaction B (Transfer 2→1):
BEGIN;
  SELECT * FROM accounts
  WHERE id IN (1, 2)
  ORDER BY id ASC           -- ← SAME ORDER: id=1 first, then id=2
  FOR UPDATE;
  UPDATE accounts SET balance = balance - 100 WHERE id = 2;
  UPDATE accounts SET balance = balance + 100 WHERE id = 1;
COMMIT;

-- Both transactions try id=1 first → one waits → no circular dependency!
-- TxA gets id=1 lock → TxB waits for id=1 → TxA gets id=2 → TxA commits
-- → TxB gets id=1 → TxB gets id=2 → TxB commits

-- ============================================
-- SOLUTION 2: RETRY ON DEADLOCK (Application Layer)
-- ============================================

-- Node.js with exponential backoff on deadlock error:
/*
async function transferWithRetry(fromId, toId, amount, maxRetries = 3) {
  for (let attempt = 1; attempt <= maxRetries; attempt++) {
    try {
      await db.transaction(async (trx) => {
        // Lock in consistent order:
        const [first, second] = [fromId, toId].sort((a, b) => a - b);
        await trx('accounts')
          .whereIn('id', [first, second])
          .orderBy('id', 'asc')
          .forUpdate();

        await trx('accounts')
          .where('id', fromId)
          .decrement('balance', amount);
        await trx('accounts')
          .where('id', toId)
          .increment('balance', amount);
      });
      return; // success
    } catch (err) {
      const isDeadlock = err.code === 'ER_LOCK_DEADLOCK' // MySQL
        || err.code === '40P01'; // PgSQL deadlock code
      if (isDeadlock && attempt < maxRetries) {
        const delay = Math.pow(2, attempt) * 100 + Math.random() * 100; // exp backoff + jitter
        console.log(`Deadlock attempt ${attempt}, retrying in ${delay}ms`);
        await sleep(delay);
        continue;
      }
      throw err;
    }
  }
}
*/

-- ============================================
-- SOLUTION 3: REDUCE LOCK SCOPE + DURATION
-- ============================================

-- ❌ Long transaction → high deadlock probability:
BEGIN;
  -- Process some other business logic (100ms)...
  SELECT * FROM accounts WHERE id = 1 FOR UPDATE;  -- holds lock for 100ms!
  -- ... more operations (200ms)...
  UPDATE accounts SET balance = balance - 100 WHERE id = 1;
COMMIT;

-- ✅ Lock late, release early:
BEGIN;
  -- Do all READ operations first (no locks):
  SELECT balance FROM accounts WHERE id = 1;
  -- Validate business logic...
  -- Calculate amount...

  -- Lock only when ready to write:
  SELECT * FROM accounts WHERE id = 1 FOR UPDATE;   -- ← lock grabbed JUST before update
  UPDATE accounts SET balance = balance - 100 WHERE id = 1;
COMMIT;
-- Lock held for milliseconds instead of seconds!

-- ============================================
-- SOLUTION 4: SELECT FOR UPDATE SKIP LOCKED
-- ============================================

-- Avoid waiting for locked rows entirely:
BEGIN;
  SELECT id FROM tasks
  WHERE status = 'pending'
  LIMIT 1
  FOR UPDATE SKIP LOCKED;  -- if row is locked, skip it, get next available!
  -- ← No deadlock possible — never waits for a locked row!
COMMIT;

-- ============================================
-- DETECTING DEADLOCKS IN MYSQL
-- ============================================

-- Show last deadlock details:
SHOW ENGINE INNODB STATUS\G
-- Look for "LATEST DETECTED DEADLOCK" section
-- Shows: which transactions, which locks, which was rolled back

-- Enable deadlock logging:
-- innodb_print_all_deadlocks = ON  (MySQL 5.6+)
-- Logs all deadlocks to error log

-- ============================================
-- DETECTING DEADLOCKS IN PGSQL
-- ============================================

-- PgSQL logs deadlocks automatically:
-- log_lock_waits = on   → log when waiting for lock > deadlock_timeout
-- deadlock_timeout = 1s → time before deadlock detection kicks in

-- See current lock waits:
SELECT
  blocked.pid AS blocked_pid,
  blocking.pid AS blocking_pid,
  blocked_activity.query AS blocked_query,
  blocking_activity.query AS blocking_query
FROM pg_stat_activity blocked_activity
JOIN pg_locks blocked ON blocked.pid = blocked_activity.pid AND NOT blocked.granted
JOIN pg_locks blocking ON blocking.transactionid = blocked.transactionid AND blocking.granted
JOIN pg_stat_activity blocking_activity ON blocking_activity.pid = blocking.pid;
```

---

## 🔍 Why This Works (3 lines max)
Deadlocks happen when multiple transactions acquire locks in different orders — creating a circular wait. The database uses a wait-for graph to detect cycles and kills one transaction. The fundamental prevention is ensuring all code acquires locks in the same global order — no circular dependency can form.
हिंदी: Deadlock circular lock wait से होता है। DB wait-for graph से detect करता है। Prevention = हमेशा same order में locks acquire करो।

---

## ⚡ Alternative Solution

```sql
-- Optimistic locking (avoid locks entirely for most cases):
-- Use a version column instead of FOR UPDATE:

ALTER TABLE accounts ADD COLUMN version INT DEFAULT 0;

BEGIN;
  SELECT id, balance, version FROM accounts WHERE id = 1;  -- Read version=5
  -- Compute new balance...
  UPDATE accounts
  SET balance = balance - 100, version = version + 1
  WHERE id = 1 AND version = 5;  -- ← only update if version hasn't changed!
  -- If 0 rows affected → someone else modified it → ROLLBACK + retry
COMMIT;

-- No FOR UPDATE → no lock held → no deadlock possible!
-- Tradeoff: retry on conflict (good when conflicts are rare)
-- Pessimistic locking (FOR UPDATE) better when conflicts are frequent
```

---

## ⚠️ Common Mistake

```sql
-- ❌ Wrong: Locking rows in different orders across transactions
-- Transaction A: Lock id=1 then id=2
-- Transaction B: Lock id=2 then id=1
-- → Classic deadlock setup!

-- ✅ Fix: Sort ids before locking
-- Always lock: MIN(id) first → MAX(id) second

-- ❌ Wrong: Long transactions with locks
BEGIN;
  SELECT * FROM accounts WHERE id = 1 FOR UPDATE;
  CALL external_api_that_takes_5_seconds();  -- holds lock for 5 seconds!
  UPDATE accounts...;
COMMIT;
-- Any other transaction needing id=1 waits 5 seconds → deadlock probability spikes!

-- ✅ Fix: Get lock → update immediately → commit → THEN call external services

-- ❌ Wrong: Not retrying on deadlock in application
try {
  await transfer(fromId, toId, amount);
} catch (err) {
  throw err;  // ← Application crashes on legitimate deadlock error!
}
-- ✅ Fix: Catch deadlock error codes (ER_LOCK_DEADLOCK / 40P01) and retry
```

---

## 🎯 Interview Tip (1 line)
Say: "I prevent deadlocks by always locking rows in ascending primary key order — this eliminates circular dependency. In application code I catch the deadlock error (MySQL: 1213, PgSQL: 40P01) and retry with exponential backoff. For read-heavy cases, I use optimistic locking with a version column to avoid locks entirely."

---

## 🔗 Related Questions
→ Q127 (optimistic vs pessimistic) | Q128 (SELECT FOR UPDATE) | Q136 (SKIP LOCKED) | Q134 (MVCC)
