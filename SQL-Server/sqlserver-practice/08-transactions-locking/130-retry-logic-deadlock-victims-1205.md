
---

# Q130. Retry Logic for Deadlock Victims (Error 1205)
# Category: TRANSACTIONS + LOCKING
# Difficulty: ⭐⭐⭐ Hard
# DB: SQL Server (PostgreSQL deadlock is SQLSTATE 40P01; MySQL error 1213; SQL Server is 1205)

---

## ❓ Question
Under load, `usp_TransferFunds` occasionally fails with "Transaction was deadlocked ... chosen as the deadlock victim" (error 1205). Write retry logic in T-SQL and in Node.js so the caller transparently retries a limited number of times.

---

## 💡 Quick Concept (2 lines only)
SQL Server kills one session in a deadlock (the cheapest to roll back) with error 1205 and rolls its transaction back; the work is safe to retry because nothing was committed. Retry with a bounded loop and a small randomized delay.
हिंदी: Deadlock में SQL Server एक session को victim बनाकर error 1205 देता है और rollback कर देता है। पूरा transaction फिर से चलाना safe है, पर limit और random delay के साथ।

---

## ✅ Answer / Solution

```sql
-- ============================================
-- SETUP
-- ============================================
CREATE TABLE dbo.Accounts (
  AccountId INT PRIMARY KEY,
  Balance   DECIMAL(12,2) NOT NULL CHECK (Balance >= 0)
);
INSERT INTO dbo.Accounts VALUES (1, 1000.00), (2, 500.00);
GO

CREATE OR ALTER PROCEDURE dbo.usp_TransferFunds
  @From INT, @To INT, @Amount DECIMAL(12,2)
AS
BEGIN
  SET NOCOUNT ON; SET XACT_ABORT ON;
  BEGIN TRAN;
    UPDATE dbo.Accounts SET Balance = Balance - @Amount WHERE AccountId = @From;
    UPDATE dbo.Accounts SET Balance = Balance + @Amount WHERE AccountId = @To;
  COMMIT;
END;
GO

-- ============================================
-- SOLUTION: T-SQL retry wrapper
-- ============================================
CREATE OR ALTER PROCEDURE dbo.usp_TransferFunds_Retry
  @From INT, @To INT, @Amount DECIMAL(12,2)
AS
BEGIN
  SET NOCOUNT ON;
  DECLARE @try INT = 1, @max INT = 3, @delay CHAR(12);

  WHILE @try <= @max
  BEGIN
    BEGIN TRY
      EXEC dbo.usp_TransferFunds @From, @To, @Amount;
      RETURN 0;                                   -- success
    END TRY
    BEGIN CATCH
      IF XACT_STATE() <> 0 ROLLBACK;              -- make sure nothing is left open

      IF ERROR_NUMBER() = 1205 AND @try < @max    -- deadlock victim -> retry
      BEGIN
        SET @try += 1;
        -- 50-250 ms jitter so both sessions do not collide again
        SET @delay = '00:00:00.' + RIGHT('000' + CAST(50 + ABS(CHECKSUM(NEWID())) % 200 AS VARCHAR(3)), 3);
        WAITFOR DELAY @delay;
      END
      ELSE
        THROW;                                    -- other errors or retries exhausted
    END CATCH
  END
END;
GO

EXEC dbo.usp_TransferFunds_Retry @From = 1, @To = 2, @Amount = 100.00;
```

```js
// Node.js (mssql): retry on 1205 (and optionally transient Azure errors 40613, 40501, 49918)
async function withRetry(fn, max = 3) {
  for (let attempt = 1; ; attempt++) {
    try { return await fn(); }
    catch (e) {
      const retryable = e.number === 1205 || (e.originalError && e.originalError.number === 1205);
      if (!retryable || attempt >= max) throw e;
      await new Promise(r => setTimeout(r, 50 * attempt + Math.random() * 100));
    }
  }
}
await withRetry(() => pool.request()
  .input('From', sql.Int, 1).input('To', sql.Int, 2).input('Amount', sql.Decimal(12,2), 100)
  .execute('dbo.usp_TransferFunds'));
```

```sql
-- EXPECTED OUTPUT
-- Deadlocks cannot be reproduced on a single connection; not executed on SQL Server.
-- Balances after a successful transfer of 100.00 (hand-checked): AccountId 1 = 900.00, AccountId 2 = 600.00
-- If 1205 hits the first attempt the whole transaction was rolled back, so the retry applies the
-- transfer exactly once.
```

---

## 🔍 Why This Works (3 lines max)
The victim's transaction is fully rolled back, so re-running the unit of work cannot double-apply it. Jitter breaks symmetry, and the retry cap prevents infinite loops during a real design-level deadlock.
हिंदी: Victim का transaction पूरा rollback हो चुका होता है, इसलिए दोबारा चलाने से दो बार apply नहीं होगा। Jitter से दोनों session फिर नहीं टकराते।

---

## ⚡ Alternative Solution

```sql
-- Fix the cause: lock in a consistent order (lowest AccountId first)
UPDATE dbo.Accounts SET Balance = Balance - IIF(AccountId = @From, @Amount, -@Amount)
WHERE  AccountId IN (@From, @To);        -- single statement, locks acquired in index order
-- Also: shorter transactions, proper indexes, READ_COMMITTED_SNAPSHOT to remove reader/writer deadlocks.
-- SET DEADLOCK_PRIORITY LOW on batch jobs makes them the preferred victim.
```

---

## ⚠️ Common Mistake

```sql
-- ❌ Wrong: retrying inside the open transaction. After 1205 the transaction is already rolled back,
--    so continuing in the same BEGIN TRAN block runs partial work outside any transaction.
-- ❌ Wrong: retrying non-idempotent side effects (sending email, calling payment API) inside the unit.
-- ❌ Wrong: unlimited retries with no delay (retry storm).
-- ❌ Wrong: catching all errors as retryable; constraint violations (547, 2627) will never succeed on retry.
```

---

## 🎯 Interview Tip (1 line)
Say: "Retries are a safety net, not the fix. I retry 1205 a few times with jittered backoff at the outermost transaction boundary, make the unit idempotent, then use the deadlock graph to fix lock ordering or missing indexes so deadlocks become rare."

---

## 🔗 Related Questions
→ Q123 (Blocking vs deadlock) | Q124 (Deadlock prevention patterns) | Q116 (Deadlock graphs and index fixes) | Q177 (What is a deadlock)
