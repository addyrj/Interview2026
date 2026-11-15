---

# Q121. SNAPSHOT Isolation
# Category: Transactions + Locking
# Difficulty: ⭐⭐⭐ Hard
# DB: SQL Server / Azure SQL (PostgreSQL REPEATABLE READ is snapshot-based; MySQL InnoDB REPEATABLE READ is also snapshot-style)

---

## ❓ Question
What is SNAPSHOT isolation, how is it enabled, how does it differ from RCSI, and what is an update conflict?

---

## 💡 Quick Concept (2 lines only)
SNAPSHOT gives the whole transaction a consistent view of data as of its first data access, using row versions, so there are no dirty reads, non-repeatable reads or phantoms and readers take no locks. If you try to update a row someone else changed after your snapshot, the update fails with an update conflict.
हिंदी: SNAPSHOT में पूरा transaction एक ही point-in-time view देखता है, बिना read locks के। अगर snapshot के बाद किसी ने वही row बदली और तुम update करो तो conflict error आता है।

---

## ✅ Answer / Solution

NOTE: not executed on SQL Server (needs two sessions); behaviour per Microsoft docs. The error number for an update conflict is deliberately not quoted here.

```sql
-- ============================================
-- SETUP
-- ============================================

ALTER DATABASE ShopDb SET ALLOW_SNAPSHOT_ISOLATION ON;
GO

USE ShopDb;
GO

CREATE TABLE dbo.Inventory (
    ProductId INT PRIMARY KEY,
    Qty       INT NOT NULL
);
INSERT INTO dbo.Inventory (ProductId, Qty) VALUES (1, 10);
GO

-- ============================================
-- TIMELINE
-- ============================================
-- Session A:
SET TRANSACTION ISOLATION LEVEL SNAPSHOT;
BEGIN TRANSACTION;
    SELECT Qty FROM dbo.Inventory WHERE ProductId = 1;      -- 10 (snapshot taken at first data access)

-- Session B (autocommit):
--   UPDATE dbo.Inventory SET Qty = 7 WHERE ProductId = 1;   -- commits

-- Session A (continued):
    SELECT Qty FROM dbo.Inventory WHERE ProductId = 1;      -- still 10 (repeatable, no blocking)

    UPDATE dbo.Inventory SET Qty = Qty - 1 WHERE ProductId = 1;
    -- Row was changed by a transaction that committed after A's snapshot started:
    -- SQL Server raises an update-conflict error and A's transaction is aborted. Retry from the start.
COMMIT TRANSACTION;

-- ============================================
-- SNAPSHOT vs RCSI
-- ============================================
-- Feature                    | READ_COMMITTED_SNAPSHOT        | SNAPSHOT
-- Consistency                | per statement                  | per transaction
-- Enable                     | database option, changes the   | ALLOW_SNAPSHOT_ISOLATION + the session
--                            | default behaviour automatically| must SET the level explicitly
-- Update-conflict detection  | no                             | yes
-- Phantoms / non-repeatable  | possible                       | not possible

-- Retry pattern for the conflict (application side or T-SQL): catch the error, ROLLBACK, re-run the transaction.
```

---

## 🔍 Why This Works (3 lines max)
At first data access the transaction is stamped with a sequence number and only reads versions at or before it. Writers still take exclusive locks; when a writer finds a newer committed version of a row than its snapshot, the engine aborts it to avoid a lost update. That is why SNAPSHOT is "optimistic" and needs retry logic.
हिंदी: Transaction शुरू होने पर एक snapshot number मिलता है, उसके बाद की changes नहीं दिखतीं। नई committed version मिले तो update fail होता है, इसलिए retry logic चाहिए।

---

## ⚡ Alternative Solution

```sql
-- Pessimistic alternative: take an update lock on the row when reading it
BEGIN TRANSACTION;
    SELECT Qty FROM dbo.Inventory WITH (UPDLOCK, ROWLOCK) WHERE ProductId = 1;
    UPDATE dbo.Inventory SET Qty = Qty - 1 WHERE ProductId = 1;
COMMIT TRANSACTION;
-- Other writers wait instead of failing; no retry loop, but less concurrency.
```

---

## ⚠️ Common Mistake

```sql
-- ❌ Wrong: ALLOW_SNAPSHOT_ISOLATION ON and expecting queries to use it automatically
-- It only makes it available; each session/transaction must run SET TRANSACTION ISOLATION LEVEL SNAPSHOT.

-- ❌ Wrong: long snapshot transactions - they pin row versions, the version store grows,
--    and reads of "stale" data become surprising for users.

-- ❌ Wrong: no retry when the update-conflict error appears
-- ✅ Treat it like a deadlock: ROLLBACK and retry the whole transaction a few times (Q130).
```

---

## 🎯 Interview Tip (1 line)
Say: "SNAPSHOT is transaction-level consistency with optimistic update-conflict detection, RCSI is statement-level and automatic. I use SNAPSHOT for reports and critical read-then-write flows where I can retry, and RCSI as the general fix for reader-writer blocking."

---

## 🔗 Related Questions
→ Q119 (isolation levels) | Q120 (RCSI) | Q127 (optimistic concurrency with rowversion) | Q130 (retry logic)
