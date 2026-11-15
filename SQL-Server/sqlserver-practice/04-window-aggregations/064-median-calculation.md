# Q064. Median Calculation
# Category: WINDOW FUNCTIONS + AGGREGATIONS
# Difficulty: ⭐⭐⭐ Hard
# DB: SQL Server (2012+) — no MEDIAN() function exists; PostgreSQL has PERCENTILE_CONT as an aggregate; MySQL needs ROW_NUMBER

---

## ❓ Question
Find the median salary per department. Departments have an odd (Finance: 1) and even (IT, HR: 4) number of employees, so the median must average the two middle rows when the count is even. Show two ways: PERCENTILE_CONT and a ROW_NUMBER approach that works everywhere.

---

## 💡 Quick Concept (2 lines only)
SQL Server has no MEDIAN. Use `PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY col) OVER (PARTITION BY ...)`, or number the rows and average the middle one or two.
हिंदी: SQL Server में MEDIAN function नहीं है। PERCENTILE_CONT(0.5) या ROW_NUMBER से बीच की 1 या 2 rows का average लो।

---

## ✅ Answer / Solution

```sql
-- ============================================
-- SETUP
-- ============================================
CREATE TABLE Employees (
    EmpId   INT PRIMARY KEY,
    EmpName VARCHAR(20) NOT NULL,
    Dept    VARCHAR(20) NOT NULL,
    Salary  INT         NOT NULL
);

INSERT INTO Employees (EmpId, EmpName, Dept, Salary) VALUES
 (1, 'Asha',  'IT',      90000), (2, 'Ravi',  'IT',      70000),
 (3, 'Meena', 'IT',      80000), (7, 'Tara',  'IT',      60000),
 (4, 'Karan', 'HR',      50000), (5, 'Divya', 'HR',      65000),
 (8, 'Neel',  'HR',      58000), (9, 'Isha',  'HR',      61000),
 (6, 'Sam',   'Finance', 72000);

-- ============================================
-- SOLUTION 1: PERCENTILE_CONT (window form, then DISTINCT to get one row per Dept)
-- ============================================
SELECT DISTINCT
    Dept,
    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY Salary) OVER (PARTITION BY Dept) AS MedianSalary
FROM Employees
ORDER BY Dept;

-- ============================================
-- SOLUTION 2: ROW_NUMBER + COUNT (portable)
-- ============================================
WITH Ranked AS (
    SELECT Dept, Salary,
           ROW_NUMBER() OVER (PARTITION BY Dept ORDER BY Salary) AS rn,
           COUNT(*)     OVER (PARTITION BY Dept)                 AS cnt
    FROM Employees
)
SELECT Dept, CAST(AVG(Salary * 1.0) AS DECIMAL(10,1)) AS MedianSalary
FROM Ranked
WHERE rn IN ((cnt + 1) / 2, (cnt + 2) / 2)    -- integer division: odd cnt -> same row twice, even cnt -> two middle rows
GROUP BY Dept
ORDER BY Dept;

-- EXPECTED OUTPUT (result derived from equivalent queries on PostgreSQL (PGlite); Solution 1 is not executed on SQL Server):
-- Dept    | MedianSalary
-- Finance | 72000.0
-- HR      | 59500.0       -- sorted 50000, 58000, 61000, 65000 -> (58000 + 61000) / 2
-- IT      | 75000.0       -- sorted 60000, 70000, 80000, 90000 -> (70000 + 80000) / 2
-- (Solution 1 returns the value as FLOAT: 72000, 59500, 75000)
-- Note the AVG salary of HR is 58500, so mean != median.
```

---

## 🔍 Why This Works (3 lines max)
PERCENTILE_CONT(0.5) interpolates at position 0.5*(n-1) in the sorted partition, which is exactly the median for both odd and even counts. In the manual method `(cnt+1)/2` and `(cnt+2)/2` use integer division to pick one row when cnt is odd (e.g. 3 -> 2 and 2) and the two middle rows when cnt is even (e.g. 4 -> 2 and 3), and AVG merges them. DISTINCT is needed because the window form returns the median on every row.
हिंदी: Odd count पर बीच की एक row, even पर दो rows का average। Integer division (cnt+1)/2 और (cnt+2)/2 यही काम करता है।

---

## ⚡ Alternative Solution

```sql
-- Aggregate-style median with no window: the "two-sided TOP" trick
SELECT d.Dept,
       (  (SELECT MAX(Salary) FROM (SELECT TOP (50) PERCENT Salary FROM Employees e WHERE e.Dept = d.Dept ORDER BY Salary)      AS lo)
        + (SELECT MIN(Salary) FROM (SELECT TOP (50) PERCENT Salary FROM Employees e WHERE e.Dept = d.Dept ORDER BY Salary DESC) AS hi)
       ) / 2.0 AS MedianSalary
FROM (SELECT DISTINCT Dept FROM Employees) AS d;
-- Classic pre-2012 trick; TOP 50 PERCENT rounds up the row count, so odd counts give the same row on both sides.
-- Hand-checked on the sample: Finance 72000, HR 59500, IT 75000. Not executed on SQL Server.

-- PostgreSQL: SELECT dept, PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY salary) FROM employees GROUP BY dept;
```

---

## ⚠️ Common Mistake

```sql
-- ❌ Using AVG as "median": HR average is 58500, median is 59500 — outliers skew the mean
SELECT Dept, AVG(Salary) FROM Employees GROUP BY Dept;

-- ❌ Picking only the row at (cnt/2): wrong for even counts (returns 61000 for HR instead of 59500)
-- ❌ GROUP BY Dept with PERCENTILE_CONT in T-SQL -> not an aggregate; it needs OVER (PARTITION BY Dept)
-- ❌ Forgetting DISTINCT (or TOP 1 per group) and returning one duplicate row per employee
-- ❌ Using AVG(Salary) of INT columns for the two middle rows: integer division truncates 59500.5 -> 59500
```

---

## 🎯 Interview Tip (1 line)
Say: "There is no MEDIAN in T-SQL, so I use PERCENTILE_CONT(0.5) for readability and keep the ROW_NUMBER/COUNT version for portability. On a big table I check the plan since PERCENTILE_CONT sorts and spools per partition, and I would pre-aggregate or index on (Dept, Salary) if it is hot."

---

## 🔗 Related Questions
→ Q060 (PERCENT_RANK, CUME_DIST, PERCENTILE_CONT) | Q056 (ROW_NUMBER, RANK, DENSE_RANK, NTILE) | Q045 (Nth highest salary — 5 ways) | Q062 (Aggregate functions with NULL)
