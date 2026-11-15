---

# Q010. INSERT, UPDATE, DELETE and the OUTPUT Clause
# Category: T-SQL Fundamentals
# Difficulty: ⭐⭐ Medium
# DB: SQL Server (OUTPUT is T-SQL; PostgreSQL/SQLite use RETURNING, MySQL has no equivalent)

---

## ❓ Question
Insert a new employee and get the generated id back, give Sales a 10% raise while capturing old and new salaries, and delete the HR employee while saving the deleted row to an archive. Use the `OUTPUT` clause. How does it differ from `SCOPE_IDENTITY()`?

---

## 💡 Quick Concept (2 lines only)
`OUTPUT` returns (or inserts into a table) the affected rows using the pseudo-tables `inserted` (new values) and `deleted` (old values) - in one atomic statement. UPDATE exposes both; INSERT only `inserted`; DELETE only `deleted`.
हिंदी: OUTPUT = बदली हुई rows तुरंत वापस। inserted = नई values, deleted = पुरानी values।

---

## ✅ Answer / Solution

```sql
-- ============================================
-- SETUP
-- ============================================

CREATE TABLE dbo.Employees (
  EmployeeId  INT IDENTITY(1,1) PRIMARY KEY,
  FullName    NVARCHAR(100) NOT NULL,
  Department  NVARCHAR(50)  NOT NULL,
  Salary      DECIMAL(10,2) NOT NULL
);

CREATE TABLE dbo.EmployeesArchive (
  EmployeeId  INT NOT NULL,
  FullName    NVARCHAR(100) NOT NULL,
  Salary      DECIMAL(10,2) NOT NULL,
  ArchivedAt  DATETIME2(0)  NOT NULL DEFAULT SYSUTCDATETIME()
);

INSERT INTO dbo.Employees (FullName, Department, Salary) VALUES
  (N'Alice Rao',  N'Engineering', 100000),
  (N'Bob Mehta',  N'Sales',        80000),
  (N'Carol Shah', N'Sales',        75000);

-- ============================================
-- 1. INSERT ... OUTPUT inserted (works for multi-row inserts, unlike SCOPE_IDENTITY)
-- ============================================

INSERT INTO dbo.Employees (FullName, Department, Salary)
OUTPUT inserted.EmployeeId, inserted.FullName, inserted.Salary
VALUES (N'Dave Nair', N'HR', 70000);

-- EmployeeId | FullName  | Salary
-- 4          | Dave Nair | 70000.00

-- ============================================
-- 2. UPDATE ... OUTPUT deleted (old) and inserted (new)
-- ============================================

UPDATE dbo.Employees
SET Salary = Salary * 1.10
OUTPUT inserted.EmployeeId,
       deleted.Salary  AS OldSalary,
       inserted.Salary AS NewSalary
WHERE Department = N'Sales';

-- EmployeeId | OldSalary | NewSalary
-- 2          | 80000.00  | 88000.00
-- 3          | 75000.00  | 82500.00

-- ============================================
-- 3. DELETE ... OUTPUT INTO an archive table (atomic move)
-- ============================================

DELETE FROM dbo.Employees
OUTPUT deleted.EmployeeId, deleted.FullName, deleted.Salary, SYSUTCDATETIME()
  INTO dbo.EmployeesArchive (EmployeeId, FullName, Salary, ArchivedAt)
WHERE Department = N'HR';

SELECT EmployeeId, FullName, Salary FROM dbo.EmployeesArchive;   -- 4 | Dave Nair | 70000.00

-- Note: new/old values derived from equivalent INSERT/UPDATE/DELETE ... RETURNING on SQLite;
-- the OUTPUT clause itself, OUTPUT INTO and the IDENTITY value (assumed 4 for the next row)
-- are per Microsoft docs; not executed on SQL Server.
```

---

## 🔍 Why This Works (3 lines max)
OUTPUT reads from the same internal rowset the DML statement modified, so you get exactly the rows that changed with no second query and no race window. `OUTPUT INTO` writes them to a table in the same statement, which makes "archive while deleting" or audit capture atomic.
हिंदी: एक ही statement में बदलाव + उसका record, बीच में कोई दूसरी query नहीं।

---

## ⚡ Alternative Solution

```sql
-- Single-row insert: SCOPE_IDENTITY() (last identity created in THIS scope and session)
INSERT INTO dbo.Employees (FullName, Department, Salary) VALUES (N'Eve Iyer', N'HR', 65000);
SELECT SCOPE_IDENTITY() AS NewId;

-- Multi-row insert: capture all ids into a table variable
DECLARE @new TABLE (EmployeeId INT, FullName NVARCHAR(100));
INSERT INTO dbo.Employees (FullName, Department, Salary)
OUTPUT inserted.EmployeeId, inserted.FullName INTO @new
VALUES (N'Frank Das', N'HR', 60000), (N'Grace Pillai', N'HR', 61000);
SELECT * FROM @new;

-- PostgreSQL / SQLite: INSERT ... RETURNING id;   MySQL: LAST_INSERT_ID() (first id of a multi-row insert)
```

---

## ⚠️ Common Mistake

```sql
-- ❌ Wrong: UPDATE/DELETE without WHERE (every row changed!)
DELETE FROM dbo.Employees;
-- ✅ Wrap in BEGIN TRAN, check @@ROWCOUNT, or SELECT with the same WHERE first.

-- ❌ Wrong: OUTPUT INTO a table that has enabled triggers or foreign keys (not allowed as target)
--    -> use a plain staging table or table variable, then copy.

-- ❌ Wrong: using @@IDENTITY (can return an id from a trigger's insert into another table)
-- ✅ SCOPE_IDENTITY() or OUTPUT.

-- ❌ Wrong: referencing 'deleted' in an INSERT ... OUTPUT (only 'inserted' exists there).

-- ❌ Wrong: assuming OUTPUT row order matches VALUES order unless you control it via ORDER BY in INSERT ... SELECT (no guarantee).
```

---

## 🎯 Interview Tip (1 line)
Say: "For multi-row writes I use OUTPUT into a table variable instead of SCOPE_IDENTITY, which only returns one value. In a Node mssql app I run INSERT ... OUTPUT inserted.Id in a single round trip. For audit I prefer OUTPUT INTO from the procedure over triggers, because it is explicit and cheaper."

---

## 🔗 Related Questions
→ Q013 (IDENTITY, SCOPE_IDENTITY, SEQUENCE) | Q011 (MERGE) | Q085 (Soft delete and audit logging procedure) | Q096 (inserted and deleted tables) | Q097 (Audit trigger pattern)
