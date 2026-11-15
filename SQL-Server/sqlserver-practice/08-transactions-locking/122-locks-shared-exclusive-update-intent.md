---

# Q122. Locks — Shared, Exclusive, Update, Intent
# Category: Transactions + Locking
# Difficulty: ⭐⭐⭐ Hard
# DB: SQL Server (InnoDB and PostgreSQL also have row/table lock modes, with different names)

---

## ❓ Question
Explain S, X, U and intent locks (IS, IX), lock granularity (row, page, table), compatibility, and how you inspect current locks.

---

## 💡 Quick Concept (2 lines only)
S (shared) is taken for reads, X (exclusive) for writes, U (update) when reading with the intent to update (avoids conversion deadlocks), and intent locks (IS/IX) on higher levels (page/table) announce that rows below are locked. Only S+S (and S+U) are compatible; X conflicts with everything.
हिंदी: S = read, X = write, U = "पढ़ूँगा फिर बदलूँगा"। Intent locks (IS/IX) table/page पर बताते हैं कि नीचे rows locked हैं। X सबसे सख्त है।

---

## ✅ Answer / Solution

NOTE: not executed on SQL Server; behaviour per Microsoft docs. The DMV columns used (resource_type, request_mode, request_status, request_session_id) are documented ones; no sample rows are shown.

```sql
-- ============================================
-- SETUP
-- ============================================

CREATE TABLE dbo.Customers (
    CustomerId INT PRIMARY KEY,
    Name       VARCHAR(50) NOT NULL,
    City       VARCHAR(50) NOT NULL
);
INSERT INTO dbo.Customers (CustomerId, Name, City) VALUES
  (1, 'Asha', 'Pune'), (2, 'Ravi', 'Delhi'), (3, 'Meera', 'Mumbai');
GO

-- ============================================
-- COMPATIBILITY (documented, requested mode vs granted mode)
-- ============================================
--        | granted IS | IX | S  | U  | X
-- req IS |    yes     | yes| yes| yes| no
-- req IX |    yes     | yes| no | no | no
-- req S  |    yes     | no | yes| yes| no
-- req U  |    yes     | no | yes| no | no
-- req X  |    no      | no | no | no | no

-- ============================================
-- WHAT A SINGLE-ROW UPDATE LOCKS (conceptually)
-- ============================================
-- IX on the table  ->  IX on the page  ->  X on the key (row)
-- A second session updating a different row: IX + IX compatible, different keys -> no blocking.

-- ============================================
-- LOOK AT LOCKS HELD BY OPEN TRANSACTIONS
-- ============================================

BEGIN TRANSACTION;
    UPDATE dbo.Customers SET City = 'Bengaluru' WHERE CustomerId = 1;

    SELECT request_session_id, resource_type, request_mode, request_status
    FROM sys.dm_tran_locks
    WHERE resource_database_id = DB_ID()
      AND request_session_id = @@SPID;
    -- Expect (per docs): an OBJECT lock in IX mode, a PAGE lock in IX mode and a KEY lock in X mode,
    -- all with request_status GRANT.
ROLLBACK TRANSACTION;

-- ============================================
-- Why U locks exist
-- ============================================
-- Two sessions both do: SELECT (S lock) ... then UPDATE (needs X) -> each waits for the other's S -> deadlock.
-- UPDLOCK takes U instead: only one session can hold U on the row, so the second waits at the read, no cycle.

BEGIN TRANSACTION;
    SELECT Name, City FROM dbo.Customers WITH (UPDLOCK) WHERE CustomerId = 2;
    UPDATE dbo.Customers SET City = 'Chennai' WHERE CustomerId = 2;
COMMIT TRANSACTION;

-- ============================================
-- Lock escalation: ~5,000 locks on one object in a statement can escalate row/page locks to a table lock
-- ============================================
ALTER TABLE dbo.Customers SET (LOCK_ESCALATION = AUTO);   -- options: TABLE (default), AUTO, DISABLE
```

---

## 🔍 Why This Works (3 lines max)
Intent locks let the engine check for conflicts at table level without scanning every row lock. U locks are asymmetric (compatible with S, not with another U) so two read-then-update transactions serialize safely. Locks are held until the end of the transaction for writes, which is why short transactions matter.
हिंदी: Intent locks से table level पर conflict जल्दी पता चलता है। U lock दो read-then-update transactions को serialize करता है। Write locks transaction के अंत तक रहते हैं।

---

## ⚡ Alternative Solution

```sql
-- Same locks as a rowset using the older helper (shows spid, object, mode, status)
EXEC sp_lock;      -- deprecated in favour of sys.dm_tran_locks, but still seen in interviews
```

---

## ⚠️ Common Mistake

```sql
-- ❌ Wrong: "SELECT never blocks" - in READ COMMITTED (without RCSI) a SELECT needs an S lock and waits for X.
-- ❌ Wrong: forgetting that a missing index forces a scan that S/U-locks many rows (Q116).
-- ❌ Wrong: thinking lock escalation is a bug - it is a memory-saving feature; fix queries or batch the work (Q145)
--    rather than disabling it blindly.
-- ❌ Wrong: leaving an explicit transaction open across user think-time.
```

---

## 🎯 Interview Tip (1 line)
Say: "I explain the hierarchy IX on table, IX on page, X on key, then the compatibility rules, and that U locks prevent the classic S-to-X conversion deadlock. I use sys.dm_tran_locks to inspect, and I know escalation can turn many row locks into a table lock."

---

## 🔗 Related Questions
→ Q123 (blocking vs deadlock) | Q124 (deadlock prevention) | Q125 (lock hints) | Q145 (batching large updates/deletes)
