---

# Q119. Isolation Levels Overview
# Category: Transactions + Locking
# Difficulty: ⭐⭐ Medium
# DB: SQL Server (default READ COMMITTED with locks; PostgreSQL default is READ COMMITTED with MVCC; MySQL InnoDB default is REPEATABLE READ)

---

## ❓ Question
List SQL Server's five isolation levels, which anomalies (dirty read, non-repeatable read, phantom) each one allows, and how to set them.

---

## 💡 Quick Concept (2 lines only)
Higher isolation = fewer anomalies but more blocking (locking levels) or more version storage (snapshot levels). Default is READ COMMITTED: no dirty reads, but non-repeatable reads and phantoms are possible.
हिंदी: Isolation जितना ऊँचा, anomalies उतनी कम, पर blocking ज़्यादा। Default READ COMMITTED में dirty read नहीं होती, पर non-repeatable read और phantom हो सकते हैं।

---

## ✅ Answer / Solution

NOTE: table below is the documented behaviour (Microsoft docs); not executed on SQL Server.

```sql
-- ============================================
-- SETUP (for the examples)
-- ============================================

CREATE TABLE dbo.Inventory (
    ProductId INT PRIMARY KEY,
    Qty       INT NOT NULL
);
INSERT INTO dbo.Inventory (ProductId, Qty) VALUES (1, 10), (2, 5);
GO

-- ============================================
-- ANOMALY MATRIX (documented)
-- ============================================
-- Level                      | Dirty read | Non-repeatable read | Phantom | Mechanism
-- READ UNCOMMITTED           | possible   | possible            | possible| no shared locks (same as NOLOCK)
-- READ COMMITTED (default)   | no         | possible            | possible| shared locks released after read
--   + READ_COMMITTED_SNAPSHOT| no         | possible            | possible| row versions, readers do not block
-- REPEATABLE READ            | no         | no                  | possible| shared locks held to end of transaction
-- SNAPSHOT                   | no         | no                  | no      | row versions, needs ALLOW_SNAPSHOT_ISOLATION
-- SERIALIZABLE               | no         | no                  | no      | key-range locks

-- ============================================
-- SET THE LEVEL (per session / transaction)
-- ============================================

SET TRANSACTION ISOLATION LEVEL REPEATABLE READ;
BEGIN TRANSACTION;
    SELECT Qty FROM dbo.Inventory WHERE ProductId = 1;   -- shared lock kept until COMMIT
    -- another session's UPDATE on ProductId = 1 now blocks until we finish
    SELECT Qty FROM dbo.Inventory WHERE ProductId = 1;   -- same value guaranteed
COMMIT TRANSACTION;

-- Check the current session level
SELECT CASE transaction_isolation_level
         WHEN 0 THEN 'Unspecified'
         WHEN 1 THEN 'ReadUncommitted'
         WHEN 2 THEN 'ReadCommitted'
         WHEN 3 THEN 'RepeatableRead'
         WHEN 4 THEN 'Serializable'
         WHEN 5 THEN 'Snapshot'
       END AS IsolationLevel
FROM sys.dm_exec_sessions
WHERE session_id = @@SPID;
-- Expected for a fresh connection: ReadCommitted

-- Per-table override with a hint:
SELECT Qty FROM dbo.Inventory WITH (HOLDLOCK) WHERE ProductId = 1;   -- = SERIALIZABLE for this table
```

---

## 🔍 Why This Works (3 lines max)
Locking levels (REPEATABLE READ, SERIALIZABLE) keep shared or key-range locks to the end of the transaction, so other writers wait. Snapshot levels give each transaction a consistent view from row versions in tempdb (or the PVS with Accelerated Database Recovery), so readers and writers do not block each other. You choose between blocking and version storage cost.
हिंदी: Locking levels में lock अंत तक रखा जाता है, इसलिए writers रुकते हैं। Snapshot levels में row versions से consistent view मिलता है, blocking कम।

---

## ⚡ Alternative Solution

```sql
-- Set it at connection level from Node.js (mssql): run the SET statement, or set it on the transaction:
-- const tx = new sql.Transaction(pool);
-- await tx.begin(sql.ISOLATION_LEVEL.REPEATABLE_READ);

-- For most OLTP apps the practical choice is: READ_COMMITTED_SNAPSHOT ON at database level (Q120),
-- and SNAPSHOT or SERIALIZABLE only for specific critical transactions.
```

---

## ⚠️ Common Mistake

```sql
-- ❌ Wrong: using SERIALIZABLE globally "to be safe"
-- Key-range locks make throughput collapse and deadlocks common.

-- ❌ Wrong: believing READ COMMITTED guarantees a read-then-update is safe
-- SELECT Qty ... ; IF Qty > 0 UPDATE ...   -- another session can change Qty in between (lost update)
-- ✅ Use UPDATE ... WHERE Qty > 0 atomically, UPDLOCK, rowversion (Q127), or a higher level.

-- ❌ Wrong: confusing MySQL and SQL Server defaults
-- MySQL InnoDB defaults to REPEATABLE READ; SQL Server's default is READ COMMITTED.
```

---

## 🎯 Interview Tip (1 line)
Say: "SQL Server's default is READ COMMITTED with locking, which can block readers behind writers. For web workloads I normally enable READ_COMMITTED_SNAPSHOT, use SNAPSHOT or UPDLOCK for specific read-modify-write cases, and keep SERIALIZABLE for rare invariants like range uniqueness."

---

## 🔗 Related Questions
→ Q117 (ACID) | Q120 (READ COMMITTED vs RCSI) | Q121 (SNAPSHOT isolation) | Q182 (explain ACID and isolation levels)
