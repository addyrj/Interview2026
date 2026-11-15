---

# Q073. TRY...CATCH Inside Procedures (ERROR_NUMBER, ERROR_MESSAGE, THROW)
# Category: Stored Procedures
# Difficulty: ⭐⭐ Medium
# DB: SQL Server (MySQL: DECLARE HANDLER; PostgreSQL: EXCEPTION WHEN ... in PL/pgSQL)

---

## ❓ Question
Write a procedure `dbo.usp_AddPayment` that inserts a payment, logs any failure into an `ErrorLog` table (number, severity, message, procedure, line) and then re-raises the error to the caller. What is the difference between `THROW` and `RAISERROR`, and what errors can TRY...CATCH NOT catch?

---

## 💡 Quick Concept (2 lines only)
Errors inside `BEGIN TRY` jump to `BEGIN CATCH`, where `ERROR_NUMBER()`, `ERROR_MESSAGE()`, `ERROR_SEVERITY()`, `ERROR_LINE()`, `ERROR_PROCEDURE()` are available. A bare `THROW;` re-raises the original error unchanged (2012+); `RAISERROR` builds a new message and does not preserve the original number.
हिंदी: Error आने पर CATCH block चलता है, `ERROR_*()` functions से details मिलती हैं। `THROW;` original error वापस भेजता है।

---

## ✅ Answer / Solution

```sql
-- ============================================
-- SETUP
-- ============================================

CREATE TABLE dbo.Payments (
  PaymentId  INT IDENTITY(1,1) PRIMARY KEY,
  OrderId    INT           NOT NULL,
  Amount     DECIMAL(10,2) NOT NULL CONSTRAINT CK_Payments_Amount CHECK (Amount > 0),
  PaidAt     DATETIME2(0)  NOT NULL CONSTRAINT DF_Payments_PaidAt DEFAULT SYSUTCDATETIME()
);
GO

CREATE TABLE dbo.ErrorLog (
  ErrorLogId   INT IDENTITY(1,1) PRIMARY KEY,
  ErrorTime    DATETIME2(0)  NOT NULL DEFAULT SYSUTCDATETIME(),
  ErrorNumber  INT           NULL,
  Severity     INT           NULL,
  ErrorState   INT           NULL,
  ProcName     NVARCHAR(128) NULL,
  ErrorLine    INT           NULL,
  ErrorMessage NVARCHAR(4000) NULL
);
GO

-- ============================================
-- SOLUTION
-- ============================================

CREATE OR ALTER PROCEDURE dbo.usp_AddPayment
    @OrderId INT,
    @Amount  DECIMAL(10,2)
AS
BEGIN
    SET NOCOUNT ON;
    SET XACT_ABORT ON;

    BEGIN TRY
        BEGIN TRANSACTION;
            INSERT INTO dbo.Payments (OrderId, Amount) VALUES (@OrderId, @Amount);
        COMMIT TRANSACTION;
    END TRY
    BEGIN CATCH
        IF XACT_STATE() <> 0 ROLLBACK TRANSACTION;   -- roll back FIRST, otherwise the log insert is rolled back too

        INSERT INTO dbo.ErrorLog (ErrorNumber, Severity, ErrorState, ProcName, ErrorLine, ErrorMessage)
        VALUES (ERROR_NUMBER(), ERROR_SEVERITY(), ERROR_STATE(), ERROR_PROCEDURE(), ERROR_LINE(), ERROR_MESSAGE());

        THROW;   -- re-raise the ORIGINAL error (must be the statement right after a previous one ending with ;)
    END CATCH;
END;
GO

EXEC dbo.usp_AddPayment @OrderId = 1, @Amount = 250.00;   -- succeeds, 1 row in Payments
EXEC dbo.usp_AddPayment @OrderId = 2, @Amount = -5.00;     -- CHECK violation -> logged, re-thrown to caller

SELECT ErrorNumber, ProcName, ErrorMessage FROM dbo.ErrorLog;
-- Expected: one row; ProcName = NULL or the procedure name depending on the error source (an error raised by the
-- INSERT inside the proc reports the proc name). ErrorNumber/message text come from SQL Server's CHECK-violation error.
-- Not executed on SQL Server; I am deliberately not quoting the exact number/text. TRY...CATCH has no equivalent
-- engine here to run.

-- Custom business error with your own number (>= 50000):
-- THROW 50001, 'Payment amount must be positive.', 1;
```

---

## 🔍 Why This Works (3 lines max)
CATCH captures the error context before any other statement resets it, so the log row has the true number/line/procedure. Rolling back before logging keeps the log row, and `THROW;` preserves the original error number and state so the Node.js caller sees the real failure.
हिंदी: पहले rollback, फिर log, फिर `THROW;` — ताकि log बचे और caller को असली error मिले।

---

## ⚡ Alternative Solution

```sql
-- Old style (pre-2012 / when you want a formatted message): RAISERROR
BEGIN TRY
    EXEC dbo.usp_AddPayment 2, -5.00;
END TRY
BEGIN CATCH
    DECLARE @msg NVARCHAR(2048) = FORMATMESSAGE(N'usp_AddPayment failed: %s (error %d)', ERROR_MESSAGE(), ERROR_NUMBER());
    RAISERROR(@msg, 16, 1);    -- NEW error 50000; original number is lost
END CATCH;

-- THROW vs RAISERROR: THROW respects XACT_ABORT, terminates the batch, severity always 16, number must be >= 50000
-- when you give it explicitly. RAISERROR can use severity < 11 (informational) and supports printf-style formatting.
```

---

## ⚠️ Common Mistake

```sql
-- ❌ Swallowing the error: CATCH with only a log insert and no THROW -> caller thinks it succeeded.
-- ❌ Logging inside the open (doomed) transaction: XACT_STATE() = -1 forbids writes; the insert fails or is rolled back.
-- ❌ Assuming TRY...CATCH catches everything. It does NOT catch: compile errors / object-name resolution errors in the
--    same scope (deferred name resolution aside), severity >= 20 that drops the connection, and attention (client
--    timeout/cancel) events. Per Microsoft docs.
-- ❌ ERROR_NUMBER() used outside the CATCH block -> returns NULL.
```

---

## 🎯 Interview Tip (1 line)
Say: "In CATCH I roll back first, log via ERROR_* functions, then `THROW;` so the original error reaches the app — and I never swallow errors silently. I also know TRY...CATCH does not catch severity 20+ or client cancellations, so the Node.js side still needs its own timeout/retry handling."

---

## 🔗 Related Questions
→ Q072 (Procedures with transactions) | Q020 (@@ROWCOUNT, @@ERROR) | Q075 (Calling from Node.js)
