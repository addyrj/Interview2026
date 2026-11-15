---

# Q125. SERIALIZABLE — Performance Cost
# Category: Transactions & ACID
# Difficulty: ⭐⭐⭐ Hard
# DB: Both (different implementations)

---

## ❓ Question
SERIALIZABLE gives the strongest guarantee. Show what it costs: (1) in MySQL plain reads start taking shared locks and block writers, (2) it can deadlock on the classic "doctors on call" write-skew pattern that REPEATABLE READ silently lets through, (3) how PostgreSQL's SSI differs (no read locks, but serialization failures to retry).

---

## 💡 Quick Concept (2 lines only)
MySQL SERIALIZABLE turns every plain SELECT into `SELECT ... FOR SHARE`, so readers block writers and conflicts end in lock waits or deadlocks. PostgreSQL uses Serializable Snapshot Isolation: readers never block, but it tracks read dependencies (SIReadLock) and aborts one transaction with a serialization failure that the app must retry.
हिंदी: MySQL SERIALIZABLE में सादा SELECT भी shared lock लेता है इसलिए लिखने वाले रुकते हैं; PostgreSQL lock नहीं लगाता पर conflict पर transaction fail करके retry करवाता है।

---

## ✅ Answer / Solution

```sql
-- MySQL 9.1.0: both experiments run with two real parallel sessions (real output below).
-- PostgreSQL: SIReadLock tracking verified on PGlite 18.6 in a single session;
-- the actual "could not serialize access" error needs two sessions and was NOT reproduced.

-- ============================================
-- SETUP (run this first)
-- ============================================

CREATE TABLE doctors (
  id      INT PRIMARY KEY,
  name    VARCHAR(50),
  on_call TINYINT                      -- PostgreSQL: BOOLEAN
) ENGINE=InnoDB;

INSERT INTO doctors VALUES (1, 'Dr. Mehta', 1), (2, 'Dr. Iyer', 1);

-- Business rule: at least ONE doctor must stay on call.

-- ============================================
-- SOLUTION
-- ============================================

-- Experiment 1: does a reader block a writer?
--   A: SET SESSION TRANSACTION ISOLATION LEVEL <level>;  START TRANSACTION;
--   A: SELECT COUNT(*) FROM doctors WHERE on_call = 1;   -- then holds the txn open ~2 s
--   B: (0.5 s later) UPDATE doctors SET name = 'Dr. Mehta' WHERE id = 1;  -- measure the wait

-- Experiment 2: write skew. Each transaction checks the rule, then removes ITSELF.
--   T1 and T2 (same script, $who = 1 or 2), started together:
SET SESSION TRANSACTION ISOLATION LEVEL SERIALIZABLE;      -- repeat with REPEATABLE READ
START TRANSACTION;
SELECT COUNT(*) FROM doctors WHERE on_call = 1;            -- both see 2 -> "safe to leave"
SELECT SLEEP(1);
UPDATE doctors SET on_call = 0 WHERE id = $who;
COMMIT;

-- ============================================
-- EXPECTED OUTPUT
-- ============================================

-- Experiment 1 (real, MySQL 9.1.0; A holds the transaction ~2 s, B starts at ~0.5 s):
--   REPEATABLE READ : B update waited ~0 s   (readers do not block writers)
--   SERIALIZABLE    : B update waited ~1 s   (blocked until A committed, ~1.5 s expected; rounded)
--
-- Experiment 2 (real):
--   REPEATABLE READ : T1 sees 2, T2 sees 2, both finish. Final: id 1 -> 0, id 2 -> 0
--                     NOBODY on call: invariant broken (write skew).
--   SERIALIZABLE    : T1 sees 2 and finishes, T2 sees 2 then
--                     ERROR 1213 (40001): Deadlock found when trying to get lock; try restarting transaction
--                     Final: id 1 -> 0, id 2 -> 1   invariant kept, but one transaction was rolled back.
--
-- PostgreSQL SSI (verified in one session): after BEGIN ISOLATION LEVEL SERIALIZABLE; SELECT count(*) FROM doctors WHERE on_call;
--   pg_locks shows:  locktype=relation | mode=SIReadLock | rel=doctors
--   With two sessions the loser gets: ERROR: could not serialize access due to read/write dependencies
--   among transactions (SQLSTATE 40001)  -- documented, not run here.
```

---

## 🔍 Why This Works (3 lines max)
In MySQL, shared locks taken by the SELECT make T1 and T2 each hold S locks on the rows and then wait for an X lock the other blocks, so InnoDB's deadlock detector kills one. REPEATABLE READ has no read locks, so both check the same snapshot and both succeed, which is why serializable is "safe" but costs waits, deadlocks and retries.
हिंदी: दोनों transactions ने S lock लिया और फिर X lock चाहा, इसलिए deadlock में एक मरती है; REPEATABLE READ में lock नहीं, इसलिए दोनों सफल और rule टूट जाता है।

---

## ⚡ Alternative Solution

```sql
-- Cheaper ways to get the same safety without global SERIALIZABLE:

-- 1) Lock what you read (any level, both DBs; not run): readers of the rule serialize on the rows
START TRANSACTION;
SELECT COUNT(*) FROM doctors WHERE on_call = 1 FOR UPDATE;      -- locks all on-call rows
UPDATE doctors SET on_call = 0 WHERE id = 1;
COMMIT;

-- 2) Guard in a single atomic statement
UPDATE doctors SET on_call = 0
WHERE id = 1 AND (SELECT COUNT(*) FROM (SELECT id FROM doctors WHERE on_call = 1) t) > 1;
-- (MySQL needs the derived table; PostgreSQL does not. Not run.)

-- 3) PostgreSQL: SERIALIZABLE + retry loop in the application
BEGIN ISOLATION LEVEL SERIALIZABLE;
-- ... do work ...
COMMIT;      -- on SQLSTATE 40001 or 40P01: ROLLBACK and retry the whole transaction
-- Tuning: keep serializable transactions short; READ ONLY DEFERRABLE for long reports:
BEGIN ISOLATION LEVEL SERIALIZABLE READ ONLY DEFERRABLE;

-- 4) Set only where needed, not globally:
SET TRANSACTION ISOLATION LEVEL SERIALIZABLE;     -- next transaction only (MySQL)
-- PostgreSQL: ALTER ROLE batch_user SET default_transaction_isolation = 'serializable';
```

---

## ⚠️ Common Mistake
```sql
-- ❌ Turning SERIALIZABLE on globally "for safety": MySQL throughput collapses under lock waits and
--    deadlocks; PostgreSQL's predicate-lock memory grows (max_pred_locks_per_transaction).
-- ❌ Using SERIALIZABLE (PostgreSQL) without a retry loop: 40001 errors become user-visible 500s.
-- ❌ Believing REPEATABLE READ prevents write skew -- it did NOT here (both doctors left).
-- ❌ Leaving a serializable transaction open while calling an external API: in MySQL it keeps
--    shared locks and blocks writers; in PostgreSQL it keeps SSI state alive.
-- ✅ Short transactions, explicit retries on 1213/40001/40P01, targeted FOR UPDATE or constraints
--    for the specific invariant.
```

---

## 🎯 Interview Tip (1 line)
Say: "SERIALIZABLE is correct but expensive: MySQL implements it with read locks so you get blocking and deadlocks, PostgreSQL with SSI so you get non-blocking reads plus serialization failures; either way I use it surgically, keep transactions short, and always wrap it in retry logic - or enforce the invariant with FOR UPDATE or constraints."

---

## 🔗 Related Questions
→ Q121 (Isolation levels) | Q124 (Phantom read) | Q129 (Deadlock example) | Q123 (Non-repeatable read)
