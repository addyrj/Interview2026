---

# Q085. Soft Delete and Audit Logging Procedure
# Category: Stored Procedures
# Difficulty: ⭐⭐ Medium
# DB: SQL Server (MySQL/PostgreSQL: no CREATE PROCEDURE ... OUTPUT clause; PostgreSQL has RETURNING, MySQL needs a separate INSERT)

---

## ❓ Question
Customers must never be physically deleted. Write `usp_SoftDeleteCustomer` that marks a customer as deleted (IsDeleted, DeletedAt, DeletedBy), writes a row to AuditLog, and does both atomically. Re-deleting an already deleted customer must not create a second audit row. Also: a deleted customer's email must be reusable by a new customer.

---

## 💡 Quick Concept (2 lines only)
Soft delete = UPDATE a flag instead of DELETE; wrap the flag update and the audit INSERT in one transaction (SET XACT_ABORT ON + TRY...CATCH). A filtered unique index (WHERE IsDeleted = 0) keeps email unique only among live rows.
हिंदी: Soft delete = row हटाओ मत, flag लगाओ। Update + audit एक transaction में। Filtered unique index से deleted email दोबारा use हो सकता है।

---

## ✅ Answer / Solution

```sql
-- ============================================
-- SETUP
-- ============================================

CREATE TABLE dbo.Customers (
  CustomerId INT IDENTITY(1,1) PRIMARY KEY,
  Name       NVARCHAR(100) NOT NULL,
  Email      NVARCHAR(200) NOT NULL,
  IsDeleted  BIT NOT NULL DEFAULT 0,
  DeletedAt  DATETIME2(0) NULL,
  DeletedBy  NVARCHAR(100) NULL
);

-- Unique email only among NON-deleted rows (filtered index, SQL Server 2008+)
CREATE UNIQUE INDEX UX_Customers_Email_Live
  ON dbo.Customers (Email) WHERE IsDeleted = 0;

CREATE TABLE dbo.AuditLog (
  AuditId   INT IDENTITY(1,1) PRIMARY KEY,
  TableName SYSNAME NOT NULL,
  RecordId  INT NOT NULL,
  Action    VARCHAR(20) NOT NULL,
  ChangedBy NVARCHAR(100) NOT NULL,
  ChangedAt DATETIME2(0) NOT NULL DEFAULT SYSUTCDATETIME()
);

INSERT INTO dbo.Customers (Name, Email) VALUES
  (N'Asha Rao',     N'asha@example.com'),
  (N'Vikram Shah',  N'vikram@example.com'),
  (N'Meera Iyer',   N'meera@example.com');
GO

-- ============================================
-- SOLUTION
-- ============================================

CREATE OR ALTER PROCEDURE dbo.usp_SoftDeleteCustomer   -- CREATE OR ALTER: SQL Server 2016 SP1+
  @CustomerId INT,
  @DeletedBy  NVARCHAR(100)
AS
BEGIN
  SET NOCOUNT ON;
  SET XACT_ABORT ON;

  BEGIN TRY
    BEGIN TRANSACTION;

    UPDATE dbo.Customers
    SET IsDeleted = 1, DeletedAt = SYSUTCDATETIME(), DeletedBy = @DeletedBy
    WHERE CustomerId = @CustomerId AND IsDeleted = 0;   -- guard = idempotent

    IF @@ROWCOUNT = 1                                    -- audit only if something changed
      INSERT INTO dbo.AuditLog (TableName, RecordId, Action, ChangedBy)
      VALUES ('Customers', @CustomerId, 'SOFT_DELETE', @DeletedBy);

    COMMIT TRANSACTION;
  END TRY
  BEGIN CATCH
    IF @@TRANCOUNT > 0 ROLLBACK TRANSACTION;
    THROW;                                               -- re-raise original error
  END CATCH
END;
GO

EXEC dbo.usp_SoftDeleteCustomer @CustomerId = 2, @DeletedBy = N'admin';
EXEC dbo.usp_SoftDeleteCustomer @CustomerId = 2, @DeletedBy = N'admin';  -- no-op, no 2nd audit row

-- Email of customer 2 is free again:
INSERT INTO dbo.Customers (Name, Email) VALUES (N'Vikram S', N'vikram@example.com');

SELECT CustomerId, Name, Email FROM dbo.Customers WHERE IsDeleted = 0 ORDER BY CustomerId;
SELECT AuditId, TableName, RecordId, Action, ChangedBy FROM dbo.AuditLog;

-- EXPECTED OUTPUT (result derived from equivalent statements on SQLite (partial unique index
-- + UPDATE + INSERT); the procedure itself is not executed on SQL Server):
-- CustomerId | Name      | Email
-- 1          | Asha Rao  | asha@example.com
-- 3          | Meera Iyer| meera@example.com
-- 4          | Vikram S  | vikram@example.com
--
-- AuditId | TableName | RecordId | Action      | ChangedBy
-- 1       | Customers | 2        | SOFT_DELETE | admin
```

Node.js (`mssql`):

```javascript
const result = await pool.request()
  .input('CustomerId', sql.Int, 2)
  .input('DeletedBy', sql.NVarChar(100), req.user.email)
  .execute('dbo.usp_SoftDeleteCustomer');
```

---

## 🔍 Why This Works (3 lines + Hindi 1 line)
The `AND IsDeleted = 0` guard makes the proc idempotent, and `@@ROWCOUNT = 1` (read immediately after the UPDATE) means audit rows appear only for real changes. XACT_ABORT ON plus TRY...CATCH guarantees update and audit commit or roll back together. The filtered unique index enforces uniqueness only on live rows.
हिंदी: Guard (`IsDeleted = 0`) से दोबारा delete safe। `@@ROWCOUNT` UPDATE के तुरंत बाद पढ़ो। Dono statements एक साथ commit या rollback।

---

## ⚡ Alternative Solution

```sql
-- OUTPUT clause: write the audit row from the same UPDATE statement (no @@ROWCOUNT check needed)
UPDATE dbo.Customers
SET IsDeleted = 1, DeletedAt = SYSUTCDATETIME(), DeletedBy = @DeletedBy
OUTPUT 'Customers', inserted.CustomerId, 'SOFT_DELETE', @DeletedBy, SYSUTCDATETIME()
INTO dbo.AuditLog (TableName, RecordId, Action, ChangedBy, ChangedAt)
WHERE CustomerId = @CustomerId AND IsDeleted = 0;
-- Atomic in one statement. Not executed on SQL Server; behaviour per Microsoft docs.
-- (OUTPUT INTO target must not have enabled triggers or be on either side of a foreign key.)
```

---

## ⚠️ Common Mistake

```sql
-- ❌ Wrong: forgetting the IsDeleted filter in every query -> deleted rows leak into the app
SELECT * FROM dbo.Customers WHERE Email = N'vikram@example.com';

-- ❌ Wrong: plain UNIQUE (Email) -> re-registering a deleted user's email fails.
-- ❌ Wrong: reading @@ROWCOUNT after another statement -> it is overwritten by every statement.
-- ✅ Hide the flag behind a view (vCustomersLive) or Row-Level Security predicate,
--    use the filtered unique index, read @@ROWCOUNT immediately.
```

---

## 🎯 Interview Tip (1 line)
Say: "I make soft delete idempotent with a guard in the WHERE, audit in the same transaction, a filtered unique index so keys are reusable, and I mention the trade-offs: every query needs the flag, so I expose a live-rows view, and for compliance (GDPR erase) soft delete is not enough — I need a purge job. Temporal tables are the alternative when the real need is history."

---

## 🔗 Related Questions
→ Q072 (Procedures with transactions) | Q073 (TRY...CATCH) | Q097 (Audit trigger pattern) | Q105 (Filtered indexes) | Q030 (Temporal tables)
