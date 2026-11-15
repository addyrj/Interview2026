---

# Q125. Lock Hints — NOLOCK Dangers, UPDLOCK, READPAST
# Category: Transactions + Locking
# Difficulty: ⭐⭐⭐ Hard
# DB: SQL Server (PostgreSQL: SELECT ... FOR UPDATE SKIP LOCKED; MySQL 8: FOR UPDATE SKIP LOCKED)

---

## ❓ Question
What do `NOLOCK`, `UPDLOCK`, `HOLDLOCK`, `ROWLOCK`, `XLOCK` and `READPAST` do? Why is NOLOCK dangerous, and what are the safer alternatives?

---

## 💡 Quick Concept (2 lines only)
NOLOCK = READ UNCOMMITTED for that table: no shared locks, so you can read uncommitted data, miss rows or read rows twice. UPDLOCK reserves rows for update, HOLDLOCK keeps range locks (SERIALIZABLE), READPAST skips rows that are locked by others.
हिंदी: NOLOCK = बिना lock पढ़ना, uncommitted/गलत data मिल सकता है। UPDLOCK = row reserve, HOLDLOCK = serializable, READPAST = locked rows skip।

---

## ✅ Answer / Solution

NOTE: lock behaviour not executed on SQL Server; behaviour per Microsoft docs.

```sql
-- ============================================
-- SETUP
-- ============================================

CREATE TABLE dbo.Orders (
    OrderId    INT PRIMARY KEY,
    CustomerId INT           NOT NULL,
    Status     VARCHAR(20)   NOT NULL,
    Amount     DECIMAL(10,2) NOT NULL
);
INSERT INTO dbo.Orders (OrderId, CustomerId, Status, Amount) VALUES
  (1, 10, 'Pending', 100), (2, 11, 'Pending', 200), (3, 12, 'Shipped', 300);
GO

-- ============================================
-- NOLOCK DANGERS
-- ============================================
SELECT SUM(Amount) FROM dbo.Orders WITH (NOLOCK);
-- 1. Dirty read: sees an UPDATE that is later rolled back
-- 2. Missing/duplicate rows: a page split during the scan can make rows be skipped or read twice
-- 3. Can fail with an error about data movement in some cases (allocation-order scan)
-- 4. Not a "free speed-up": under RCSI (Q120) readers do not block anyway, so use that instead.
-- Acceptable only for rough monitoring counts where wrong numbers are fine.

-- ============================================
-- UPDLOCK: safe read-then-write on one row
-- ============================================
BEGIN TRANSACTION;
    SELECT Status FROM dbo.Orders WITH (UPDLOCK, ROWLOCK) WHERE OrderId = 1;   -- reserve the row
    UPDATE dbo.Orders SET Status = 'Processing' WHERE OrderId = 1 AND Status = 'Pending';
COMMIT TRANSACTION;

-- ============================================
-- HOLDLOCK (= SERIALIZABLE): protect "insert if not exists" from races
-- ============================================
BEGIN TRANSACTION;
    IF NOT EXISTS (SELECT 1 FROM dbo.Orders WITH (UPDLOCK, HOLDLOCK) WHERE OrderId = 4)
        INSERT INTO dbo.Orders (OrderId, CustomerId, Status, Amount) VALUES (4, 13, 'Pending', 50);
COMMIT TRANSACTION;
-- Range lock stops another session inserting OrderId = 4 between the check and the insert.

-- ============================================
-- READPAST: skip locked rows instead of waiting (queue pattern, see Q126)
-- ============================================
SELECT TOP (1) OrderId FROM dbo.Orders WITH (READPAST, UPDLOCK) WHERE Status = 'Pending' ORDER BY OrderId;

-- ============================================
-- Others
-- ============================================
-- ROWLOCK  : prefer row-level locks (can raise total lock count and escalation risk)
-- TABLOCKX : exclusive table lock (bulk loads, maintenance)
-- XLOCK    : take exclusive locks on read
-- READCOMMITTEDLOCK : force locking read even when RCSI is on
```

---

## 🔍 Why This Works (3 lines max)
Lock hints change which lock mode and how long it is held for that table in that statement. UPDLOCK + HOLDLOCK make a check-then-insert atomic; READPAST turns "wait" into "skip". NOLOCK skips locking entirely, which is why correctness guarantees disappear.
हिंदी: Hint बताता है कौन सा lock और कितनी देर। UPDLOCK+HOLDLOCK से check-then-insert atomic होता है। NOLOCK में correctness की guarantee ही खत्म।

---

## ⚡ Alternative Solution

```sql
-- Instead of NOLOCK for reporting: enable RCSI so readers see committed data without blocking
ALTER DATABASE ShopDb SET READ_COMMITTED_SNAPSHOT ON WITH ROLLBACK IMMEDIATE;

-- Instead of check-then-insert with hints: a UNIQUE constraint and handle the duplicate-key error
-- (the database enforces it, no hint needed).
```

---

## ⚠️ Common Mistake

```sql
-- ❌ Wrong: NOLOCK on financial / inventory / reporting totals
SELECT SUM(Amount) FROM dbo.Orders WITH (NOLOCK);   -- may include rolled-back or double-counted rows

-- ❌ Wrong: IF EXISTS (...) INSERT ... without UPDLOCK/HOLDLOCK or a unique constraint
--    two sessions both pass the check, both insert.

-- ❌ Wrong: READPAST on a query where skipping rows changes the meaning
--    (e.g. SUM, COUNT or "is there any pending order for this customer?").

-- ❌ Wrong: adding hints everywhere instead of finding the blocker (Q123).
```

---

## 🎯 Interview Tip (1 line)
Say: "NOLOCK is READ UNCOMMITTED: dirty reads plus skipped or duplicated rows, so I replace it with RCSI. I use UPDLOCK for read-then-update, UPDLOCK+HOLDLOCK for upsert races (or better a unique constraint), and READPAST only for queue-style workers."

---

## 🔗 Related Questions
→ Q120 (RCSI) | Q122 (locks) | Q126 (queue processing with READPAST) | Q183 (NOLOCK — good or bad)
