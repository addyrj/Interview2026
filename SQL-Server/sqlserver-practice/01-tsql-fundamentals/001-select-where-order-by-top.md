---

# Q001. SELECT, WHERE, ORDER BY and TOP
# Category: T-SQL Fundamentals
# Difficulty: ⭐ Easy
# DB: SQL Server (MySQL/PostgreSQL use LIMIT instead of TOP)

---

## ❓ Question
From an `Employees` table, return the 2 highest-paid Engineering employees earning at least 90,000. Then return the top 3 paid employees company-wide. Explain why `TOP` without `ORDER BY` is a bug and when `TOP (n) PERCENT` or `TOP (@n)` is useful.

---

## 💡 Quick Concept (2 lines only)
`TOP (n)` limits rows AFTER `ORDER BY` is applied; without `ORDER BY` the rows you get are whatever the engine reads first (non-deterministic). Logical order: FROM → WHERE → SELECT → ORDER BY → TOP.
हिंदी: TOP हमेशा ORDER BY के साथ use करो, वरना कौन सी rows आएँगी इसकी कोई guarantee नहीं।

---

## ✅ Answer / Solution

```sql
-- ============================================
-- SETUP
-- ============================================

CREATE TABLE dbo.Employees (
  EmployeeId  INT           NOT NULL PRIMARY KEY,
  FullName    NVARCHAR(100) NOT NULL,
  Department  NVARCHAR(50)  NOT NULL,
  Salary      DECIMAL(10,2) NOT NULL,
  HireDate    DATE          NOT NULL
);

INSERT INTO dbo.Employees (EmployeeId, FullName, Department, Salary, HireDate) VALUES
  (1, N'Alice Rao',    N'Engineering', 120000, '2020-01-15'),
  (2, N'Bob Mehta',    N'Engineering',  95000, '2021-03-20'),
  (3, N'Carol Shah',   N'Engineering',  95000, '2019-07-01'),
  (4, N'Dave Nair',    N'Sales',        85000, '2022-05-10'),
  (5, N'Eve Iyer',     N'Sales',        80000, '2023-01-05'),
  (6, N'Frank Das',    N'Sales',        90000, '2020-02-28'),
  (7, N'Grace Pillai', N'HR',           70000, '2021-08-15'),
  (8, N'Heidi Jain',   N'HR',           70000, '2020-11-30');

-- ============================================
-- SOLUTION 1: Top 2 Engineering earners >= 90000
-- ============================================

SELECT TOP (2) EmployeeId, FullName, Salary
FROM dbo.Employees
WHERE Department = N'Engineering'
  AND Salary >= 90000
ORDER BY Salary DESC, FullName;   -- FullName = deterministic tiebreaker

-- Expected output:
-- EmployeeId | FullName   | Salary
-- 1          | Alice Rao  | 120000.00
-- 2          | Bob Mehta  | 95000.00
-- (Bob and Carol tie at 95000 -> tiebreaker FullName picks Bob)

-- ============================================
-- SOLUTION 2: Top 3 company-wide (variable + percent forms)
-- ============================================

DECLARE @n INT = 3;

SELECT TOP (@n) EmployeeId, FullName, Department, Salary
FROM dbo.Employees
ORDER BY Salary DESC, EmployeeId;

-- Expected output (3 rows):
-- 1 | Alice Rao  | Engineering | 120000.00
-- 2 | Bob Mehta  | Engineering | 95000.00
-- 3 | Carol Shah | Engineering | 95000.00

-- TOP (25) PERCENT -> 25% of 8 rows = 2 rows (rounded UP when fractional)
SELECT TOP (25) PERCENT FullName, Salary
FROM dbo.Employees
ORDER BY Salary DESC;

-- Note: result derived from equivalent query on SQLite (LIMIT 2 / LIMIT 3);
-- not executed on SQL Server. TOP syntax was parsed with sqlglot (tsql).
```

---

## 🔍 Why This Works (3 lines max)
`WHERE` filters rows first, `ORDER BY` sorts the survivors, and `TOP` cuts the sorted set — so the order of clauses in your head must follow logical processing, not typing order. Parentheses in `TOP (n)` are mandatory for variables and for INSERT/UPDATE/DELETE. Adding a unique tiebreaker column makes the result repeatable.
हिंदी: पहले WHERE, फिर ORDER BY, फिर TOP। Tie हो तो extra column से order तय करो।

---

## ⚡ Alternative Solution

```sql
-- Standard ANSI form (SQL Server 2012+): OFFSET/FETCH
SELECT EmployeeId, FullName, Salary
FROM dbo.Employees
WHERE Department = N'Engineering' AND Salary >= 90000
ORDER BY Salary DESC, FullName
OFFSET 0 ROWS FETCH NEXT 2 ROWS ONLY;

-- MySQL / PostgreSQL / SQLite equivalent:
--   ... ORDER BY Salary DESC, FullName LIMIT 2;
```

---

## ⚠️ Common Mistake

```sql
-- ❌ Wrong: TOP without ORDER BY -> arbitrary rows, can change after an index/plan change
SELECT TOP (3) * FROM dbo.Employees;

-- ❌ Wrong: TOP 3 (no parentheses) with a variable
DECLARE @n INT = 3;
SELECT TOP @n * FROM dbo.Employees ORDER BY Salary DESC;  -- syntax error
-- ✅ SELECT TOP (@n) ...

-- ❌ Wrong: referencing a SELECT alias in WHERE
SELECT Salary * 12 AS AnnualSalary FROM dbo.Employees WHERE AnnualSalary > 1000000;
-- WHERE is evaluated BEFORE SELECT -> alias unknown. Repeat the expression or use a CTE.
-- (ORDER BY CAN use the alias because it runs after SELECT.)
```

---

## 🎯 Interview Tip (1 line)
Say: "I never ship TOP without ORDER BY plus a unique tiebreaker, and I use TOP (@n) with a parameter so the plan can be reused. For paging I move to OFFSET/FETCH or keyset, and for ties I'd use WITH TIES." Mentioning logical query processing order (FROM, WHERE, GROUP BY, HAVING, SELECT, ORDER BY, TOP) is the 5+ YOE signal.

---

## 🔗 Related Questions
→ Q002 (TOP WITH TIES and OFFSET FETCH) | Q003 (DISTINCT, GROUP BY, HAVING) | Q147 (Pagination performance) | Q190 (Pagination in SQL Server)
