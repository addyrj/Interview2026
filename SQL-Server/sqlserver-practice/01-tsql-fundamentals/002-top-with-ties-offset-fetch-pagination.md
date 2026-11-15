---

# Q002. TOP WITH TIES and OFFSET FETCH Pagination
# Category: T-SQL Fundamentals
# Difficulty: ⭐⭐ Medium
# DB: SQL Server (OFFSET/FETCH needs 2012+; MySQL/PostgreSQL use LIMIT ... OFFSET)

---

## ❓ Question
Using the `Employees` table, return the top 2 salaries INCLUDING everyone tied with the 2nd place. Then build page 1, 2 and 3 of a 3-rows-per-page listing ordered by salary. What happens if `ORDER BY` is missing or not unique?

---

## 💡 Quick Concept (2 lines only)
`TOP (n) WITH TIES` returns n rows plus any extra rows that tie with the last row on the ORDER BY columns (ORDER BY is mandatory). `OFFSET x ROWS FETCH NEXT y ROWS ONLY` is the ANSI pager and also requires ORDER BY.
हिंदी: WITH TIES = आख़िरी row के बराबर वाली सब rows भी आती हैं। Paging के लिए OFFSET-FETCH, और ORDER BY unique रखो।

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
  Salary      DECIMAL(10,2) NOT NULL
);

INSERT INTO dbo.Employees (EmployeeId, FullName, Department, Salary) VALUES
  (1, N'Alice Rao',    N'Engineering', 120000),
  (2, N'Bob Mehta',    N'Engineering',  95000),
  (3, N'Carol Shah',   N'Engineering',  95000),
  (4, N'Dave Nair',    N'Sales',        85000),
  (5, N'Eve Iyer',     N'Sales',        80000),
  (6, N'Frank Das',    N'Sales',        90000),
  (7, N'Grace Pillai', N'HR',           70000),
  (8, N'Heidi Jain',   N'HR',           70000);

-- ============================================
-- SOLUTION 1: TOP 2 WITH TIES
-- ============================================

SELECT TOP (2) WITH TIES EmployeeId, FullName, Salary
FROM dbo.Employees
ORDER BY Salary DESC;

-- Expected output (3 rows, not 2!):
-- EmployeeId | FullName   | Salary
-- 1          | Alice Rao  | 120000.00
-- 2          | Bob Mehta  | 95000.00
-- 3          | Carol Shah | 95000.00
-- (Row order between Bob/Carol is not guaranteed - add EmployeeId to ORDER BY
--  for display order; WITH TIES would still use only the listed columns' ties.)

-- ============================================
-- SOLUTION 2: OFFSET / FETCH pagination (3 rows per page)
-- ============================================

DECLARE @PageNumber INT = 2, @PageSize INT = 3;

SELECT EmployeeId, FullName, Salary
FROM dbo.Employees
ORDER BY Salary DESC, EmployeeId          -- unique, stable order
OFFSET (@PageNumber - 1) * @PageSize ROWS
FETCH NEXT @PageSize ROWS ONLY;

-- Page 1 (@PageNumber = 1): 1 Alice 120000 | 2 Bob 95000 | 3 Carol 95000
-- Page 2 (@PageNumber = 2): 6 Frank 90000  | 4 Dave 85000 | 5 Eve 80000
-- Page 3 (@PageNumber = 3): 7 Grace 70000  | 8 Heidi 70000   (only 2 rows)

-- Note: results derived from equivalent LIMIT/OFFSET queries on SQLite;
-- not executed on SQL Server. TOP ... WITH TIES row count verified via
-- RANK() <= 2 on SQLite (3 rows).
```

---

## 🔍 Why This Works (3 lines max)
WITH TIES compares the last included row to following rows using the ORDER BY columns and keeps those that are equal, so the row count can exceed n. OFFSET skips rows after sorting and FETCH takes the next block, which is why a deterministic unique sort key (salary + id) is needed or rows can repeat/vanish across pages.
हिंदी: Tie-break के लिए unique column ज़रूरी है, वरना page 2 में वही row फिर आ सकती है या कोई row छूट सकती है।

---

## ⚡ Alternative Solution

```sql
-- Same as WITH TIES using RANK() (works everywhere, filter any rank):
SELECT EmployeeId, FullName, Salary
FROM (
  SELECT *, RANK() OVER (ORDER BY Salary DESC) AS rk
  FROM dbo.Employees
) AS r
WHERE rk <= 2;

-- Keyset pagination (faster for deep pages, no OFFSET scan cost):
DECLARE @LastSalary DECIMAL(10,2) = 95000, @LastId INT = 3;
SELECT TOP (3) EmployeeId, FullName, Salary
FROM dbo.Employees
WHERE Salary < @LastSalary
   OR (Salary = @LastSalary AND EmployeeId > @LastId)
ORDER BY Salary DESC, EmployeeId;
```

---

## ⚠️ Common Mistake

```sql
-- ❌ Wrong: OFFSET without ORDER BY -> syntax error in SQL Server
SELECT * FROM dbo.Employees OFFSET 3 ROWS FETCH NEXT 3 ROWS ONLY;

-- ❌ Wrong: non-unique ORDER BY while paging
SELECT * FROM dbo.Employees ORDER BY Salary DESC OFFSET 3 ROWS FETCH NEXT 3 ROWS ONLY;
-- Bob/Carol (95000) and Grace/Heidi (70000) may swap between page requests.

-- ❌ Wrong: TOP ... WITH TIES without ORDER BY -> error (ORDER BY is required)
SELECT TOP (2) WITH TIES * FROM dbo.Employees;

-- ❌ Wrong: assuming OFFSET scales - OFFSET 1000000 still reads and discards 1M rows.
```

---

## 🎯 Interview Tip (1 line)
Say: "OFFSET/FETCH is fine for admin screens, but for deep or high-traffic paging I use keyset pagination on an indexed (Salary, Id) pair and return a total count separately or cache it. WITH TIES is my answer for 'top N including ties', with RANK as the portable alternative."

---

## 🔗 Related Questions
→ Q001 (SELECT, WHERE, ORDER BY, TOP) | Q056 (ROW_NUMBER, RANK, DENSE_RANK) | Q083 (Pagination procedure with total count) | Q147 (Pagination performance) | Q190 (Pagination in SQL Server)
