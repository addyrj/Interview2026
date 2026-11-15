---

# Q117. ACID in SQL Server
# Category: Transactions + Locking
# Difficulty: ⭐⭐ Medium
# DB: SQL Server (MySQL InnoDB and PostgreSQL are also ACID; MySQL MyISAM is not)

---

## ❓ Question
Explain Atomicity, Consistency, Isolation and Durability with a bank transfer, and say which SQL Server mechanism provides each one.

---

## 💡 Quick Concept (2 lines only)
Atomic = all or nothing (rollback). Consistent = constraints always hold. Isolated = concurrent transactions do not see half-done work (locks/row versioning). Durable = committed data survives a crash (write-ahead transaction log).
हिंदी: Atomic = सब या कुछ नहीं। Consistent = constraints नहीं टूटते। Isolated = बीच का काम दूसरों को नहीं दिखता। Durable = commit के बाद crash में भी data सुरक्षित (log)।

---

## ✅ Answer / Solution

```sql
-- ============================================
-- SETUP
-- ============================================

CREATE TABLE dbo.Accounts (
    AccountId INT           NOT NULL PRIMARY KEY,
    Owner     VARCHAR(50)   NOT NULL,
    Balance   DECIMAL(12,2) NOT NULL CONSTRAINT CK_Accounts_Balance CHECK (Balance >= 0)
);

INSERT INTO dbo.Accounts (AccountId, Owner, Balance) VALUES
  (1, 'Asha', 1000.00),
  (2, 'Ravi',  500.00);
GO

-- ============================================
-- A + D: transfer 300 from Asha to Ravi, atomically
-- ============================================

SET XACT_ABORT ON;
BEGIN TRANSACTION;
    UPDATE dbo.Accounts SET Balance = Balance - 300 WHERE AccountId = 1;
    UPDATE dbo.Accounts SET Balance = Balance + 300 WHERE AccountId = 2;
COMMIT TRANSACTION;           -- log record flushed to disk before COMMIT returns = Durable

SELECT AccountId, Owner, Balance FROM dbo.Accounts ORDER BY AccountId;
-- Result derived from equivalent statements on SQLite; not executed on SQL Server:
-- AccountId | Owner | Balance
-- 1         | Asha  | 700
-- 2         | Ravi  | 800

-- ============================================
-- C: the CHECK constraint rejects an invalid state, so the whole transaction rolls back
-- ============================================

BEGIN TRANSACTION;
    UPDATE dbo.Accounts SET Balance = Balance + 2000 WHERE AccountId = 2;
    UPDATE dbo.Accounts SET Balance = Balance - 2000 WHERE AccountId = 1;   -- violates CK_Accounts_Balance
COMMIT TRANSACTION;
-- The second UPDATE raises a constraint-violation error; with XACT_ABORT ON the whole transaction is rolled back.
-- Equivalent test on SQLite: error "CHECK constraint failed: Balance>=0", balances stay 700 / 800.
-- (SQL Server's exact error text/number not reproduced here.)

SELECT AccountId, Balance FROM dbo.Accounts ORDER BY AccountId;
-- AccountId | Balance
-- 1         | 700
-- 2         | 800

-- ============================================
-- I: isolation is chosen per session
-- ============================================

SET TRANSACTION ISOLATION LEVEL READ COMMITTED;   -- default; see Q119/Q120 for the others
```

---

## 🔍 Why This Works (3 lines max)
Every change is first written to the transaction log (write-ahead logging); COMMIT waits for the log flush, so recovery can redo committed work and undo uncommitted work after a crash. Constraints are validated per statement, and an error plus rollback restores the previous state. Locks (or row versions) keep other sessions from reading uncommitted values.
हिंदी: पहले log में लिखा जाता है, फिर commit return होता है। Crash के बाद redo/undo से recovery होती है। Locks या row versions से isolation मिलता है।

---

## ⚡ Alternative Solution

```sql
-- Same atomicity using TRY...CATCH (explicit rollback and re-raise) - not executed on SQL Server
BEGIN TRY
    BEGIN TRANSACTION;
        UPDATE dbo.Accounts SET Balance = Balance - 300 WHERE AccountId = 1;
        UPDATE dbo.Accounts SET Balance = Balance + 300 WHERE AccountId = 2;
    COMMIT TRANSACTION;
END TRY
BEGIN CATCH
    IF @@TRANCOUNT > 0 ROLLBACK TRANSACTION;
    THROW;
END CATCH;
```

---

## ⚠️ Common Mistake

```sql
-- ❌ Wrong: assuming a multi-statement batch is atomic without a transaction
UPDATE dbo.Accounts SET Balance = Balance - 300 WHERE AccountId = 1;
UPDATE dbo.Accounts SET Balance = Balance + 300 WHERE AccountId = 2;
-- Each statement is its own auto-commit transaction (the default autocommit mode).
-- If the second fails, the first stays committed -> money disappears.

-- ❌ Wrong: no SET XACT_ABORT ON and no TRY...CATCH: some errors leave the transaction open and
--    the next statements keep running.

-- ❌ Wrong: "durable" with DELAYED_DURABILITY = FORCED on a bank table (can lose the last commits on crash).
```

---

## 🎯 Interview Tip (1 line)
Say: "Atomicity and durability come from the write-ahead log, consistency from constraints plus correct application logic, and isolation is tunable: default READ COMMITTED, with RCSI or SNAPSHOT to reduce blocking. I always wrap multi-statement changes in an explicit transaction with XACT_ABORT ON."

---

## 🔗 Related Questions
→ Q118 (BEGIN TRAN, COMMIT, ROLLBACK, XACT_ABORT) | Q119 (isolation levels) | Q131 (transaction log and recovery models) | Q182 (explain ACID and isolation levels)
