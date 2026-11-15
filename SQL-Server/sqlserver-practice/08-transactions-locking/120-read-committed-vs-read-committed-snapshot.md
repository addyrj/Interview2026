---

# Q120. READ COMMITTED vs READ_COMMITTED_SNAPSHOT (RCSI)
# Category: Transactions + Locking
# Difficulty: ⭐⭐⭐ Hard
# DB: SQL Server / Azure SQL (Azure SQL Database has RCSI ON by default; PostgreSQL's READ COMMITTED is already MVCC)

---

## ❓ Question
Readers are blocked by an open UPDATE transaction. What is the difference between the default READ COMMITTED and READ_COMMITTED_SNAPSHOT, how do you turn it on, and what are the costs?

---

## 💡 Quick Concept (2 lines only)
Default READ COMMITTED takes shared locks, so a SELECT waits for an uncommitted writer. With RCSI the same isolation level reads the last committed row version from the version store, so readers do not block writers and writers do not block readers.
हिंदी: Default में SELECT को writer के commit का इंतज़ार करना पड़ता है। RCSI में SELECT पुराना committed version पढ़ता है, इसलिए blocking नहीं होती।

---

## ✅ Answer / Solution

NOTE: not executed on SQL Server (two concurrent sessions needed); timeline below is documented behaviour.

```sql
-- ============================================
-- SETUP
-- ============================================

CREATE TABLE dbo.Products (
    ProductId INT PRIMARY KEY,
    Name      VARCHAR(50)   NOT NULL,
    Price     DECIMAL(10,2) NOT NULL
);
INSERT INTO dbo.Products (ProductId, Name, Price) VALUES (1, 'Keyboard', 50.00);
GO

-- ============================================
-- TIMELINE (two sessions)
-- ============================================
-- Session A:  BEGIN TRAN; UPDATE dbo.Products SET Price = 60 WHERE ProductId = 1;   -- X lock, not committed
-- Session B:  SELECT Price FROM dbo.Products WHERE ProductId = 1;
--
--   Default READ COMMITTED : B waits (blocked) until A commits or rolls back
--   RCSI ON                : B returns 50.00 immediately (last committed value)
--
-- Session A:  COMMIT;
-- Session B:  SELECT again -> 60.00 in both modes (RCSI is statement-level, not transaction-level)

-- ============================================
-- ENABLE RCSI
-- ============================================

-- Needs exclusive access for the moment of the change; ROLLBACK IMMEDIATE kicks other sessions out.
ALTER DATABASE ShopDb SET READ_COMMITTED_SNAPSHOT ON WITH ROLLBACK IMMEDIATE;

-- Verify
SELECT name, is_read_committed_snapshot_on, snapshot_isolation_state_desc
FROM sys.databases
WHERE name = 'ShopDb';
-- Expect is_read_committed_snapshot_on = 1 after the change.

-- ============================================
-- COSTS
-- ============================================
-- * Row versions are kept (tempdb, or the persistent version store with Accelerated Database Recovery)
-- * Each modified row gets 14 extra bytes of versioning info
-- * Long-running open transactions make the version store grow
-- * Writers still block writers (update conflicts are not detected in RCSI - last writer wins after the lock)

-- Opt a single query out and force the old locking read:
SELECT Price FROM dbo.Products WITH (READCOMMITTEDLOCK) WHERE ProductId = 1;
```

---

## 🔍 Why This Works (3 lines max)
With RCSI each statement sees the data as of the statement start, built from row versions kept for modified rows. The shared-lock requirement for reads disappears, which removes most reader-writer blocking and many deadlocks without changing application code. The price is version store space and slightly more IO/CPU for writes.
हिंदी: हर statement अपने शुरू होने के समय का committed data देखता है। Shared lock की ज़रूरत नहीं, इसलिए reader-writer blocking खत्म। कीमत: version store की जगह।

---

## ⚡ Alternative Solution

```sql
-- Full SNAPSHOT isolation (transaction-level consistent view, update-conflict detection) - see Q121
ALTER DATABASE ShopDb SET ALLOW_SNAPSHOT_ISOLATION ON;

-- Monitor the version store size (tempdb)
SELECT SUM(version_store_reserved_page_count) * 8 / 1024.0 AS version_store_mb
FROM sys.dm_db_file_space_usage;
-- Run this in tempdb context on SQL Server (when ADR is not used for versions).
```

---

## ⚠️ Common Mistake

```sql
-- ❌ Wrong: enabling RCSI and expecting a read-modify-write to become safe
SELECT @qty = Qty FROM dbo.Inventory WHERE ProductId = 1;   -- reads a version, takes no lock
UPDATE dbo.Inventory SET Qty = @qty - 1 WHERE ProductId = 1;  -- lost update possible
-- ✅ Use UPDATE ... SET Qty = Qty - 1 WHERE Qty > 0, or SELECT ... WITH (UPDLOCK), or rowversion (Q127).

-- ❌ Wrong: relying on locks for logic that RCSI silently changes
-- Code written with the assumption "a reader waits for the writer" (e.g. polling) sees old values now.

-- ❌ Wrong: leaving a transaction open for hours with RCSI on -> version store keeps growing.
```

---

## 🎯 Interview Tip (1 line)
Say: "I enable RCSI on OLTP databases to remove reader-writer blocking without code changes, and I know the trade-offs: version store in tempdb, 14 bytes per row, and read-modify-write patterns still need UPDLOCK or atomic updates. Azure SQL Database already has it on by default."

---

## 🔗 Related Questions
→ Q119 (isolation levels) | Q121 (SNAPSHOT isolation) | Q123 (blocking vs deadlock) | Q127 (optimistic concurrency with rowversion)
