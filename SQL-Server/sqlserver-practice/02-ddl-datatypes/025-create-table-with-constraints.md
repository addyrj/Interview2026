---

# Q025. CREATE TABLE with Constraints
# Category: DDL + DATA TYPES
# Difficulty: ⭐⭐ Medium
# DB: SQL Server (MySQL: constraint names optional, CHECK enforced from 8.0.16; PostgreSQL: same ANSI syntax)

---

## ❓ Question
Create Departments and Employees tables with a primary key, identity, foreign key, unique email, a CHECK on salary and a DEFAULT hire date. Name every constraint explicitly. Show which inserts fail.

---

## 💡 Quick Concept (2 lines only)
Constraints enforce data rules inside the database: PRIMARY KEY, UNIQUE, FOREIGN KEY, CHECK, DEFAULT, NOT NULL. Always name them (`PK_`, `UQ_`, `FK_`, `CK_`, `DF_`) so error messages and later ALTERs are readable.
हिंदी: Constraints data rules को database में enforce करते हैं। हर constraint का नाम खुद दो (PK_, FK_, CK_...), वरना SQL Server random नाम बना देता है।

---

## ✅ Answer / Solution

```sql
-- ============================================
-- SETUP
-- ============================================

CREATE TABLE Departments (
  DepartmentId INT           NOT NULL,
  Name         NVARCHAR(100) NOT NULL,
  CONSTRAINT PK_Departments      PRIMARY KEY (DepartmentId),
  CONSTRAINT UQ_Departments_Name UNIQUE (Name)
);

CREATE TABLE Employees (
  EmployeeId   INT IDENTITY(1,1) NOT NULL,
  Email        VARCHAR(255)  NOT NULL,
  Salary       DECIMAL(10,2) NOT NULL,
  DepartmentId INT           NOT NULL,
  HireDate     DATE          NOT NULL
               CONSTRAINT DF_Employees_HireDate DEFAULT (CAST(GETDATE() AS DATE)),
  CONSTRAINT PK_Employees       PRIMARY KEY (EmployeeId),
  CONSTRAINT UQ_Employees_Email UNIQUE (Email),
  CONSTRAINT CK_Employees_Salary CHECK (Salary > 0),
  CONSTRAINT FK_Employees_Departments
      FOREIGN KEY (DepartmentId) REFERENCES Departments (DepartmentId)
);

INSERT INTO Departments (DepartmentId, Name) VALUES (1, N'Engineering'), (2, N'Sales');
GO

-- ============================================
-- SOLUTION: valid and invalid inserts
-- ============================================

INSERT INTO Employees (Email, Salary, DepartmentId) VALUES ('asha@corp.com', 90000, 1);

SELECT EmployeeId, Email, Salary, DepartmentId FROM Employees;

-- Output:
-- EmployeeId | Email         | Salary   | DepartmentId
-- 1          | asha@corp.com | 90000.00 | 1
-- (HireDate defaults to today's date, so it is omitted from this output.)

-- Each of these fails:
INSERT INTO Employees (Email, Salary, DepartmentId) VALUES ('asha@corp.com', 1, 1);   -- duplicate email
INSERT INTO Employees (Email, Salary, DepartmentId) VALUES ('b@corp.com', -1, 1);     -- CHECK violated
INSERT INTO Employees (Email, Salary, DepartmentId) VALUES ('c@corp.com', 10, 9);     -- no department 9

-- Expected: unique violation (error 2627), CHECK violation (547), FOREIGN KEY violation (547); the
-- messages name the constraint, e.g. "...conflicted with the CHECK constraint "CK_Employees_Salary"".
-- Valid row and all three rejections verified on SQLite 3.49 (messages there differ); error numbers
-- and message text per Microsoft docs; not executed on SQL Server.
```

---

## 🔍 Why This Works (3 lines max)
The engine checks each constraint on every INSERT/UPDATE and rolls back the statement on violation. Named constraints give readable errors (`CK_Employees_Salary`) and let `ALTER TABLE ... DROP CONSTRAINT` target them directly. A PRIMARY KEY creates a clustered index by default, and UNIQUE creates a nonclustered unique index.
हिंदी: हर INSERT/UPDATE पर constraints check होते हैं और violation पर statement rollback। नाम देने से error और बाद का ALTER आसान। PRIMARY KEY default में clustered index बनाता है।

---

## ⚡ Alternative Solution

```sql
-- Add constraints after the table exists (typical in migrations)
ALTER TABLE Employees ADD CONSTRAINT CK_Employees_Email CHECK (Email LIKE '%_@_%._%');

-- Composite key and table-level CHECK across columns
CREATE TABLE OrderItems (
  OrderId   INT NOT NULL,
  LineNo    INT NOT NULL,
  Quantity  INT NOT NULL,
  UnitPrice DECIMAL(10,2) NOT NULL,
  CONSTRAINT PK_OrderItems PRIMARY KEY (OrderId, LineNo),
  CONSTRAINT CK_OrderItems_Qty CHECK (Quantity > 0 AND UnitPrice >= 0)
);

-- Inspect constraints
SELECT name, type_desc FROM sys.objects
WHERE parent_object_id = OBJECT_ID('dbo.Employees') AND type IN ('PK','UQ','F','C','D');
```

---

## ⚠️ Common Mistake

```sql
-- ❌ Wrong: unnamed constraints - SQL Server generates names like PK__Employee__7AD04F11A3B2C1D0,
--           different per environment, so migration scripts that drop them by name break
CREATE TABLE Bad (Id INT PRIMARY KEY, Email VARCHAR(100) UNIQUE);

-- ❌ Wrong: no FOREIGN KEY "because it is faster" - orphan rows are the price
-- ❌ Wrong: DEFAULT GETDATE() on a DATE column without CAST works but stores the converted value;
--           use SYSUTCDATETIME() on DATETIME2 columns for audit timestamps
-- ❌ Wrong: a CHECK that calls a user function doing lookups (slow, not safe against changes)
```

---

## 🎯 Interview Tip (1 line)
Say: "I name every constraint, keep rules in the database as the last line of defence (the app validates too), and index foreign key columns because SQL Server does not do that automatically." Also note a PRIMARY KEY is clustered unless I say NONCLUSTERED.

---

## 🔗 Related Questions
→ Q026 (PK, UNIQUE, FK with cascade) | Q027 (CHECK and DEFAULT) | Q102 (clustered vs non-clustered) | Q176 (primary key vs unique key vs foreign key)
