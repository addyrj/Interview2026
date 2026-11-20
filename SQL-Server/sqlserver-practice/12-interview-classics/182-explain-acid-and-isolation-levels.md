---

# Q182. Explain ACID and Isolation Levels
# Category: Interview Classics
# Difficulty: ⭐⭐⭐ Hard
# DB: SQL Server (PostgreSQL defaults to READ COMMITTED with MVCC; MySQL InnoDB defaults to REPEATABLE READ; SQL Server's default is locking READ COMMITTED, but Azure SQL Database enables READ_COMMITTED_SNAPSHOT)

---

## ❓ Question
Explain ACID with a money-transfer example, then explain SQL Server's isolation levels, which anomalies each prevents, and which one you would choose for an Express API.

---

## 💡 Quick Concept (2 lines only)
ACID = Atomicity (all or nothing), Consistency (constraints always hold), Isolation (concurrent transactions do not see each other's half-done work), Durability (committed data survives a crash, via the write-ahead log). Isolation levels trade correctness against concurrency: lower levels allow dirty/non-repeatable/phantom reads.
हिंदी: ACID = पूरा या कुछ नहीं, constraints सही, transactions एक-दूसरे से अलग, commit के बाद data सुरक्षित। Isolation जितना ऊँचा, उतना safe पर slow।

---

## ✅ Answer / Solution

```sql
-- ============================================
-- NOT EXECUTED ON SQL SERVER: isolation anomalies need two concurrent sessions and no SQL Server
-- instance exists in the authoring environment. Behaviour per Microsoft docs; syntax parsed with sqlglot.
-- ============================================
CREATE TABLE dbo.Accounts (
  AccountId INT PRIMARY KEY,
  Balance   DECIMAL(12,2) NOT NULL CONSTRAINT CK_Balance_NonNegative CHECK (Balance >= 0)
);
INSERT INTO dbo.Accounts VALUES (1, 1000.00), (2, 500.00);

-- ATOMICITY + CONSISTENCY + DURABILITY in one transaction
SET XACT_ABORT ON;            -- any runtime error aborts and rolls back the whole transaction
BEGIN TRANSACTION;
  UPDATE dbo.Accounts SET Balance = Balance - 200 WHERE AccountId = 1;
  UPDATE dbo.Accounts SET Balance = Balance + 200 WHERE AccountId = 2;
COMMIT TRANSACTION;           -- durable once the log record is hardened to disk
-- Hand-checked result: balances become 800.00 and 700.00 (total stays 1500.00)
-- A transfer of 5000 would violate CK_Balance_NonNegative -> error, XACT_ABORT rolls back -> 1000 / 500 remain.

-- ============================================
-- ISOLATION LEVELS (set per session / transaction)
-- ============================================
SET TRANSACTION ISOLATION LEVEL READ COMMITTED;     -- default (on-prem). Azure SQL DB: RCSI row versioning.
-- Others: READ UNCOMMITTED | REPEATABLE READ | SNAPSHOT | SERIALIZABLE

-- Check what your database uses:
SELECT name, is_read_committed_snapshot_on, snapshot_isolation_state_desc
FROM sys.databases WHERE name = DB_NAME();

-- Enabling row-versioning options (needs a quiet moment or WITH ROLLBACK IMMEDIATE):
ALTER DATABASE ShopDb SET READ_COMMITTED_SNAPSHOT ON WITH ROLLBACK IMMEDIATE;
ALTER DATABASE ShopDb SET ALLOW_SNAPSHOT_ISOLATION ON;
```

```sql
-- Anomalies prevented (per Microsoft documentation)
-- Level                | Dirty read | Non-repeatable read | Phantom   | Mechanism
-- READ UNCOMMITTED     | possible   | possible            | possible  | no shared locks (NOLOCK)
-- READ COMMITTED       | prevented  | possible            | possible  | shared locks released right after the read (or row versions with RCSI)
-- REPEATABLE READ      | prevented  | prevented           | possible  | shared locks held to end of transaction
-- SNAPSHOT             | prevented  | prevented           | prevented | row versions; update conflicts raise an error
-- SERIALIZABLE         | prevented  | prevented           | prevented | range locks held to end of transaction
```

```javascript
// Node.js (mssql): isolation level per transaction
const tx = new sql.Transaction(pool);
await tx.begin(sql.ISOLATION_LEVEL.READ_COMMITTED);   // or REPEATABLE_READ, SERIALIZABLE, SNAPSHOT
try {
  await new sql.Request(tx).query('UPDATE dbo.Accounts SET Balance = Balance - 200 WHERE AccountId = 1');
  await new sql.Request(tx).query('UPDATE dbo.Accounts SET Balance = Balance + 200 WHERE AccountId = 2');
  await tx.commit();
} catch (e) { await tx.rollback(); throw e; }
```

---

## 🔍 Why This Works (3 lines max)
The transaction log is written before data pages (write-ahead logging), which gives atomic rollback and crash-safe durability; constraints supply consistency. Isolation uses either locks (readers block writers at higher levels) or row versions in tempdb/version store (readers do not block). Higher isolation holds more locks for longer, so deadlocks and blocking rise.
हिंदी: Write-ahead log से rollback और durability मिलती है। Isolation = locks या row versions। ऊँचा level = ज़्यादा blocking।

---

## ⚡ Alternative Solution

```sql
-- Optimistic concurrency without a high isolation level: rowversion column (Q127)
UPDATE dbo.Accounts SET Balance = Balance - 200
WHERE AccountId = 1 AND RowVer = @OriginalRowVer;   -- 0 rows affected => someone else changed it, retry
-- Read-then-write on the same row: SELECT ... WITH (UPDLOCK, ROWLOCK) inside the transaction (Q125).
-- Reporting that must see a stable picture: SNAPSHOT isolation, no blocking of writers.
```

---

## ⚠️ Common Mistake

```sql
-- ❌ Wrong: believing a "transaction" in SQL alone protects a read-modify-write done in app code:
--    SELECT balance (tx 1) ... app computes ... UPDATE: another request can slip in between at READ COMMITTED.
--    Do it in one UPDATE (Balance = Balance - @Amt) or use UPDLOCK / rowversion.
-- ❌ Wrong: SERIALIZABLE everywhere "to be safe": heavy locking and deadlocks.
-- ❌ Wrong: not setting XACT_ABORT ON, so a runtime error leaves the transaction open (Q118).
-- ❌ Wrong: long transactions around HTTP calls; version store and locks grow.
-- ❌ Wrong: thinking SNAPSHOT is free: it uses tempdb/version store space and can fail on update conflicts.
```

---

## 🎯 Interview Tip (5+ YOE level)
Say: "I default to READ COMMITTED with row versioning (RCSI), which is already the Azure SQL default, so readers do not block writers. For read-modify-write I use a single atomic UPDATE, UPDLOCK, or rowversion-based optimistic concurrency, and I keep transactions short with XACT_ABORT ON. SERIALIZABLE or SNAPSHOT only for specific invariants, and I handle deadlock and update-conflict retries in the app." Contrast with MySQL's REPEATABLE READ default to show breadth.

---

## 🔗 Related Questions
→ Q117 (ACID in SQL Server) | Q119 (isolation levels overview) | Q120 (READ COMMITTED vs RCSI) | Q121 (SNAPSHOT isolation) | Q127 (optimistic concurrency with rowversion)
