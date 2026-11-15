---

# Q124. Deadlock Prevention Patterns
# Category: Transactions + Locking
# Difficulty: ⭐⭐⭐ Hard
# DB: SQL Server (same ideas apply to MySQL InnoDB and PostgreSQL)

---

## ❓ Question
Two transfers run at the same time: A to B and B to A. They deadlock. Show the cause and the prevention patterns: consistent ordering, short transactions, indexes, UPDLOCK, RCSI and retry.

---

## 💡 Quick Concept (2 lines only)
A deadlock needs a cycle: T1 holds X on row A and wants B, T2 holds B and wants A. Break the cycle by always touching resources in the same order, holding locks for less time, and locking fewer rows.
हिंदी: Deadlock = चक्र (T1 के पास A, B चाहिए; T2 के पास B, A चाहिए)। हमेशा एक ही order में lock लो, transaction छोटा रखो, कम rows lock करो।

---

## ✅ Answer / Solution

NOTE: the deadlock itself is not executed (needs two sessions on SQL Server); the final balances below are hand-checked arithmetic (1000-300+100, 500+300-100), not an engine result.

```sql
-- ============================================
-- SETUP
-- ============================================

CREATE TABLE dbo.Accounts (
    AccountId INT           NOT NULL PRIMARY KEY,
    Owner     VARCHAR(50)   NOT NULL,
    Balance   DECIMAL(12,2) NOT NULL CHECK (Balance >= 0)
);
INSERT INTO dbo.Accounts (AccountId, Owner, Balance) VALUES (1, 'Asha', 1000), (2, 'Ravi', 500);
GO

-- ============================================
-- THE DEADLOCK (opposite order)
-- ============================================
-- T1: UPDATE ... WHERE AccountId = 1   (X on 1)      T2: UPDATE ... WHERE AccountId = 2   (X on 2)
-- T1: UPDATE ... WHERE AccountId = 2   (waits for T2)  T2: UPDATE ... WHERE AccountId = 1   (waits for T1)
-- -> cycle; SQL Server picks a victim (error 1205).

-- ============================================
-- PATTERN 1: consistent lock order - always lock the lower AccountId first
-- ============================================

CREATE PROCEDURE dbo.TransferMoney
    @FromId INT, @ToId INT, @Amount DECIMAL(12,2)
AS
BEGIN
    SET NOCOUNT ON;
    SET XACT_ABORT ON;

    DECLARE @First INT  = CASE WHEN @FromId < @ToId THEN @FromId ELSE @ToId END;
    DECLARE @Second INT = CASE WHEN @FromId < @ToId THEN @ToId   ELSE @FromId END;

    BEGIN TRANSACTION;
        -- Touch rows in ascending id order regardless of transfer direction
        SELECT AccountId FROM dbo.Accounts WITH (UPDLOCK, ROWLOCK) WHERE AccountId = @First;
        SELECT AccountId FROM dbo.Accounts WITH (UPDLOCK, ROWLOCK) WHERE AccountId = @Second;

        UPDATE dbo.Accounts SET Balance = Balance - @Amount WHERE AccountId = @FromId;
        UPDATE dbo.Accounts SET Balance = Balance + @Amount WHERE AccountId = @ToId;
    COMMIT TRANSACTION;
END;
GO

EXEC dbo.TransferMoney @FromId = 1, @ToId = 2, @Amount = 300;
EXEC dbo.TransferMoney @FromId = 2, @ToId = 1, @Amount = 100;   -- same lock order, no cycle
GO

SELECT AccountId, Balance FROM dbo.Accounts ORDER BY AccountId;
-- Hand-checked; not executed on SQL Server:
-- AccountId | Balance
-- 1         | 800
-- 2         | 700

-- ============================================
-- PATTERN 2-5 (summary)
-- ============================================
-- 2. Keep transactions short: no user input, no HTTP calls, no big loops inside BEGIN TRAN
-- 3. Index the predicates (Q116): fewer rows scanned = fewer locks
-- 4. UPDLOCK on read-then-update to avoid S->X conversion deadlocks (Q122)
-- 5. RCSI for reader/writer deadlocks (Q120); retry on 1205 as safety net (Q130)
-- Optional: SET DEADLOCK_PRIORITY LOW; for background jobs so they become the victim, not the user request.
```

---

## 🔍 Why This Works (3 lines max)
With a global ordering rule a cycle cannot form: whoever gets the lower id first makes the other wait, and the waiter holds nothing the first needs. UPDLOCK makes the "reserve" step explicit. Shorter transactions reduce the window in which a conflict can occur at all.
हिंदी: Global order हो तो चक्र बन ही नहीं सकता। UPDLOCK से पहले ही row reserve हो जाती है। छोटा transaction = conflict का समय कम।

---

## ⚡ Alternative Solution

```sql
-- Single-statement transfer using one UPDATE with CASE - one statement locks both rows together
-- (rows still lock in plan order, so keep the ordering pattern if the plan can vary)
UPDATE dbo.Accounts
SET Balance = Balance + CASE AccountId WHEN @FromId THEN -@Amount ELSE @Amount END
WHERE AccountId IN (@FromId, @ToId);

-- Node.js: wrap the EXEC in a retry for error number 1205 (Q130):
-- if (err.number === 1205 && attempt < 3) return retry();
```

---

## ⚠️ Common Mistake

```sql
-- ❌ Wrong: ordering by the transfer direction (from first, then to)
-- ❌ Wrong: NOLOCK as a "deadlock fix" - hides the problem and returns dirty data (Q125)
-- ❌ Wrong: relying on retry only, with long transactions: every retry repeats the heavy work
-- ❌ Wrong: different procedures touching the same tables in different orders (Orders then Stock vs
--    Stock then Orders) - document one table access order for the whole codebase
```

---

## 🎯 Interview Tip (1 line)
Say: "My prevention checklist: same access order everywhere, short transactions, proper indexes, UPDLOCK for read-then-write, RCSI to remove reader/writer cycles, and a bounded retry for 1205 in the data-access layer. I verify with the deadlock graph that it actually stopped."

---

## 🔗 Related Questions
→ Q116 (deadlock graphs and index fixes) | Q122 (locks) | Q130 (retry logic for deadlock victims) | Q189 (procedure to transfer money safely)
