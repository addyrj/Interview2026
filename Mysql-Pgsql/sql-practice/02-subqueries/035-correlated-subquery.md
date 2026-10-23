---

# Q035. Correlated Subquery — When to Use and When to Avoid
# Category: Subqueries
# Difficulty: ⭐⭐⭐ Hard
# DB: Both (MySQL + PostgreSQL)

---

## ❓ Question
What is a correlated subquery? Show real examples. When is it necessary vs when does it cause performance problems? How do you rewrite a correlated subquery using a JOIN or window function?

---

## 💡 Quick Concept (2 lines only)
A correlated subquery references columns from the outer query — it re-executes for EVERY row of the outer query. This is O(n²) and can be very slow. Often replaceable with a JOIN or window function that runs in O(n log n).
हिंदी: Correlated subquery = outer query के हर row के लिए inner query re-run होती है — O(n²)। JOIN या window function से O(n log n) में replace करो।

---

## ✅ Answer / Solution

```sql
-- ============================================
-- SETUP
-- ============================================

CREATE TABLE departments (
  id   INT PRIMARY KEY,
  name VARCHAR(100)
);

CREATE TABLE employees (
  id      INT PRIMARY KEY,
  name    VARCHAR(100),
  dept_id INT,
  salary  DECIMAL(10,2),
  hire_date DATE
);

INSERT INTO departments VALUES (1,'Engineering'), (2,'Sales'), (3,'Marketing');
INSERT INTO employees VALUES
  (1, 'Alice',  1, 120000, '2020-01-15'),
  (2, 'Bob',    1,  95000, '2021-03-20'),
  (3, 'Carol',  1,  85000, '2019-07-01'),
  (4, 'Dave',   2,  90000, '2020-02-28'),
  (5, 'Eve',    2,  75000, '2021-08-15'),
  (6, 'Frank',  3, 100000, '2019-05-01'),
  (7, 'Grace',  3,  80000, '2020-09-15');

-- ============================================
-- WHAT IS A CORRELATED SUBQUERY?
-- ============================================

-- Regular subquery (runs ONCE, independent):
SELECT * FROM employees
WHERE dept_id = (SELECT id FROM departments WHERE name = 'Engineering');
-- Inner query executes once, returns 1 → outer query filters by dept_id = 1

-- Correlated subquery (runs ONCE PER ROW — note reference to e.dept_id):
SELECT name, salary, dept_id
FROM employees e
WHERE salary > (
  SELECT AVG(salary)
  FROM employees
  WHERE dept_id = e.dept_id  -- ← references outer query's e.dept_id !
);
-- For EACH employee row: inner query runs with THAT employee's dept_id
-- "Find employees earning more than their department's average"
-- 7 employees → inner query runs 7 times!

-- Output:
-- Alice  | 120000 | 1  ← above Engineering average (100000)
-- Dave   | 90000  | 2  ← above Sales average (82500)
-- Frank  | 100000 | 3  ← above Marketing average (90000)

-- ============================================
-- PERFORMANCE PROBLEM
-- ============================================

-- With 100,000 employees: inner query runs 100,000 times = very slow!
-- EXPLAIN shows: "DEPENDENT SUBQUERY" in MySQL
-- PgSQL: shows nested loop with subplan

-- EXPLAIN SELECT name FROM employees e WHERE salary > (
--   SELECT AVG(salary) FROM employees WHERE dept_id = e.dept_id
-- );
-- MySQL: select_type = DEPENDENT SUBQUERY ← bad for large tables
-- PgSQL: SubPlan (correlated) in plan output

-- ============================================
-- REWRITE: JOIN + AGGREGATE (much faster!)
-- ============================================

-- Replace correlated subquery with JOIN to a pre-aggregated subquery:
SELECT e.name, e.salary, e.dept_id
FROM employees e
JOIN (
  SELECT dept_id, AVG(salary) AS avg_salary
  FROM employees
  GROUP BY dept_id           -- ← runs ONCE for all depts, not N times!
) dept_avg ON e.dept_id = dept_avg.dept_id
WHERE e.salary > dept_avg.avg_salary;

-- Now the inner query (GROUP BY) runs ONCE → all dept averages
-- Then one JOIN → O(n log n) instead of O(n²)

-- CTE version (same performance, more readable):
WITH dept_averages AS (
  SELECT dept_id, AVG(salary) AS avg_salary
  FROM employees GROUP BY dept_id
)
SELECT e.name, e.salary
FROM employees e
JOIN dept_averages da ON e.dept_id = da.dept_id
WHERE e.salary > da.avg_salary;

-- ============================================
-- REWRITE: WINDOW FUNCTION (cleanest)
-- ============================================

SELECT name, salary, dept_id
FROM (
  SELECT name, salary, dept_id,
    AVG(salary) OVER (PARTITION BY dept_id) AS dept_avg
  FROM employees
) WITH_AVG
WHERE salary > dept_avg;

-- Window function computes dept average in a SINGLE PASS
-- No subquery, no join — purest form. O(n log n) due to partitioning.

-- ============================================
-- WHEN CORRELATED SUBQUERY IS NECESSARY
-- ============================================

-- 1. EXISTS check (most common valid use case — stops at first match!):
SELECT d.name AS dept_name
FROM departments d
WHERE EXISTS (
  SELECT 1 FROM employees e
  WHERE e.dept_id = d.id
    AND e.salary > 100000         -- dept has at least one high earner
);
-- EXISTS is efficient: stops after finding FIRST matching row
-- Correlated here but NOT O(n²) in practice — index on (dept_id, salary) = fast

-- 2. NOT EXISTS (safest way to find non-matching records):
SELECT d.name
FROM departments d
WHERE NOT EXISTS (
  SELECT 1 FROM employees WHERE dept_id = d.id
);
-- Find departments with no employees
-- Equivalent to LEFT JOIN IS NULL but cleaner semantics

-- 3. Subquery in SELECT (scalar correlated):
SELECT
  d.name,
  (SELECT COUNT(*) FROM employees WHERE dept_id = d.id) AS emp_count,
  (SELECT AVG(salary) FROM employees WHERE dept_id = d.id) AS avg_salary
FROM departments d;
-- Correlated but each subquery is indexed (dept_id index) → may be OK for small tables
-- Becomes slow at scale — rewrite with LEFT JOIN + GROUP BY:
SELECT d.name, COUNT(e.id) AS emp_count, AVG(e.salary) AS avg_salary
FROM departments d
LEFT JOIN employees e ON d.id = e.dept_id
GROUP BY d.id, d.name;

-- 4. Update using correlation:
UPDATE employees e
SET salary = salary * 1.10
WHERE salary < (
  SELECT AVG(salary) FROM employees WHERE dept_id = e.dept_id
);
-- Give 10% raise to employees below their dept average
-- Correlated UPDATE — necessary here (each row uses its own dept's avg)

-- MySQL version (can't use same table in subquery for UPDATE):
UPDATE employees e
JOIN (
  SELECT dept_id, AVG(salary) AS avg_sal
  FROM employees GROUP BY dept_id
) dept_avg ON e.dept_id = dept_avg.dept_id
SET e.salary = e.salary * 1.10
WHERE e.salary < dept_avg.avg_sal;
-- JOIN-based UPDATE avoids the correlated subquery limitation in MySQL

-- ============================================
-- EXISTS vs IN — PERFORMANCE DIFFERENCE
-- ============================================

-- IN with subquery:
SELECT * FROM departments
WHERE id IN (SELECT dept_id FROM employees WHERE salary > 100000);
-- Subquery runs once, builds value list, then IN checks each dept

-- EXISTS:
SELECT * FROM departments d
WHERE EXISTS (SELECT 1 FROM employees WHERE dept_id = d.id AND salary > 100000);
-- Correlated but: stops at FIRST match per department!
-- If Engineering has 50 employees earning > 100K, EXISTS stops after finding 1

-- Performance:
-- IN: better when subquery result set is small
-- EXISTS: better when subquery result is large (stops early)
-- NOT IN with NULLs: dangerous! NULL in IN list → returns no rows
-- NOT EXISTS: safe with NULLs (preferred over NOT IN)

-- ============================================
-- LATERAL SUBQUERY (PgSQL — controlled correlation)
-- ============================================

-- LATERAL allows safe correlated subquery in FROM clause:
SELECT d.name, recent.name AS top_earner, recent.salary
FROM departments d
JOIN LATERAL (
  SELECT name, salary
  FROM employees
  WHERE dept_id = d.id
  ORDER BY salary DESC
  LIMIT 1
) recent ON true;

-- LATERAL = "for each department, run this subquery"
-- Uses index on (dept_id, salary DESC) → efficient
-- Better than correlated scalar subquery because:
--   1. Can return multiple columns
--   2. Can use LIMIT (correlated scalar can't)
--   3. More readable intent
```

---

## 🔍 Why This Works (3 lines max)
Correlated subqueries re-execute for every outer row — an `AVG()` correlated subquery on a 100K row table runs 100K inner queries. Rewriting with JOIN+GROUP BY computes all aggregates once then joins — O(n log n). The key exception is EXISTS/NOT EXISTS: the database can short-circuit after the first match, making it efficient even when correlated.
हिंदी: Correlated = N outer rows × M inner rows = O(n²)। JOIN+GROUP BY = once aggregate करो = O(n log n)। EXISTS = first match मिलते ही stop — efficient।

---

## ⚡ Alternative Solution

```sql
-- Window function for correlated UPDATE (PgSQL — elegant):
WITH salary_with_avg AS (
  SELECT id, salary,
    AVG(salary) OVER (PARTITION BY dept_id) AS dept_avg
  FROM employees
)
UPDATE employees
SET salary = salary * 1.10
FROM salary_with_avg
WHERE employees.id = salary_with_avg.id
  AND salary_with_avg.salary < salary_with_avg.dept_avg;
-- PgSQL: UPDATE ... FROM CTE — efficient, no correlated subquery
```

---

## ⚠️ Common Mistake

```sql
-- ❌ Wrong: Correlated subquery in WHERE for large tables
SELECT * FROM orders o
WHERE total > (
  SELECT AVG(total) FROM orders WHERE user_id = o.user_id
);
-- 1M orders, 100K users → 1M inner queries → extremely slow!
-- ✅ Fix: window function
SELECT * FROM (
  SELECT *, AVG(total) OVER (PARTITION BY user_id) AS user_avg
  FROM orders
) x WHERE total > user_avg;

-- ❌ Wrong: NOT IN with NULL values in subquery
SELECT * FROM departments
WHERE id NOT IN (SELECT dept_id FROM employees);
-- If ANY dept_id in employees is NULL: the IN list contains NULL
-- NOT IN with NULL → ALL rows fail! (NULL comparisons return UNKNOWN, not FALSE)
-- Returns empty set unexpectedly!
-- ✅ Fix: NOT EXISTS (handles NULLs correctly):
SELECT * FROM departments d
WHERE NOT EXISTS (SELECT 1 FROM employees WHERE dept_id = d.id);
-- OR: WHERE id NOT IN (SELECT dept_id FROM employees WHERE dept_id IS NOT NULL)

-- ❌ Wrong: Scalar correlated subquery returning multiple rows
SELECT name, (SELECT salary FROM employees WHERE dept_id = d.id LIMIT 1) AS sample
FROM departments d;
-- What if there are multiple employees? Without LIMIT: ERROR (subquery returns >1 row)
-- ✅ Always ensure scalar subquery returns exactly 1 row (use LIMIT 1 or aggregate)
```

---

## 🎯 Interview Tip (1 line)
Say: "Correlated subqueries re-execute for every outer row — O(n²) for large tables. I replace them with JOIN+GROUP BY (pre-aggregate once) or window functions (single pass). The valid exceptions are EXISTS/NOT EXISTS for membership checks (short-circuits on first match) and LATERAL JOIN in PostgreSQL for per-row subqueries with LIMIT."

---

## 🔗 Related Questions
→ Q075 (top N per group) | Q055 (Nth highest salary) | Q108 (N+1 problem) | Q086 (EXPLAIN output) | Q185 (LATERAL join)
