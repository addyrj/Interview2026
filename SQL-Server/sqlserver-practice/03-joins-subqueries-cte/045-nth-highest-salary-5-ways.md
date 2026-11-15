---

# Q045. Nth Highest Salary — 5 Ways
# Category: Joins, Subqueries & CTEs
# Difficulty: ⭐⭐ Medium
# DB: SQL Server (MySQL: LIMIT/OFFSET instead of OFFSET FETCH; PostgreSQL: same as MySQL plus FETCH FIRST)

---

## ❓ Question
Find the 2nd and 3rd highest distinct salary in `Employees`, show how ties are handled, and also find the 2nd highest salary per department. Give 5 approaches and say which you would pick.

---

## 💡 Quick Concept (2 lines only)
First decide: "Nth highest distinct value" (DENSE_RANK) or "Nth row" (ROW_NUMBER)? With ties these differ. DENSE_RANK or `SELECT DISTINCT ... OFFSET FETCH` give the Nth distinct salary.
हिंदी: पहले तय करो — Nth distinct salary चाहिए या Nth row? Ties हों तो DENSE_RANK सही है, ROW_NUMBER गलत जवाब दे सकता है।

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
  (1, 'Asha',   'IT',    90000),
  (2, 'Bhavna', 'IT',    90000),   -- tied with Asha
  (3, 'Chetan', 'HR',    75000),
  (4, 'Deepak', 'IT',    60000),
  (5, 'Esha',   'HR',    60000),
  (6, 'Farhan', 'Sales', 50000),
  (7, 'Gita',   'Sales', 40000);

-- Distinct salaries, high to low: 90000, 75000, 60000, 50000, 40000

-- ============================================
-- WAY 1: DENSE_RANK  (best general answer, N = 2)
-- ============================================
SELECT DISTINCT Salary
FROM (
  SELECT Salary, DENSE_RANK() OVER (ORDER BY Salary DESC) AS dr
  FROM Employees
) AS x
WHERE dr = 2;
-- EXPECTED OUTPUT (derived on SQLite): 75000

-- ============================================
-- WAY 2: OFFSET ... FETCH on DISTINCT  (N = 3 -> skip 2)
-- ============================================
SELECT DISTINCT Salary
FROM Employees
ORDER BY Salary DESC
OFFSET 2 ROWS FETCH NEXT 1 ROWS ONLY;      -- OFFSET FETCH needs ORDER BY; SQL Server 2012+
-- EXPECTED OUTPUT (derived with LIMIT 1 OFFSET 2 on SQLite): 60000

-- ============================================
-- WAY 3: Nested MAX  (2nd highest only)
-- ============================================
SELECT MAX(Salary) AS SecondHighest
FROM Employees
WHERE Salary < (SELECT MAX(Salary) FROM Employees);
-- EXPECTED OUTPUT: 75000

-- ============================================
-- WAY 4: Correlated COUNT(DISTINCT)  (N = 3 -> 2 distinct salaries above it)
-- ============================================
SELECT DISTINCT e1.Salary
FROM Employees AS e1
WHERE 2 = (SELECT COUNT(DISTINCT e2.Salary) FROM Employees AS e2 WHERE e2.Salary > e1.Salary);
-- EXPECTED OUTPUT: 60000       (slow: O(n^2), but a classic)

-- ============================================
-- WAY 5: TOP twice  (N = 2; classic pre-2012 trick)
-- ============================================
SELECT TOP 1 Salary
FROM (SELECT DISTINCT TOP 2 Salary FROM Employees ORDER BY Salary DESC) AS t
ORDER BY Salary ASC;
-- EXPECTED OUTPUT: 75000

-- ============================================
-- BONUS: 2nd highest per department
-- ============================================
SELECT Dept, Name, Salary
FROM (
  SELECT Dept, Name, Salary,
         DENSE_RANK() OVER (PARTITION BY Dept ORDER BY Salary DESC) AS dr
  FROM Employees
) AS x
WHERE dr = 2
ORDER BY Dept, Name;
-- EXPECTED OUTPUT (derived on SQLite):
-- Dept  | Name   | Salary
-- HR    | Esha   | 60000
-- IT    | Deepak | 60000
-- Sales | Gita   | 40000

-- Results derived from equivalent queries on SQLite; not executed on SQL Server.
-- If N is larger than the number of distinct salaries, ways 1, 2 and 4 return zero rows (not NULL).
```

---

## 🔍 Why This Works (3 lines max)
DENSE_RANK gives equal salaries the same rank and never skips numbers, so `dr = N` is exactly the Nth distinct value. OFFSET FETCH works only after DISTINCT has collapsed ties. The correlated version literally counts how many distinct salaries are higher.
हिंदी: DENSE_RANK में ties को same rank मिलता है और gap नहीं आता, इसलिए `dr = N` = Nth distinct salary। OFFSET FETCH से पहले DISTINCT ज़रूरी है।

---

## ⚡ Alternative Solution

```sql
-- Return NULL instead of an empty result when N is too large (useful inside a procedure/function):
DECLARE @N INT = 10;

SELECT (
  SELECT DISTINCT Salary
  FROM Employees
  ORDER BY Salary DESC
  OFFSET @N - 1 ROWS FETCH NEXT 1 ROWS ONLY
) AS NthHighestSalary;     -- scalar subquery with no row -> NULL
-- OFFSET / FETCH accept variables and expressions in SQL Server, so N can be a parameter.
```

---

## ⚠️ Common Mistake

```sql
-- ❌ Wrong: ROW_NUMBER for "2nd highest salary"
SELECT Salary FROM (
  SELECT Salary, ROW_NUMBER() OVER (ORDER BY Salary DESC) AS rn FROM Employees) x
WHERE rn = 2;
-- rn = 2 is the other 90000 row (tie) -> returns 90000, not 75000.

-- ❌ Wrong: RANK for Nth distinct
-- RANK skips numbers after a tie: 90000, 90000 -> rank 1,1 then 75000 gets rank 3. "rank = 2" returns nothing.

-- ❌ Wrong: OFFSET FETCH without DISTINCT
-- OFFSET 1 skips one ROW, so with a tie at the top it returns 90000 again.

-- ❌ Wrong: TOP 1 ... ORDER BY without a tiebreaker when you need one specific employee
-- Add a deterministic tiebreaker (EmployeeId) or use WITH TIES deliberately.
```

---

## 🎯 Interview Tip (1 line)
Say: "First I clarify the tie semantics: Nth distinct salary or Nth employee. For distinct I use DENSE_RANK (and it extends to per-department with PARTITION BY); the OFFSET FETCH on DISTINCT is the shortest. I mention the correlated COUNT as the old way and why it does not scale, and I ask what should be returned when N exceeds the distinct count."

---

## 🔗 Related Questions
→ Q047 (top N per group) | Q056 (ROW_NUMBER, RANK, DENSE_RANK) | Q187 (second highest salary) | Q002 (TOP WITH TIES, OFFSET FETCH)
