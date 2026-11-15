---

# Q135. Long-Running Transaction Problems
# Category: Transactions & ACID
# Difficulty: ⭐⭐⭐ Hard
# DB: Both (MySQL 8.0+ | PostgreSQL) — MySQL part run on 9.1.0 with two sessions; PgSQL monitoring queries run on PGlite (single connection, so no real idle sessions)

---

## ❓ Question
A transaction has been open for 30 minutes (e.g. an app opened BEGIN and then called a slow external API). What problems does it cause, how do you find it, and how do you prevent it?

---

## 💡 Quick Concept (2 lines only)
An open transaction holds its row locks, pins old row versions (undo/dead tuples can't be cleaned), and holds a connection. One forgotten transaction can stall writers, bloat storage and exhaust the pool.
हिंदी: लंबा transaction locks पकड़े रखता है, पुराने row versions साफ़ नहीं होने देता और connection घेरता है; एक भूला हुआ transaction पूरा system धीमा कर सकता है।

---

## ✅ Answer / Solution

```sql
-- ============================================
-- SETUP (run this first)
-- ============================================

CREATE TABLE orders (
  id     INT PRIMARY KEY,
  status VARCHAR(20),          -- PgSQL: TEXT also fine
  total  DECIMAL(10,2)         -- PgSQL: NUMERIC(10,2)
);

INSERT INTO orders VALUES
  (1, 'pending', 99.00),
  (2, 'pending', 49.00);

-- ============================================
-- REPRODUCE (MySQL, two sessions)
-- ============================================

-- Session A (the "forgotten" transaction):
BEGIN;
UPDATE orders SET status = 'processing' WHERE id = 1;
-- ... app now calls a slow payment API, never commits for minutes ...

-- Session B:
SET SESSION innodb_lock_wait_timeout = 2;                -- default is 50 seconds!
UPDATE orders SET status = 'shipped' WHERE id = 1;       -- blocks, then fails
-- ERROR 1205 (HY000): Lock wait timeout exceeded; try restarting transaction

UPDATE orders SET status = 'shipped' WHERE id = 2;       -- other row: fine, no problem

-- ============================================
-- FIND THE CULPRIT (MySQL)
-- ============================================

SELECT trx_id, trx_state, trx_started, trx_rows_locked, trx_query
FROM information_schema.innodb_trx
ORDER BY trx_started;                                    -- oldest first

-- ============================================
-- EXPECTED OUTPUT (real MySQL 9.1.0, run while session A was sleeping)
-- ============================================

-- trx_id | trx_state | trx_rows_locked | trx_query
-- -------+-----------+-----------------+------------
-- 1338   | RUNNING   | 1               | DO SLEEP(6)    <- trx_id/started differ per run
-- Session B on id=1 : ERROR 1205 Lock wait timeout exceeded
-- Session B on id=2 : succeeds -> orders = (1,pending,99.00) (2,shipped,49.00)

-- ============================================
-- FIND THE CULPRIT (PostgreSQL)
-- ============================================

SELECT pid, usename, state,
       now() - xact_start  AS xact_age,
       now() - state_change AS idle_for,
       left(query, 60)     AS last_query
FROM pg_stat_activity
WHERE xact_start IS NOT NULL
ORDER BY xact_start;
-- state = 'idle in transaction' with a big xact_age is the classic offender.
-- (PGlite has one connection, so it only returned its own row: pid=42, state=active.)

-- Kill it:
-- PgSQL : SELECT pg_terminate_backend(<pid>);       MySQL: KILL <processlist_id>;
-- Note: innodb_trx.trx_mysql_thread_id is the id to pass to KILL.
```

---

## 🔍 Why This Works (3 lines max)
Locks are only released at COMMIT/ROLLBACK, so anything the transaction touched stays blocked, and MVCC cannot purge versions older than its snapshot. Monitoring views expose transaction start time so you can find and kill the oldest one.
हिंदी: Locks सिर्फ COMMIT/ROLLBACK पर छूटते हैं और MVCC पुराने versions तब तक नहीं हटा सकता; monitoring views से सबसे पुराना transaction ढूँढकर kill करो।

---

## ⚡ Alternative Solution

```sql
-- PREVENTION (configs - not executed here except the pg_settings read, which showed defaults of 0 = off)

-- PostgreSQL: kill sessions that sit idle inside a transaction
ALTER DATABASE appdb SET idle_in_transaction_session_timeout = '30s';
ALTER DATABASE appdb SET lock_timeout = '5s';
ALTER DATABASE appdb SET statement_timeout = '30s';

-- MySQL:
SET GLOBAL innodb_lock_wait_timeout = 10;     -- fail fast instead of 50s pile-ups
SET GLOBAL wait_timeout = 600;                -- close idle connections (not txn-aware)
SET GLOBAL max_execution_time = 30000;        -- ms, applies to SELECT only

-- Detect blocking chains
-- MySQL : SELECT * FROM sys.innodb_lock_waits\G
-- PgSQL : SELECT pid, pg_blocking_pids(pid) AS blocked_by, query FROM pg_stat_activity
--         WHERE cardinality(pg_blocking_pids(pid)) > 0;

-- Design fix: do slow work (HTTP calls, file uploads) OUTSIDE the transaction.
--   1. SELECT/validate  2. call external API  3. short BEGIN; UPDATE...; COMMIT;
```

---

## ⚠️ Common Mistake

```sql
-- ❌ Wrong: opening a transaction around an external call
BEGIN;
UPDATE orders SET status = 'processing' WHERE id = 1;
-- await paymentGateway.charge(...)     <- 20 seconds, row locked the whole time
COMMIT;

-- ❌ Wrong: a "SELECT-only" transaction left open
-- In PgSQL it still pins the xmin horizon -> VACUUM cannot remove dead tuples
-- for ANY table; in MySQL it grows the undo "History list length".

-- ✅ Correct: short transactions, timeouts set, idle-in-transaction monitored,
--    and use optimistic checks (version column) rather than holding locks across user think-time.
```

---

## 🎯 Interview Tip (1 line)
Say: "I'd alert on oldest transaction age, set idle_in_transaction_session_timeout and lock_timeout, and move slow I/O outside the transaction; long transactions hurt three ways: blocked writers, bloat/undo growth, and connection pool exhaustion."

---

## 🔗 Related Questions
→ Q134 (MVCC) | Q129 (Deadlock example) | Q127 (Optimistic vs pessimistic locking) | Q139 (WAL)
