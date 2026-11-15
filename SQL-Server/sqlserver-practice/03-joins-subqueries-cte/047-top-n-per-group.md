---

# Q047. Top N Per Group
# Category: Joins, Subqueries & CTEs
# Difficulty: ⭐⭐⭐ Hard
# DB: SQL Server (CROSS APPLY is T-SQL; PostgreSQL uses LATERAL, MySQL 8.0.14+ also supports LATERAL)

---

## ❓ Question
From `Employees(EmployeeId, Name, Dept, Salary)` return the top 2 earners per department. Handle ties two ways: exactly 2 rows per department, or "top 2 salary levels" where ties are all included. Also show the CROSS APPLY version.

---

## 💡 Quick Concept (2 lines only)
Number rows per group with `ROW_NUMBER() OVER (PARTITION BY Dept ORDER BY Salary DESC, EmployeeId)` and filter `rn <= N` in an outer query or CTE. Use DENSE_RANK if ties must all appear.
हिंदी: PARTITION BY से हर group में अलग numbering, फिर rn <= N filter। Ties सब चाहिए तो DENSE_RANK; exactly N चाहिए तो ROW_NUMBER।

---

## ✅ Answer / Solution

```sql
-- ============================================
-- SETUP
-- ============================================

CREATE TABLE Employees (
  EmployeeId INT PRIMARY KEY,
  Name       VARCHAR(100) NOT NULL,
  Dept       VARCHAR(50)  NOT NULL,
  Salary     INT          NOT NULL
);

INSERT INTO Employees (EmployeeId, Name, Dept, Salary) VALUES
  (1, 'Asha',   'IT',    120000),
  (2, 'Bhavna', 'IT',     95000),
  (3, 'Chetan', 'IT',     95000),   -- tied with Bhavna
  (4, 'Deepak', 'IT',     85000),
  (5, 'Esha',   'HR',     90000),
  (6, 'Farhan', 'HR',     75000),
  (7, 'Gita',   'HR',     75000),   -- tied with Farhan
  (8, 'Harsh',  'Sales',  60000),
  (9, 'Isha',   'Sales',  55000);

-- ============================================
-- EXACTLY 2 PER DEPARTMENT: ROW_NUMBER with a tiebreaker
-- ============================================
WITH Ranked AS (
  SELECT Dept, Name, Salary,
         ROW_NUMBER() OVER (PARTITION BY Dept ORDER BY Salary DESC, EmployeeId) AS rn
  FROM Employees
)
SELECT Dept, Name, Salary, rn
FROM Ranked
WHERE rn <= 2
ORDER BY Dept, rn;
-- EXPECTED OUTPUT (derived on SQLite):
-- Dept  | Name   | Salary | rn
-- HR    | Esha   | 90000  | 1
-- HR    | Farhan | 75000  | 2
-- IT    | Asha   | 120000 | 1
-- IT    | Bhavna | 95000  | 2
-- Sales | Harsh  | 60000  | 1
-- Sales | Isha   | 55000  | 2

-- ============================================
-- TOP 2 SALARY LEVELS: DENSE_RANK (ties all included)
-- ============================================
WITH Ranked AS (
  SELECT Dept, Name, Salary,
         DENSE_RANK() OVER (PARTITION BY Dept ORDER BY Salary DESC) AS dr
  FROM Employees
)
SELECT Dept, Name, Salary, dr
FROM Ranked
WHERE dr <= 2
ORDER BY Dept, dr, Name;
-- EXPECTED OUTPUT (derived on SQLite; note 3 rows for HR and IT):
-- HR    | Esha   | 90000  | 1
-- HR    | Farhan | 75000  | 2
-- HR    | Gita   | 75000  | 2
-- IT    | Asha   | 120000 | 1
-- IT    | Bhavna | 95000  | 2
-- IT    | Chetan | 95000  | 2
-- Sales | Harsh  | 60000  | 1
-- Sales | Isha   | 55000  | 2

-- ============================================
-- CROSS APPLY VERSION (T-SQL)
-- ============================================
SELECT d.Dept, t.Name, t.Salary
FROM (SELECT DISTINCT Dept FROM Employees) AS d
CROSS APPLY (
  SELECT TOP (2) e.Name, e.Salary
  FROM Employees AS e
  WHERE e.Dept = d.Dept
  ORDER BY e.Salary DESC, e.EmployeeId
) AS t
ORDER BY d.Dept, t.Salary DESC;
-- Same 6 rows as the ROW_NUMBER version. CROSS APPLY itself has no equivalent engine here:
-- the result was checked using an equivalent join on SQLite; not executed on SQL Server.
-- (SELECT TOP (2) ... WITH TIES would return the tied rows, like DENSE_RANK on the last level.)
```

---

## 🔍 Why This Works (3 lines max)
PARTITION BY makes each department its own window, so numbering restarts at 1 per group, and the outer WHERE keeps only the first N without collapsing rows like GROUP BY. The tiebreaker (`EmployeeId`) makes ROW_NUMBER deterministic. CROSS APPLY runs the TOP (N) subquery once per department, which is very fast when an index on (Dept, Salary DESC) exists.
हिंदी: हर department अलग window है, इसलिए numbering फिर से 1 से शुरू। Tiebreaker से result fix रहता है। CROSS APPLY हर group के लिए TOP (N) चलाता है।

---

## ⚡ Alternative Solution

```sql
-- Supporting index makes both approaches cheap on big tables:
CREATE INDEX IX_Employees_Dept_Salary ON Employees (Dept, Salary DESC) INCLUDE (Name);

-- When there are FEW groups and MANY rows per group, CROSS APPLY + TOP usually beats the window
-- (it does one index seek per group). When there are MANY groups with few rows, ROW_NUMBER is usually better.
-- Measure with SET STATISTICS IO ON; do not assume.
-- PostgreSQL: JOIN LATERAL (...) LIMIT N.   MySQL 8: window function or LATERAL.
```

---

## ⚠️ Common Mistake

```sql
-- ❌ Wrong: window function in WHERE
SELECT *, ROW_NUMBER() OVER (PARTITION BY Dept ORDER BY Salary DESC) AS rn
FROM Employees WHERE rn <= 2;    -- Invalid column name 'rn': WHERE is evaluated before SELECT
-- ✅ Wrap in a CTE/subquery and filter outside.

-- ❌ Wrong: no tiebreaker in ORDER BY
-- Bhavna and Chetan both earn 95000; without EmployeeId the survivor may change between runs.

-- ❌ Wrong: RANK for "exactly N rows"
-- RANK leaves gaps after ties (1,2,2,4) so rank <= 3 can return fewer or more rows than you expect.

-- ❌ Wrong: GROUP BY Dept with MAX(Salary) and expecting the employee name
```

---

## 🎯 Interview Tip (1 line)
Say: "ROW_NUMBER with a unique tiebreaker for exactly N rows, DENSE_RANK when ties must all appear, and CROSS APPLY with TOP (N) when groups are few and big. I confirm the business rule on ties first, and back it with a (group, sort) index so it does not sort the whole table."

---

## 🔗 Related Questions
→ Q067 (top-N per group with window functions) | Q056 (ROW_NUMBER, RANK, DENSE_RANK) | Q038 (CROSS APPLY) | Q045 (Nth highest salary)
