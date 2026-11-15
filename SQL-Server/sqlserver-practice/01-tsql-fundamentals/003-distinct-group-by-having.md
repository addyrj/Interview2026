---

# Q003. DISTINCT, GROUP BY and HAVING
# Category: T-SQL Fundamentals
# Difficulty: ⭐ Easy
# DB: SQL Server (same ANSI behaviour in MySQL/PostgreSQL; MySQL used to allow non-grouped columns)

---

## ❓ Question
From `Employees`: list the distinct departments; show headcount, total and average salary per department; then show only departments with at least 2 employees hired since 2020. Explain WHERE vs HAVING.

---

## 💡 Quick Concept (2 lines only)
`GROUP BY` collapses rows into groups and aggregates them; `HAVING` filters groups AFTER aggregation, `WHERE` filters rows BEFORE it. `DISTINCT` removes duplicate result rows (it sorts/hashes, so it is not free).
हिंदी: WHERE = group बनने से पहले rows filter, HAVING = group बनने के बाद filter।

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
-- 1. DISTINCT
-- ============================================

SELECT DISTINCT Department FROM dbo.Employees ORDER BY Department;
-- Engineering
-- HR
-- Sales

-- ============================================
-- 2. GROUP BY with aggregates
-- ============================================

SELECT Department,
       COUNT(*)                              AS Headcount,
       SUM(Salary)                           AS TotalSalary,
       CAST(AVG(Salary) AS DECIMAL(10,2))    AS AvgSalary
FROM dbo.Employees
GROUP BY Department
ORDER BY Department;

-- Department  | Headcount | TotalSalary | AvgSalary
-- Engineering | 3         | 310000.00   | 103333.33
-- HR          | 2         | 140000.00   | 70000.00
-- Sales       | 3         | 255000.00   | 85000.00

-- ============================================
-- 3. WHERE + GROUP BY + HAVING
-- ============================================

SELECT Department,
       COUNT(*)                           AS Headcount,
       CAST(AVG(Salary) AS DECIMAL(10,2)) AS AvgSalary
FROM dbo.Employees
WHERE HireDate >= '2020-01-01'          -- row filter, runs first
GROUP BY Department
HAVING COUNT(*) >= 2                    -- group filter, runs after aggregation
ORDER BY Department;

-- Department  | Headcount | AvgSalary
-- Engineering | 2         | 107500.00
-- HR          | 2         | 70000.00
-- Sales       | 3         | 85000.00
-- (Carol, hired 2019, is removed by WHERE before grouping)

-- COUNT(DISTINCT Salary) over the table = 6 (distinct values: 120000, 95000, 90000, 85000, 80000, 70000)

-- Note: result derived from equivalent query on SQLite (AVG formatted to 2 decimals);
-- not executed on SQL Server. Without the CAST, SQL Server shows AVG of DECIMAL(10,2)
-- with more decimal places.
```

---

## 🔍 Why This Works (3 lines max)
Logical order is FROM → WHERE → GROUP BY → HAVING → SELECT → DISTINCT → ORDER BY, so HAVING can use aggregates but not SELECT aliases, and WHERE cannot use aggregates at all. Every non-aggregated column in SELECT must appear in GROUP BY — SQL Server enforces this (error), unlike old MySQL modes.
हिंदी: SELECT के हर non-aggregate column को GROUP BY में होना चाहिए, वरना SQL Server error देता है।

---

## ⚡ Alternative Solution

```sql
-- DISTINCT vs GROUP BY: same plan for plain de-duplication
SELECT Department FROM dbo.Employees GROUP BY Department;

-- Group filter without HAVING (derived table) - useful when you need the filter in reuse:
SELECT *
FROM (
  SELECT Department, COUNT(*) AS Headcount
  FROM dbo.Employees
  GROUP BY Department
) AS g
WHERE g.Headcount >= 3;
```

---

## ⚠️ Common Mistake

```sql
-- ❌ Wrong: aggregate in WHERE
SELECT Department FROM dbo.Employees WHERE COUNT(*) > 1 GROUP BY Department;  -- error
-- ✅ HAVING COUNT(*) > 1

-- ❌ Wrong: column neither grouped nor aggregated
SELECT Department, FullName, AVG(Salary) FROM dbo.Employees GROUP BY Department;  -- error

-- ❌ Wrong: HAVING used as a row filter (works but scans/groups everything first)
SELECT Department, COUNT(*) FROM dbo.Employees
GROUP BY Department HAVING Department = N'Sales';
-- ✅ Put non-aggregate conditions in WHERE so they can use an index and shrink the work.

-- ❌ Wrong: DISTINCT sprinkled to "fix" duplicates caused by a bad join -> hides the bug.
```

---

## 🎯 Interview Tip (1 line)
Say: "Row-level predicates go in WHERE, only aggregate predicates in HAVING. If a join produces duplicates I fix the join key or aggregate first instead of slapping DISTINCT on it, because DISTINCT adds a sort/hash and can hide wrong results."

---

## 🔗 Related Questions
→ Q001 (SELECT, WHERE, ORDER BY, TOP) | Q062 (Aggregate functions with NULL) | Q061 (ROLLUP, CUBE, GROUPING SETS) | Q172 (WHERE vs HAVING) | Q188 (Find duplicate rows)
