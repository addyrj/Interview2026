---

# Q055. Nth Highest Salary — Classic Interview Problem
# Category: Joins & Subqueries
# Difficulty: ⭐⭐ Medium
# DB: Both (MySQL + PostgreSQL)

---

## ❓ Question
Write a query to find the Nth highest salary from an employees table. Handle the case where N exceeds the number of distinct salaries. Show 4 different approaches.

---

## 💡 Quick Concept (2 lines only)
Classic problem tests knowledge of DENSE_RANK (handles ties), LIMIT/OFFSET (simple but fragile), and correlated subqueries (shows SQL fundamentals). DENSE_RANK is the best answer — handles ties + works for any N.
हिंदी: DENSE_RANK सबसे अच्छा approach है — ties handle करता है, कोई भी N के लिए काम करता है।

---

## ✅ Answer / Solution

```sql
-- ============================================
-- SETUP
-- ============================================

CREATE TABLE employees (
  id     INT PRIMARY KEY,
  name   VARCHAR(50),
  salary DECIMAL(10,2)
);

INSERT INTO employees VALUES
  (1, 'Alice', 90000),
  (2, 'Bob',   85000),
  (3, 'Carol', 85000),  -- tied with Bob!
  (4, 'Dave',  80000),
  (5, 'Eve',   75000);

-- Target: 2nd highest salary = 85000 (Bob AND Carol)

-- ============================================
-- APPROACH 1: DENSE_RANK (BEST — handles ties, scalable)
-- ============================================

-- Find 2nd highest:
SELECT DISTINCT salary
FROM (
  SELECT salary,
    DENSE_RANK() OVER (ORDER BY salary DESC) AS dr
  FROM employees
) ranked
WHERE dr = 2;

-- Output: 85000 ✅ (returns the value, not the row count)

-- Get the employees with that salary:
SELECT name, salary
FROM (
  SELECT name, salary,
    DENSE_RANK() OVER (ORDER BY salary DESC) AS dr
  FROM employees
) ranked
WHERE dr = 2;

-- Output:
-- Bob   | 85000
-- Carol | 85000
-- ← BOTH employees with 2nd highest salary returned! ✅

-- Generic N (use variable or parameter):
-- MySQL:
SET @N = 2;
SELECT name, salary
FROM (
  SELECT name, salary,
    DENSE_RANK() OVER (ORDER BY salary DESC) AS dr
  FROM employees
) ranked
WHERE dr = @N;

-- PgSQL:
SELECT name, salary
FROM (
  SELECT name, salary,
    DENSE_RANK() OVER (ORDER BY salary DESC) AS dr
  FROM employees
) ranked
WHERE dr = 2;  -- replace 2 with $1 for parameterized query

-- ============================================
-- APPROACH 2: LIMIT + OFFSET (SIMPLE, fragile with ties)
-- ============================================

-- 2nd highest distinct salary:
SELECT DISTINCT salary
FROM employees
ORDER BY salary DESC
LIMIT 1 OFFSET 1;   -- OFFSET N-1 for Nth highest

-- ⚠️ Problem: returns only one salary value
-- Bob and Carol both earn 85000 — this misses Carol!
-- Use only when you need the VALUE, not all employees with that salary:
SELECT name, salary
FROM employees
WHERE salary = (
  SELECT DISTINCT salary FROM employees ORDER BY salary DESC LIMIT 1 OFFSET 1
);
-- This correctly returns Bob AND Carol

-- Handle NULL (when N > distinct salaries):
SELECT IFNULL(
  (SELECT DISTINCT salary FROM employees ORDER BY salary DESC LIMIT 1 OFFSET 1),
  NULL
) AS second_highest;
-- Returns NULL if only 1 distinct salary exists

-- PgSQL equivalent:
SELECT salary FROM employees ORDER BY salary DESC LIMIT 1 OFFSET 1;

-- ============================================
-- APPROACH 3: CORRELATED SUBQUERY (Classic Interview Answer)
-- ============================================

-- 2nd highest (find salary where exactly 1 higher distinct salary exists):
SELECT MAX(salary) AS second_highest
FROM employees
WHERE salary < (SELECT MAX(salary) FROM employees);
-- Explanation:
-- Inner: MAX(salary) = 90000 (Alice)
-- Outer: MAX of salaries < 90000 = 85000 ✅

-- For Nth highest (correlated subquery approach):
SELECT MAX(salary) AS nth_highest
FROM employees
WHERE salary < ALL (
  SELECT DISTINCT salary
  FROM employees
  ORDER BY salary DESC
  LIMIT 1  -- replace 1 with N-1 for Nth highest
);
-- This is tricky to generalize to arbitrary N

-- Better generalization using COUNT:
-- Nth highest = salary where exactly (N-1) salaries are higher
SELECT DISTINCT salary
FROM employees e1
WHERE (N-1) = (
  SELECT COUNT(DISTINCT salary)
  FROM employees e2
  WHERE e2.salary > e1.salary
);
-- Replace (N-1) with the actual value, e.g., for N=2: WHERE 1 = COUNT(...)
-- O(n²) — slow on large tables! Use window function approach for production

-- Example for 2nd highest:
SELECT DISTINCT salary
FROM employees e1
WHERE 1 = (
  SELECT COUNT(DISTINCT salary)
  FROM employees e2
  WHERE e2.salary > e1.salary
);
-- Output: 85000 ✅

-- ============================================
-- APPROACH 4: EXCEPT / MINUS (Advanced)
-- ============================================

-- PgSQL (using EXCEPT):
-- Remove the top N-1 salaries, then take MAX
SELECT MAX(salary)
FROM employees
WHERE salary NOT IN (
  SELECT DISTINCT salary FROM employees ORDER BY salary DESC LIMIT 1
);
-- Removes Alice's 90000, then MAX of remaining = 85000 ✅

-- MySQL using subquery:
SELECT MAX(salary)
FROM employees
WHERE salary NOT IN (
  SELECT DISTINCT salary FROM (
    SELECT DISTINCT salary FROM employees ORDER BY salary DESC LIMIT 1  -- top N-1
  ) sub
);

-- ============================================
-- HANDLING EDGE CASES
-- ============================================

-- Edge case 1: N > distinct salaries → return NULL
SELECT salary
FROM (
  SELECT salary,
    DENSE_RANK() OVER (ORDER BY salary DESC) AS dr
  FROM employees
) r
WHERE dr = 10;  -- only 5 employees → returns empty result set (not NULL!)

-- Wrap to return NULL explicitly:
SELECT COALESCE(
  (SELECT DISTINCT salary FROM (
    SELECT salary, DENSE_RANK() OVER (ORDER BY salary DESC) AS dr
    FROM employees
  ) r WHERE dr = 10),
  NULL
) AS nth_highest;

-- Edge case 2: All employees same salary → 2nd highest doesn't exist
INSERT INTO employees VALUES (6, 'Frank', 90000);
-- Only distinct salary: 90000 → no 2nd highest → query returns empty/NULL ✅

-- Edge case 3: Negative or zero N → validate in application layer before query
```

---

## 🔍 Why This Works (3 lines max)
DENSE_RANK assigns consecutive ranks to distinct salary values — two employees with salary 85000 both get rank 2, and rank 3 is 80000 (not skipped). Filtering `WHERE dr = N` correctly returns all employees at that salary tier. For the classic interview question asking just the salary value, `LIMIT 1 OFFSET N-1` on `SELECT DISTINCT salary` is simpler but doesn't handle the "all employees at that salary" variant.
हिंदी: DENSE_RANK ties को same rank देता है, gaps नहीं होते। WHERE dr = N सभी employees उस salary tier पर return करता है।

---

## ⚡ Alternative Solution

```sql
-- Department-wise Nth highest (added complexity):
-- Top 2 salaries per department:
SELECT dept, name, salary
FROM (
  SELECT dept, name, salary,
    DENSE_RANK() OVER (PARTITION BY dept ORDER BY salary DESC) AS dr
  FROM employees
) ranked
WHERE dr <= 2;
-- Returns top 2 distinct salary tiers per department
-- All employees at those tiers included

-- Nth highest using MySQL variables (legacy — MySQL < 8.0):
SELECT salary FROM (
  SELECT salary, @rank := @rank + 1 AS pos
  FROM (SELECT DISTINCT salary FROM employees ORDER BY salary DESC) s,
       (SELECT @rank := 0) init
) ranked
WHERE pos = 2;
-- Variable-based ranking — avoid in MySQL 8.0+ (use window functions)
```

---

## ⚠️ Common Mistake

```sql
-- ❌ Wrong: RANK() instead of DENSE_RANK() for "Nth highest"
SELECT name, salary
FROM (
  SELECT name, salary, RANK() OVER (ORDER BY salary DESC) AS r
  FROM employees
) r WHERE r = 3;
-- If Bob and Carol both have RANK=2, then rank 3 is SKIPPED!
-- WHERE r = 3 returns NOTHING even though Dave has the 3rd distinct salary
-- DENSE_RANK: Dave gets dr=3 (no skip) → WHERE dr = 3 works ✅

-- ❌ Wrong: Missing DISTINCT in LIMIT/OFFSET approach
SELECT salary FROM employees ORDER BY salary DESC LIMIT 1 OFFSET 1;
-- Without DISTINCT: if two people earn 90000, OFFSET 1 gives 90000 again!
-- ✅ Fix: SELECT DISTINCT salary FROM employees ORDER BY salary DESC LIMIT 1 OFFSET 1

-- ❌ Wrong: Returning only the salary value when asked for employees
-- "Find the employee(s) with the 2nd highest salary"
-- Common mistake: stop at returning 85000 instead of Bob + Carol
-- ✅ Use DENSE_RANK or WHERE salary = (2nd highest value subquery)
```

---

## 🎯 Interview Tip (1 line)
Say: "I use DENSE_RANK for this — it handles ties correctly (Bob and Carol both earning 85000 are both rank 2), and rank N always exists if there are N distinct salary levels, unlike RANK which skips numbers. LIMIT OFFSET is simpler for just the value but misses tied employees."

---

## 🔗 Related Questions
→ Q066 (ROW_NUMBER vs RANK vs DENSE_RANK) | Q075 (top N per group) | Q067 (LEAD/LAG) | Q056 (running totals)
