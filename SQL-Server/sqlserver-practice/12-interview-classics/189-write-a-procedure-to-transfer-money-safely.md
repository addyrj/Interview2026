---

# Q189. Write a Procedure to Transfer Money Safely
# Category: Interview Classics
# Difficulty: ⭐⭐⭐ Hard
# DB: SQL Server (MySQL: START TRANSACTION + SELECT ... FOR UPDATE; PostgreSQL: same FOR UPDATE; SQL Server uses UPDLOCK/ROWLOCK hints)

---

## ❓ Question
Write usp_TransferFunds(@FromAccountId, @ToAccountId, @Amount) that moves money between accounts. It must be atomic, never overdraw, avoid deadlocks when two transfers run in opposite directions, write a ledger row, and surface errors to the caller (and to Node.js).

---

## 💡 Quick Concept (2 lines only)
Use SET XACT_ABORT ON + BEGIN TRY/CATCH + one transaction; lock both rows with UPDLOCK in a fixed order (lowest id first); check balance after locking, then update both and insert the ledger row. THROW in CATCH after ROLLBACK.
हिंदी: XACT_ABORT ON + TRY/CATCH + एक transaction। दोनों rows UPDLOCK से हमेशा छोटे id पहले lock करो ताकि deadlock न हो। Balance lock के बाद check करो, फिर update।

---

## ✅ Answer / Solution

```sql
-- ============================================
-- SETUP
-- ============================================
CREATE TABLE Accounts (
    AccountId INT PRIMARY KEY,
    Holder    NVARCHAR(100) NOT NULL,
    Balance   DECIMAL(12,2) NOT NULL CONSTRAINT CK_Accounts_Balance CHECK (Balance >= 0)
);

CREATE TABLE TransferLedger (
    TransferId    BIGINT IDENTITY(1,1) PRIMARY KEY,
    FromAccountId INT NOT NULL REFERENCES Accounts(AccountId),
    ToAccountId   INT NOT NULL REFERENCES Accounts(AccountId),
    Amount        DECIMAL(12,2) NOT NULL CHECK (Amount > 0),
    CreatedAt     DATETIME2 NOT NULL DEFAULT SYSUTCDATETIME()
);

INSERT INTO Accounts VALUES (1, N'Asha Rao', 1000.00), (2, N'Vikram Sen', 500.00);
GO

-- ============================================
-- PROCEDURE
-- ============================================
CREATE OR ALTER PROCEDURE dbo.usp_TransferFunds     -- CREATE OR ALTER: SQL Server 2016 SP1+
    @FromAccountId INT,
    @ToAccountId   INT,
    @Amount        DECIMAL(12,2)
AS
BEGIN
    SET NOCOUNT ON;
    SET XACT_ABORT ON;                 -- any runtime error dooms + rolls back the transaction

    IF @Amount IS NULL OR @Amount <= 0 THROW 50001, 'Amount must be positive.', 1;
    IF @FromAccountId = @ToAccountId   THROW 50002, 'Cannot transfer to the same account.', 1;

    BEGIN TRY
        BEGIN TRAN;

        -- Lock BOTH rows in a fixed order (lowest id first) -> opposite transfers cannot deadlock
        DECLARE @First INT  = CASE WHEN @FromAccountId < @ToAccountId THEN @FromAccountId ELSE @ToAccountId END;
        DECLARE @Second INT = CASE WHEN @FromAccountId < @ToAccountId THEN @ToAccountId ELSE @FromAccountId END;
        DECLARE @Locked INT;

        SELECT @Locked = AccountId FROM Accounts WITH (UPDLOCK, ROWLOCK) WHERE AccountId = @First;
        IF @@ROWCOUNT = 0 THROW 50003, 'Account not found.', 1;
        SELECT @Locked = AccountId FROM Accounts WITH (UPDLOCK, ROWLOCK) WHERE AccountId = @Second;
        IF @@ROWCOUNT = 0 THROW 50003, 'Account not found.', 1;

        -- Check balance AFTER locking (otherwise another session can spend it in between)
        DECLARE @Balance DECIMAL(12,2);
        SELECT @Balance = Balance FROM Accounts WHERE AccountId = @FromAccountId;
        IF @Balance < @Amount
            THROW 50004, 'Insufficient funds.', 1;

        UPDATE Accounts SET Balance = Balance - @Amount WHERE AccountId = @FromAccountId;
        UPDATE Accounts SET Balance = Balance + @Amount WHERE AccountId = @ToAccountId;

        INSERT INTO TransferLedger (FromAccountId, ToAccountId, Amount)
        VALUES (@FromAccountId, @ToAccountId, @Amount);

        COMMIT;
    END TRY
    BEGIN CATCH
        IF @@TRANCOUNT > 0 ROLLBACK;
        THROW;                         -- re-raise original error to the caller
    END CATCH
END;
GO

-- ============================================
-- EXEC EXAMPLES
-- ============================================
EXEC dbo.usp_TransferFunds @FromAccountId = 1, @ToAccountId = 2, @Amount = 250.00;
SELECT AccountId, Balance FROM Accounts ORDER BY AccountId;

-- Expected (hand-checked arithmetic; NOT executed on SQL Server - behaviour per Microsoft docs):
-- AccountId | Balance
-- 1         | 750.00
-- 2         | 750.00
-- and one TransferLedger row (1 -> 2, 250.00). Total money stays 1500.00.

EXEC dbo.usp_TransferFunds 1, 2, 9999.00;
-- Raises our custom error 50004 'Insufficient funds.'; balances unchanged (rolled back).
```

```js
// Node.js (mssql): proc errors arrive as exceptions
const result = await pool.request()
  .input('FromAccountId', sql.Int, 1)
  .input('ToAccountId',   sql.Int, 2)
  .input('Amount',        sql.Decimal(12, 2), 250.00)
  .execute('dbo.usp_TransferFunds');
// catch (err) { err.number === 50004 -> 409 "Insufficient funds" ; deadlock victim -> retry }
```

---

## 🔍 Why This Works (3 lines max)
One transaction makes debit, credit and ledger all-or-nothing; XACT_ABORT guarantees rollback even on errors TRY/CATCH might miss. UPDLOCK on both rows (consistently ordered) stops two sessions from reading the same balance, and the CHECK constraint is a last line of defence against negative balances.
हिंदी: एक transaction = सब या कुछ नहीं। UPDLOCK से दो sessions एक ही balance नहीं पढ़ पाते। CHECK constraint आख़िरी सुरक्षा है।

---

## ⚡ Alternative Solution

```sql
-- Atomic conditional UPDATE: no separate balance read at all
UPDATE Accounts
SET Balance = Balance - @Amount
WHERE AccountId = @FromAccountId AND Balance >= @Amount;

IF @@ROWCOUNT = 0 THROW 50004, 'Insufficient funds or account missing.', 1;
-- Then credit the other account. Still wrap both in one transaction.
-- Lower-contention pattern; lock ordering still matters for deadlocks.
```

---

## ⚠️ Common Mistake

```sql
-- ❌ Wrong: read balance, check in app code, then update later (race: two requests both pass the check)
-- ❌ Wrong: no transaction -> debit succeeds, credit fails, money vanishes
-- ❌ Wrong: ROLLBACK in CATCH without checking @@TRANCOUNT, or swallowing the error (caller thinks it worked)
-- ❌ Wrong: always locking "from" then "to" -> transfer A->B and B->A deadlock (error 1205 victim)
-- ✅ Fixed lock order + UPDLOCK; still add retry in the app for deadlock victims (Q130)
-- ❌ Wrong: using FLOAT/MONEY for currency math -> use DECIMAL(12,2)
```

---

## 🎯 Interview Tip (1 line)
Say: "Atomic transaction, XACT_ABORT ON, lock both rows in a deterministic order, validate after locking, ledger insert in the same transaction, THROW the error back, and make the API idempotent with a client-supplied transfer key so a retry can't double-debit." The idempotency key is what separates senior answers.

---

## 🔗 Related Questions
→ Q072 (Procedures with transactions) | Q073 (TRY...CATCH in procedures) | Q118 (BEGIN TRAN, XACT_ABORT) | Q125 (Lock hints) | Q130 (Retry for deadlock victims) | Q177 (Deadlock and how to fix)
