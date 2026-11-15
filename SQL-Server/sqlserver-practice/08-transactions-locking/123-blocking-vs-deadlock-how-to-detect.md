---

# Q123. Blocking vs Deadlock — How to Detect
# Category: Transactions + Locking
# Difficulty: ⭐⭐⭐ Hard
# DB: SQL Server (PostgreSQL: pg_stat_activity + pg_locks; MySQL: performance_schema.data_lock_waits)

---

## ❓ Question
The API is timing out. How do you tell blocking from a deadlock, find the head blocker, and see what it is running?

---

## 💡 Quick Concept (2 lines only)
Blocking is one session waiting for another; it resolves when the blocker commits, or it keeps going if the blocker never finishes. A deadlock is a cycle where each waits for the other, so SQL Server kills one victim (error 1205) automatically.
हिंदी: Blocking = एक session दूसरे का इंतज़ार कर रहा है, blocker खत्म हो तो छूट जाता है। Deadlock = दोनों एक-दूसरे का इंतज़ार, SQL Server एक को खुद मार देता है।

---

## ✅ Answer / Solution

NOTE: not executed on SQL Server (needs concurrent sessions); DMV and column names are documented ones, no sample rows are shown.

```sql
-- ============================================
-- SETUP (to reproduce blocking manually)
-- ============================================

CREATE TABLE dbo.Orders (
    OrderId INT PRIMARY KEY,
    Status  VARCHAR(20) NOT NULL
);
INSERT INTO dbo.Orders (OrderId, Status) VALUES (1, 'Pending'), (2, 'Pending');
GO

-- Session 1 (leave open):
--   BEGIN TRAN; UPDATE dbo.Orders SET Status = 'Shipped' WHERE OrderId = 1;
-- Session 2 (hangs = blocked):
--   SELECT Status FROM dbo.Orders WHERE OrderId = 1;     -- (under default READ COMMITTED)

-- ============================================
-- STEP 1: who is blocked and by whom
-- ============================================

SELECT
    r.session_id,
    r.blocking_session_id,
    r.wait_type,
    r.wait_time,                 -- milliseconds
    r.status,
    DB_NAME(r.database_id)       AS database_name,
    t.text                       AS running_sql
FROM sys.dm_exec_requests AS r
OUTER APPLY sys.dm_exec_sql_text(r.sql_handle) AS t
WHERE r.blocking_session_id <> 0;

-- ============================================
-- STEP 2: find the head blocker (blocks others but is not blocked itself)
-- ============================================

SELECT DISTINCT r.blocking_session_id AS head_blocker
FROM sys.dm_exec_requests AS r
WHERE r.blocking_session_id <> 0
  AND r.blocking_session_id NOT IN (SELECT session_id FROM sys.dm_exec_requests WHERE blocking_session_id <> 0);

-- What is the head blocker doing? (it may be sleeping with an open transaction)
SELECT s.session_id, s.status, s.login_name, s.host_name, s.program_name, s.open_transaction_count
FROM sys.dm_exec_sessions AS s
WHERE s.session_id = 55;          -- replace with the id found above

-- Quick legacy view: EXEC sp_who2;   (BlkBy column)

-- ============================================
-- STEP 3: deadlocks are different - they resolve themselves
-- ============================================
-- * Victim gets error 1205 and its transaction is rolled back
-- * Evidence: system_health xml_deadlock_report (see Q116)
-- Blocking symptom : many sessions with the same blocking_session_id, wait_type LCK_M_* (e.g. LCK_M_S, LCK_M_X)
-- Deadlock symptom : sporadic 1205 errors in the application log, no long-lasting wait

-- ============================================
-- Resolve (last resort): KILL the head blocker - rolls back its work
-- ============================================
-- KILL 55;
```

---

## 🔍 Why This Works (3 lines max)
`blocking_session_id` in sys.dm_exec_requests gives the wait chain; following it to a session that is not itself blocked finds the root. A sleeping session with an open transaction (open_transaction_count > 0) is the typical culprit: the app forgot to commit. Deadlocks leave a trace in Extended Events instead of a persistent wait.
हिंदी: blocking_session_id से chain मिलती है, जो खुद blocked नहीं है वह head blocker है। अक्सर कोई session transaction खुली छोड़कर बैठा होता है।

---

## ⚡ Alternative Solution

```sql
-- Add a client-side timeout so the app fails fast instead of hanging forever
SET LOCK_TIMEOUT 5000;       -- wait max 5 seconds for a lock, then an error is raised for the statement

-- Node.js (mssql): requestTimeout in pool config also protects the API:
-- const pool = await sql.connect({ ..., requestTimeout: 15000 });
```

---

## ⚠️ Common Mistake

```sql
-- ❌ Wrong: KILL-ing the first blocked session you see instead of the head blocker
-- ❌ Wrong: treating all slowness as deadlock; deadlocks produce 1205, blocking produces timeouts.
-- ❌ Wrong: ignoring a sleeping session with open_transaction_count > 0 (a forgotten COMMIT in app code,
--    e.g. an exception path that skips commit/rollback and returns the connection to the pool).
-- ✅ Fix the code path; consider RCSI (Q120) so readers stop queuing behind writers.
```

---

## 🎯 Interview Tip (1 line)
Say: "For blocking I query sys.dm_exec_requests for blocking_session_id, walk to the head blocker and check its open transactions and SQL text; for deadlocks I read the system_health graph. Then I fix the root cause: short transactions, indexes, RCSI, and proper commit or rollback in the application."

---

## 🔗 Related Questions
→ Q116 (deadlock graphs and index fixes) | Q122 (locks) | Q124 (deadlock prevention patterns) | Q177 (what is a deadlock and how do you fix one)
