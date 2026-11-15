---

# Q097. Audit Trigger Pattern
# Category: Functions, Views + Triggers
# Difficulty: ⭐⭐⭐ Hard
# DB: SQL Server (PostgreSQL: row-level audit triggers with to_jsonb(OLD/NEW); MySQL: three row-level triggers)

---

## ❓ Question
Audit every INSERT, UPDATE and DELETE on Employees: who changed what, when, and the old and new row as JSON. It must be correct for multi-row statements and must not log updates that changed nothing.

---

## 💡 Quick Concept (2 lines only)
One AFTER INSERT, UPDATE, DELETE trigger joins `inserted` and `deleted` on the key, derives the action, and writes old/new row images with `FOR JSON PATH` (SQL Server 2016+). Capture the caller with SUSER_SNAME() or SESSION_CONTEXT for app users.
हिंदी: एक AFTER trigger, `inserted` और `deleted` को key पर join, action तय करो, old/new row को JSON में लिखो। App user के लिए SESSION_CONTEXT use करो।

---

## ✅ Answer / Solution

```sql
-- ============================================
-- SETUP
-- ============================================

CREATE TABLE dbo.Employees (
  EmployeeId INT PRIMARY KEY,
  Name       NVARCHAR(100) NOT NULL,
  Salary     DECIMAL(10,2) NOT NULL
);

CREATE TABLE dbo.EmployeeAudit (
  AuditId    BIGINT IDENTITY(1,1) PRIMARY KEY,
  EmployeeId INT NOT NULL,
  Action     VARCHAR(10) NOT NULL,
  OldValues  NVARCHAR(MAX) NULL,
  NewValues  NVARCHAR(MAX) NULL,
  ChangedBy  NVARCHAR(128) NOT NULL DEFAULT SUSER_SNAME(),
  ChangedAt  DATETIME2(3) NOT NULL DEFAULT SYSUTCDATETIME()
);
GO

-- ============================================
-- SOLUTION
-- ============================================

CREATE OR ALTER TRIGGER dbo.trg_Employees_Audit
ON dbo.Employees
AFTER INSERT, UPDATE, DELETE
AS
BEGIN
  SET NOCOUNT ON;
  IF NOT EXISTS (SELECT 1 FROM inserted) AND NOT EXISTS (SELECT 1 FROM deleted) RETURN;

  DECLARE @user NVARCHAR(128) = COALESCE(CONVERT(NVARCHAR(128), SESSION_CONTEXT(N'AppUser')), SUSER_SNAME());

  INSERT INTO dbo.EmployeeAudit (EmployeeId, Action, OldValues, NewValues, ChangedBy)
  SELECT COALESCE(i.EmployeeId, d.EmployeeId),
         CASE WHEN d.EmployeeId IS NULL THEN 'INSERT'
              WHEN i.EmployeeId IS NULL THEN 'DELETE' ELSE 'UPDATE' END,
         (SELECT d.Name, d.Salary FOR JSON PATH, WITHOUT_ARRAY_WRAPPER),
         (SELECT i.Name, i.Salary FOR JSON PATH, WITHOUT_ARRAY_WRAPPER),
         @user
  FROM inserted i
  FULL OUTER JOIN deleted d ON d.EmployeeId = i.EmployeeId
  WHERE d.EmployeeId IS NULL OR i.EmployeeId IS NULL           -- insert / delete
     OR d.Name <> i.Name OR d.Salary <> i.Salary;              -- real update only
END;
GO

EXEC sys.sp_set_session_context @key = N'AppUser', @value = N'priya@corp.com';

INSERT INTO dbo.Employees VALUES (1, N'Ravi', 50000), (2, N'Neha', 55000);
UPDATE dbo.Employees SET Salary = Salary + 5000 WHERE EmployeeId IN (1, 2);
DELETE FROM dbo.Employees WHERE EmployeeId = 1;

SELECT AuditId, EmployeeId, Action, OldValues, NewValues FROM dbo.EmployeeAudit ORDER BY AuditId;

-- EXPECTED OUTPUT (action/salary sequence derived from equivalent row-level triggers on SQLite;
-- the JSON text, FOR JSON PATH, SESSION_CONTEXT and the FULL JOIN trigger are not executed on
-- SQL Server, so the OldValues/NewValues columns are shown only as the salary pair):
-- AuditId | EmployeeId | Action | Old Salary | New Salary
-- 1       | 1          | INSERT | NULL       | 50000
-- 2       | 2          | INSERT | NULL       | 55000
-- 3       | 1          | UPDATE | 50000      | 55000
-- 4       | 2          | UPDATE | 55000      | 60000
-- 5       | 1          | DELETE | 55000      | NULL
```

Needs SQL Server 2016+ for `FOR JSON` and `SESSION_CONTEXT`.

---

## 🔍 Why This Works (3 lines + Hindi 1 line)
The FULL JOIN of `inserted` and `deleted` yields old and new images in one set, whatever the DML type or row count. The WHERE keeps inserts, deletes and updates where a tracked column changed. SESSION_CONTEXT lets the app pass the real user, since a pooled connection always shows the same login.
हिंदी: FULL JOIN से हर DML और हर row का old/new एक साथ। Connection pool में login एक ही रहता है, इसलिए असली user SESSION_CONTEXT से भेजो।

---

## ⚡ Alternative Solution

```sql
-- System-versioned temporal table: engine records every old row version automatically
ALTER TABLE dbo.Employees ADD
  ValidFrom DATETIME2 GENERATED ALWAYS AS ROW START HIDDEN DEFAULT SYSUTCDATETIME(),
  ValidTo   DATETIME2 GENERATED ALWAYS AS ROW END HIDDEN DEFAULT CONVERT(DATETIME2, '9999-12-31 23:59:59.9999999'),
  PERIOD FOR SYSTEM_TIME (ValidFrom, ValidTo);
ALTER TABLE dbo.Employees SET (SYSTEM_VERSIONING = ON (HISTORY_TABLE = dbo.EmployeesHistory));
-- No custom code and cheap queries (FOR SYSTEM_TIME AS OF), but no "who" column.
-- Also available: SQL Server Audit / Change Tracking / CDC for compliance. Not executed here.
```

---

## ⚠️ Common Mistake

```sql
-- ❌ Wrong: one trigger per operation with scalar variables (multi-row statements log only one row)
-- ❌ Wrong: logging SUSER_SNAME() only -> every row says the app's service account.
-- ❌ Wrong: audit table in the same hot filegroup with no retention -> grows without bound,
--    and a slow audit insert slows every write on Employees.
-- ❌ Wrong: no real-change filter -> UPDATE SET Salary = Salary creates noise rows.
-- ✅ Set-based, partitioned/archived audit table, SESSION_CONTEXT for the app user.
```

---

## 🎯 Interview Tip (1 line)
Say: "For simple row history I use temporal tables; for who/what/why auditing I use a set-based trigger with FOR JSON and SESSION_CONTEXT for the application user; for compliance-grade auditing I use SQL Server Audit or CDC. I always weigh write overhead and retention."

---

## 🔗 Related Questions
→ Q096 (inserted and deleted tables) | Q094 (AFTER triggers) | Q030 (Temporal tables) | Q031 (JSON in SQL Server) | Q085 (Soft delete and audit procedure)
