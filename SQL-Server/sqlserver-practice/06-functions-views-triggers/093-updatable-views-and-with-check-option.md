---

# Q093. Updatable Views and WITH CHECK OPTION
# Category: Functions, Views + Triggers
# Difficulty: ⭐⭐ Medium
# DB: SQL Server (MySQL and PostgreSQL also support WITH CHECK OPTION on simple views)

---

## ❓ Question
Create a view `vSalesEmployees` showing only Sales employees. Can you INSERT/UPDATE through it? What happens if an update moves a row out of the view's filter, and how does WITH CHECK OPTION change that?

---

## 💡 Quick Concept (2 lines only)
A single-table view with no aggregates/DISTINCT/TOP can be modified; changes go to the base table. Without WITH CHECK OPTION, an update can make the row vanish from the view; with it, SQL Server rejects any INSERT/UPDATE that would leave the view's WHERE condition.
हिंदी: Simple view पर INSERT/UPDATE चलता है, base table बदलती है। WITH CHECK OPTION के बिना row view से गायब हो सकती है; उसके साथ ऐसा update reject होता है।

---

## ✅ Answer / Solution

```sql
-- ============================================
-- SETUP
-- ============================================

CREATE TABLE dbo.Employees (
  EmployeeId INT PRIMARY KEY,
  Name       NVARCHAR(100) NOT NULL,
  Department VARCHAR(20)   NOT NULL,
  Salary     DECIMAL(10,2) NOT NULL
);

INSERT INTO dbo.Employees VALUES
  (1, N'Ravi', 'Sales', 50000),
  (2, N'Neha', 'Sales', 55000),
  (3, N'Arun', 'HR',    45000);
GO

-- ============================================
-- SOLUTION
-- ============================================

CREATE OR ALTER VIEW dbo.vSalesEmployees
AS
SELECT EmployeeId, Name, Department, Salary
FROM dbo.Employees
WHERE Department = 'Sales'
WITH CHECK OPTION;
GO

-- Allowed: row stays inside the filter
UPDATE dbo.vSalesEmployees SET Salary = 60000 WHERE EmployeeId = 1;

-- Rejected by CHECK OPTION: the new row would no longer satisfy Department = 'Sales'
UPDATE dbo.vSalesEmployees SET Department = 'HR' WHERE EmployeeId = 2;   -- raises an error, nothing changes

-- Rejected too: INSERT of a non-Sales row via the view
INSERT INTO dbo.vSalesEmployees (EmployeeId, Name, Department, Salary) VALUES (4, N'Zoya', 'HR', 40000);

-- The same moves directly on the BASE table are allowed (CHECK OPTION guards only the view):
UPDATE dbo.Employees SET Department = 'HR' WHERE EmployeeId = 2;
SELECT EmployeeId, Name, Department FROM dbo.vSalesEmployees ORDER BY EmployeeId;

-- EXPECTED OUTPUT (last query only; derived from equivalent statements on SQLite, which has
-- no WITH CHECK OPTION, so the two rejections are NOT executed here and the exact error text
-- is not shown; behaviour per Microsoft docs):
-- EmployeeId | Name | Department
-- 1          | Ravi | Sales
```

---

## 🔍 Why This Works (3 lines + Hindi 1 line)
A view over one table maps each view row to exactly one base row, so DML can be translated. WITH CHECK OPTION re-evaluates the view's WHERE on the modified row and fails the statement if it no longer qualifies. It does not stop direct changes to the base table.
हिंदी: View की हर row base की एक row से map होती है इसलिए DML चलता है। CHECK OPTION modified row पर WHERE दोबारा जाँचता है। Base table पर direct update नहीं रोकता।

---

## ⚡ Alternative Solution

```sql
-- Complex views (joins, aggregates): make them updatable with an INSTEAD OF trigger (Q095),
-- or skip the view and use a stored procedure to apply the change with validation.
-- Row-Level Security predicates (2016+) can block rows at the table level for all access paths:
-- CREATE SECURITY POLICY ... ADD BLOCK PREDICATE ...   (not executed here)
```

---

## ⚠️ Common Mistake

```sql
-- ❌ Wrong: view without CHECK OPTION used as "security" for writes
UPDATE dbo.vSalesEmployees SET Department = 'HR' WHERE EmployeeId = 2;   -- succeeds silently, row disappears
-- ❌ Wrong: thinking CHECK OPTION protects the base table from direct updates.
-- ❌ Wrong: trying to update a view with GROUP BY/DISTINCT/UNION, or a join view touching two base
--    tables in one statement (limited to columns of one table per statement).
-- ✅ WITH CHECK OPTION + permissions on the view only.
```

---

## 🎯 Interview Tip (1 line)
Say: "For tenant or status-scoped views I add WITH CHECK OPTION so writes cannot escape the filter, remember it only protects access through the view, and use INSTEAD OF triggers or procedures when the view is too complex to be directly updatable."

---

## 🔗 Related Questions
→ Q091 (Views) | Q095 (INSTEAD OF triggers) | Q027 (CHECK and DEFAULT constraints) | Q081 (WITH EXECUTE AS and security) | Q096 (inserted and deleted tables)
