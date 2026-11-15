
---

# Q132. TRY...CATCH Complete Guide
# Category: ERROR HANDLING + SECURITY
# Difficulty: ⭐⭐⭐ Hard
# DB: SQL Server (MySQL uses DECLARE HANDLER; PostgreSQL uses EXCEPTION blocks in PL/pgSQL)

---

## ❓ Question
Explain exactly what TRY...CATCH catches in T-SQL and what it does not. Write a procedure that inserts a payment, uses all the ERROR_* functions, handles `XACT_STATE()` correctly and re-raises the error to the caller.

---

## 💡 Quick Concept (2 lines only)
A CATCH block runs for runtime errors with severity 11-19 (and 20+ that do not kill the connection) raised inside the TRY. Inside CATCH use ERROR_NUMBER/SEVERITY/STATE/PROCEDURE/LINE/MESSAGE, check XACT_STATE(), and `THROW;` to re-raise.
हिंदी: TRY...CATCH severity 11-19 के runtime errors पकड़ता है। CATCH में ERROR_* functions और XACT_STATE() देखो, और आख़िर में THROW; से error आगे भेजो।

---

## ✅ Answer / Solution

```sql
-- ============================================
-- SETUP
-- ============================================
CREATE TABLE dbo.Payments (
  PaymentId INT IDENTITY(1,1) PRIMARY KEY,
  OrderId   INT NOT NULL,
  Amount    DECIMAL(10,2) NOT NULL CHECK (Amount > 0),
  Method    VARCHAR(20) NOT NULL,
  CONSTRAINT UQ_Payments_Order UNIQUE (OrderId)
);
GO

-- ============================================
-- SOLUTION
-- ============================================
CREATE OR ALTER PROCEDURE dbo.usp_AddPayment
  @OrderId INT, @Amount DECIMAL(10,2), @Method VARCHAR(20)
AS
BEGIN
  SET NOCOUNT ON;
  SET XACT_ABORT ON;     -- makes most errors doom the tran; XACT_STATE() then returns -1
  BEGIN TRY
    BEGIN TRAN;
      INSERT INTO dbo.Payments (OrderId, Amount, Method) VALUES (@OrderId, @Amount, @Method);
    COMMIT;
  END TRY
  BEGIN CATCH
    IF XACT_STATE() <> 0 ROLLBACK;       -- 1 = committable, -1 = uncommittable; both must end here

    SELECT ERROR_NUMBER()    AS ErrNo,
           ERROR_SEVERITY()  AS Severity,
           ERROR_STATE()     AS State,
           ERROR_PROCEDURE() AS ProcName,
           ERROR_LINE()      AS LineNo,
           ERROR_MESSAGE()   AS Msg;

    THROW;                               -- re-raise original error (SQL Server 2012+)
  END CATCH
END;
GO

EXEC dbo.usp_AddPayment 1001, 250.00, 'CARD';   -- ok
EXEC dbo.usp_AddPayment 1001, 250.00, 'CARD';   -- duplicate OrderId -> unique violation
EXEC dbo.usp_AddPayment 1002, -5.00,  'CARD';   -- CHECK violation
```

```sql
-- EXPECTED OUTPUT
-- Not executed on SQL Server; behaviour per Microsoft docs. Unique key violation is error 2627 and
-- CHECK violation is error 547 (both documented, severity 14 and 16 respectively).
-- 2nd call -> ErrNo 2627, ProcName usp_AddPayment, Msg "Violation of UNIQUE KEY constraint 'UQ_Payments_Order'..."
-- 3rd call -> ErrNo 547,  Msg "The INSERT statement conflicted with the CHECK constraint ..."
-- Message text is abbreviated; LineNo/State depend on the server.
-- Constraint logic cross-checked on SQLite: the duplicate and the negative amount are both rejected.
```

**What TRY...CATCH does NOT catch**
- Severity 20+ that terminate the connection; severity 10 or lower (informational)
- Compile errors and name-resolution errors in the SAME batch/scope (e.g. missing table in the same procedure body at first compile; use dynamic SQL or an outer TRY to catch)
- Attentions (client disconnect / timeout)
- Errors in a nested scope where the transaction is already doomed: you may only ROLLBACK

---

## 🔍 Why This Works (3 lines max)
CATCH transfers control on error, ERROR_* functions are only valid there, and XACT_STATE() tells whether COMMIT is still allowed. THROW without arguments rethrows the original number, message and line so callers and the Node driver see the real error.
हिंदी: CATCH में control आता है, ERROR_* सिर्फ़ वहीं काम करते हैं। XACT_STATE() बताता है कि commit हो सकता है या नहीं; THROW; असली error आगे पहुँचाता है।

---

## ⚡ Alternative Solution

```sql
-- Nested TRY to catch errors from deferred name resolution / child scope, and cleanup pattern with TRY...CATCH + a flag
DECLARE @ok BIT = 1;
BEGIN TRY
  EXEC (N'SELECT * FROM dbo.TableThatDoesNotExist');   -- error is raised in child batch -> caught
END TRY
BEGIN CATCH
  SET @ok = 0;
  PRINT CONCAT('Failed: ', ERROR_NUMBER(), ' ', ERROR_MESSAGE());
END CATCH;
```

---

## ⚠️ Common Mistake

```sql
-- ❌ Wrong: swallowing errors (empty CATCH) -> caller thinks it succeeded
BEGIN CATCH
END CATCH;

-- ❌ Wrong: COMMIT inside CATCH without checking XACT_STATE() (error 3930 when state = -1)
-- ❌ Wrong: calling ERROR_MESSAGE() after other statements that reset it, or outside CATCH (returns NULL)
-- ❌ Wrong: RAISERROR(ERROR_MESSAGE(), 16, 1) to rethrow: loses the original error number (becomes 50000)
-- ❌ Wrong: assuming @@ERROR works like a CATCH; it is reset by the very next statement.
```

---

## 🎯 Interview Tip (1 line)
Say: "My standard template is SET XACT_ABORT ON, BEGIN TRY / BEGIN TRAN, and in CATCH: rollback if XACT_STATE() <> 0, log the ERROR_* values, then THROW. The Node layer then receives the original error number and can map 2627 to 409 and 547 to 400."

---

## 🔗 Related Questions
→ Q073 (TRY...CATCH inside procedures) | Q118 (XACT_ABORT) | Q133 (THROW vs RAISERROR) | Q134 (Error logging table pattern)
