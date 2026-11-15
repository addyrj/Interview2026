
---

# Q134. Error Logging Table Pattern
# Category: ERROR HANDLING + SECURITY
# Difficulty: ⭐⭐⭐ Hard
# DB: SQL Server (MySQL/PostgreSQL: same table idea, different error functions)

---

## ❓ Question
Build a central `ErrorLog` table and a logging procedure that every CATCH block can call. The log row must survive the rollback of the failed business transaction. Show usage in a procedure.

---

## 💡 Quick Concept (2 lines only)
Create a table plus `usp_LogError` that captures ERROR_* values, user, and parameters. Call it AFTER ROLLBACK, otherwise the log insert is rolled back with the transaction (a table variable is the classic trick when you must log inside it).
हिंदी: ErrorLog table + एक logging procedure बनाओ। इसे ROLLBACK के बाद call करो, वरना log भी rollback के साथ गायब हो जाएगा।

---

## ✅ Answer / Solution

```sql
-- ============================================
-- SETUP
-- ============================================
CREATE TABLE dbo.ErrorLog (
  ErrorLogId  INT IDENTITY(1,1) PRIMARY KEY,
  LoggedAtUtc DATETIME2(3)   NOT NULL DEFAULT SYSUTCDATETIME(),
  DbUser      SYSNAME        NOT NULL DEFAULT SUSER_SNAME(),
  ProcName    NVARCHAR(128)  NULL,
  ErrNo       INT            NULL,
  Severity    INT            NULL,
  ErrState    INT            NULL,
  ErrLine     INT            NULL,
  Msg         NVARCHAR(4000) NULL,
  Context     NVARCHAR(4000) NULL            -- e.g. JSON of input params
);
GO

CREATE OR ALTER PROCEDURE dbo.usp_LogError @Context NVARCHAR(4000) = NULL
AS
BEGIN
  SET NOCOUNT ON;
  IF ERROR_NUMBER() IS NULL RETURN;          -- not called from CATCH
  INSERT INTO dbo.ErrorLog (ProcName, ErrNo, Severity, ErrState, ErrLine, Msg, Context)
  VALUES (ERROR_PROCEDURE(), ERROR_NUMBER(), ERROR_SEVERITY(), ERROR_STATE(),
          ERROR_LINE(), ERROR_MESSAGE(), @Context);
END;
GO
-- ERROR_* functions work inside a procedure called from CATCH, so no params are needed for them.

-- ============================================
-- SOLUTION: usage
-- ============================================
CREATE OR ALTER PROCEDURE dbo.usp_PlaceOrder @CustomerId INT, @Total DECIMAL(10,2)
AS
BEGIN
  SET NOCOUNT ON; SET XACT_ABORT ON;
  BEGIN TRY
    BEGIN TRAN;
      INSERT INTO dbo.Orders (CustomerId, Total) VALUES (@CustomerId, @Total);
    COMMIT;
  END TRY
  BEGIN CATCH
    IF XACT_STATE() <> 0 ROLLBACK;                       -- 1) roll back first
    DECLARE @ctx NVARCHAR(4000) =
      CONCAT('{"customerId":', @CustomerId, ',"total":', @Total, '}');
    EXEC dbo.usp_LogError @Context = @ctx;               -- 2) log after, so the row persists
    THROW;                                               -- 3) tell the caller
  END CATCH
END;
GO

SELECT ErrorLogId, ProcName, ErrNo, Msg, Context FROM dbo.ErrorLog;
```

```sql
-- EXPECTED OUTPUT
-- Insert/select logic run on SQLite; ERROR_* values and SUSER_SNAME() cannot be produced there,
-- so the row below uses a hand-supplied example (ErrNo 547). Not executed on SQL Server.
-- ErrorLogId | ProcName       | ErrNo | Msg          | Context
-- 1          | usp_PlaceOrder | 547   | FK conflict  | {"customerId":10,"total":100.00}
-- (Real Msg is the full constraint-conflict text from SQL Server.)
```

---

## 🔍 Why This Works (3 lines max)
Logging after the ROLLBACK means the INSERT into ErrorLog runs outside the failed transaction, so it commits (autocommit) and persists. Capturing procedure, line and input context lets you reproduce failures without guessing.
हिंदी: ROLLBACK के बाद log करने से INSERT अलग से commit होता है और बचा रहता है। Procedure, line और input सब मिलने से bug दोबारा चलाना आसान होता है।

---

## ⚡ Alternative Solution

```sql
-- Log from the application (Node) instead: winston/pino -> Application Insights / Azure Monitor.
-- Keeps DB writes off the failure path and survives a full DB outage. Best used alongside, not instead:
--   DB log   = what the DB saw (number, line, proc)
--   App log  = request id, user, payload, trace id
-- If you must log inside an open transaction use a table variable:
DECLARE @e TABLE (ErrNo INT, Msg NVARCHAR(4000));
-- INSERT @e in CATCH BEFORE ROLLBACK; after ROLLBACK, copy @e rows into dbo.ErrorLog (table variables ignore rollback).
```

---

## ⚠️ Common Mistake

```sql
-- ❌ Wrong: logging BEFORE the ROLLBACK -> the log row disappears with the transaction
BEGIN CATCH
  EXEC dbo.usp_LogError;
  ROLLBACK;
END CATCH;

-- ❌ Wrong: logging while XACT_STATE() = -1 (uncommittable): writes are not allowed until rollback.
-- ❌ Wrong: no retention policy; the table grows forever. Purge or partition by LoggedAtUtc.
-- ❌ Wrong: logging passwords/PII into Context.
-- ❌ Wrong: the logger itself failing and masking the original error: keep it tiny, wrap in its own TRY.
```

---

## 🎯 Interview Tip (1 line)
Say: "Rollback first, log second, rethrow third. I add a correlation id from the Node request into Context, index LoggedAtUtc, keep 30-90 days, and alert on spikes. DB-side logging is a complement to application telemetry, not a replacement."

---

## 🔗 Related Questions
→ Q132 (TRY...CATCH guide) | Q133 (THROW vs RAISERROR) | Q085 (Soft delete and audit logging) | Q097 (Audit trigger pattern)
