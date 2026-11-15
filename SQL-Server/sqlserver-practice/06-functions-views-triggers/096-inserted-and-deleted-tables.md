---

# Q096. inserted and deleted Tables
# Category: Functions, Views + Triggers
# Difficulty: ⭐⭐ Medium
# DB: SQL Server (MySQL/SQLite/PostgreSQL use row-level OLD and NEW instead of these pseudo-tables)

---

## ❓ Question
What do the `inserted` and `deleted` tables contain for INSERT, UPDATE and DELETE statements? Show how to detect which operation fired a trigger and compare old vs new salary for a multi-row UPDATE.

---

## 💡 Quick Concept (2 lines only)
`inserted` holds new row images, `deleted` holds old row images, for all rows the statement touched. INSERT = only inserted; DELETE = only deleted; UPDATE = both (same key in each, old in deleted, new in inserted).
हिंदी: `inserted` = नई rows, `deleted` = पुरानी rows, पूरे statement की। INSERT में सिर्फ़ inserted, DELETE में सिर्फ़ deleted, UPDATE में दोनों।

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

CREATE TABLE dbo.SalaryChangeLog (
  LogId      INT IDENTITY(1,1) PRIMARY KEY,
  EmployeeId INT NOT NULL,
  Operation  VARCHAR(10) NOT NULL,
  OldSalary  DECIMAL(10,2) NULL,
  NewSalary  DECIMAL(10,2) NULL
);
GO

-- ============================================
-- SOLUTION
-- ============================================

CREATE OR ALTER TRIGGER dbo.trg_Employees_Log
ON dbo.Employees
AFTER INSERT, UPDATE, DELETE
AS
BEGIN
  SET NOCOUNT ON;

  -- FULL JOIN pairs old and new images; unmatched side = INSERT or DELETE
  INSERT INTO dbo.SalaryChangeLog (EmployeeId, Operation, OldSalary, NewSalary)
  SELECT COALESCE(i.EmployeeId, d.EmployeeId),
         CASE WHEN d.EmployeeId IS NULL THEN 'INSERT'
              WHEN i.EmployeeId IS NULL THEN 'DELETE'
              ELSE 'UPDATE' END,
         d.Salary,
         i.Salary
  FROM inserted i
  FULL OUTER JOIN deleted d ON d.EmployeeId = i.EmployeeId
  WHERE d.EmployeeId IS NULL OR i.EmployeeId IS NULL OR d.Salary <> i.Salary;
END;
GO

INSERT INTO dbo.Employees VALUES (1, N'Ravi', 50000), (2, N'Neha', 55000);
UPDATE dbo.Employees SET Salary = Salary + 5000 WHERE EmployeeId IN (1, 2);
DELETE FROM dbo.Employees WHERE EmployeeId = 1;

SELECT LogId, EmployeeId, Operation, OldSalary, NewSalary FROM dbo.SalaryChangeLog ORDER BY LogId;

-- EXPECTED OUTPUT (same sequence reproduced with three row-level triggers on SQLite using
-- OLD/NEW; the single FULL JOIN trigger is not executed on SQL Server; in SQL Server the two
-- UPDATE rows come from ONE trigger run. LogId order within one statement is not guaranteed):
-- LogId | EmployeeId | Operation | OldSalary | NewSalary
-- 1     | 1          | INSERT    | NULL      | 50000.00
-- 2     | 2          | INSERT    | NULL      | 55000.00
-- 3     | 1          | UPDATE    | 50000.00  | 55000.00
-- 4     | 2          | UPDATE    | 55000.00  | 60000.00
-- 5     | 1          | DELETE    | 55000.00  | NULL
```

---

## 🔍 Why This Works (3 lines + Hindi 1 line)
Joining the two pseudo-tables on the primary key gives old and new values side by side for every row. A row missing on one side tells you the operation, so one trigger covers all three DML types. They are scoped to the trigger and live only for the duration of the statement.
हिंदी: Primary key पर join करो तो old और new values साथ मिलती हैं। कोई side missing हो तो operation पता चल जाता है। ये tables सिर्फ़ trigger के अंदर और statement तक ही होती हैं।

---

## ⚡ Alternative Solution

```sql
-- Outside triggers: the OUTPUT clause exposes the same images for any DML statement
UPDATE dbo.Employees SET Salary = Salary + 5000
OUTPUT inserted.EmployeeId, deleted.Salary AS OldSalary, inserted.Salary AS NewSalary
WHERE EmployeeId = 2;
-- MERGE exposes both plus $action. Not executed on SQL Server; behaviour per Microsoft docs.
```

---

## ⚠️ Common Mistake

```sql
-- ❌ Wrong: reading a scalar from inserted
DECLARE @newSalary DECIMAL(10,2) = (SELECT Salary FROM inserted);   -- fails/arbitrary when >1 row
-- ❌ Wrong: referencing deleted in an INSERT trigger (it is empty) or joining on a non-key column.
-- ❌ Wrong: assuming trigger fired for 0 rows is skipped -> it still fires, with empty tables;
--    guard with IF NOT EXISTS (SELECT 1 FROM inserted) AND NOT EXISTS (SELECT 1 FROM deleted) RETURN;
-- ✅ Always treat them as sets; determine the operation by EXISTS on each side.
```

---

## 🎯 Interview Tip (1 line)
Say: "inserted/deleted are statement-scoped row sets, so triggers must be set-based. I derive the operation from which side has rows, join on the primary key for old vs new, handle the zero-row case, and note that OUTPUT gives the same images without a trigger."

---

## 🔗 Related Questions
→ Q094 (AFTER triggers) | Q095 (INSTEAD OF triggers) | Q097 (Audit trigger pattern) | Q084 (Upsert: MERGE vs UPDATE/INSERT) | Q073 (TRY...CATCH inside procedures)
