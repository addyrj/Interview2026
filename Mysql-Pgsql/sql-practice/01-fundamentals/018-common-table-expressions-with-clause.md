---

# Q018. Common Table Expressions (WITH Clause)
# Category: Fundamentals
# Difficulty: ⭐⭐ Medium
# DB: Both (MySQL 8.0+ | PostgreSQL)

---

## ❓ Question
What is a CTE (`WITH` clause)? Show a basic CTE, chained CTEs, reusing one CTE twice, a recursive CTE (org chart) and a CTE feeding an UPDATE. How does it differ from a subquery or a temp table?

---

## 💡 Quick Concept (2 lines only)
A CTE is a named, query-scoped result set defined with `WITH name AS (...)` that the main statement can reference like a table — it makes multi-step logic readable and lets you reference the same subquery more than once. It is not stored and not indexed.
हिंदी: CTE एक नाम वाला temporary result है जो सिर्फ उसी query में चलता है; पढ़ने में आसान और बार-बार use हो सकता है।

---

## ✅ Answer / Solution

```sql
-- ============================================
-- SETUP (run this first; works on MySQL 8.0+ and PostgreSQL)
-- ============================================

CREATE TABLE employees (
  id         INT PRIMARY KEY,
  name       VARCHAR(50),
  dept       VARCHAR(30),
  salary     DECIMAL(10,2),
  manager_id INT
);

INSERT INTO employees VALUES
  (1, 'Meera',  'Engineering', 150000, NULL),
  (2, 'Rohan',  'Engineering', 110000, 1),
  (3, 'Sneha',  'Engineering',  95000, 2),
  (4, 'Vikram', 'Sales',        80000, 1),
  (5, 'Anita',  'Sales',        60000, 4),
  (6, 'Karan',  'Sales',        55000, 4),
  (7, 'Divya',  'HR',           50000, 1);

-- ============================================
-- SOLUTION
-- ============================================

-- 1) Single CTE: employees earning more than their department average
WITH dept_avg AS (                                  -- Step 1: build per-dept average
  SELECT dept, AVG(salary) AS avg_salary FROM employees GROUP BY dept
)
SELECT e.name, e.dept, e.salary, ROUND(d.avg_salary, 2) AS dept_avg
FROM employees e
JOIN dept_avg d ON d.dept = e.dept                  -- Step 2: use it like a table
WHERE e.salary > d.avg_salary
ORDER BY e.id;
-- name   | dept        | salary    | dept_avg
-- Meera  | Engineering | 150000.00 | 118333.33
-- Vikram | Sales       | 80000.00  | 65000.00

-- 2) Chained CTEs: later CTEs can read earlier ones
WITH dept_stats AS (
  SELECT dept, COUNT(*) AS headcount, SUM(salary) AS payroll FROM employees GROUP BY dept
),
big_depts AS (
  SELECT dept, headcount, payroll FROM dept_stats WHERE headcount >= 3
)
SELECT * FROM big_depts ORDER BY dept;
-- dept        | headcount | payroll
-- Engineering | 3         | 355000.00
-- Sales       | 3         | 195000.00

-- 3) One CTE referenced twice (scalar total + rows) — no repeated subquery text
WITH totals AS (SELECT dept, SUM(salary) AS payroll FROM employees GROUP BY dept)
SELECT t.dept, t.payroll,
       ROUND(100 * t.payroll / (SELECT SUM(payroll) FROM totals), 1) AS pct
FROM totals t
ORDER BY t.payroll DESC;
-- dept        | payroll   | pct
-- Engineering | 355000.00 | 59.2
-- Sales       | 195000.00 | 32.5
-- HR          | 50000.00  | 8.3

-- 4) Recursive CTE: walk the manager hierarchy (anchor UNION ALL recursive step)
WITH RECURSIVE org AS (
  SELECT id, name, manager_id, 1 AS lvl FROM employees WHERE manager_id IS NULL   -- anchor
  UNION ALL
  SELECT e.id, e.name, e.manager_id, o.lvl + 1                                    -- recursive
  FROM employees e JOIN org o ON e.manager_id = o.id
)
SELECT id, name, lvl FROM org ORDER BY lvl, id;
-- id | name   | lvl
-- 1  | Meera  | 1
-- 2  | Rohan  | 2
-- 4  | Vikram | 2
-- 7  | Divya  | 2
-- 3  | Sneha  | 3
-- 5  | Anita  | 3
-- 6  | Karan  | 3

-- 5) CTE in front of UPDATE (works in both; id list comes from CTE)
WITH low_paid AS (SELECT id FROM employees WHERE salary < 56000)
UPDATE employees SET salary = salary * 1.10 WHERE id IN (SELECT id FROM low_paid);
SELECT id, salary FROM employees WHERE id IN (6, 7) ORDER BY id;
-- id | salary
-- 6  | 60500.00      <- Karan 55000 -> +10%
-- 7  | 55000.00      <- Divya 50000 -> +10%

-- ============================================
-- EXPECTED OUTPUT
-- ============================================
-- All five blocks produced exactly the results shown above on MySQL 9.1.0 and
-- PostgreSQL 18 (PGlite). Row order of non-ORDER-BY queries is never guaranteed.
```

---

## 🔍 Why This Works (3 lines max)
The optimizer treats the CTE as a named derived table scoped to the one statement; recursive CTEs repeatedly join the previous iteration's rows until no new rows appear. It improves readability and avoids duplicating subquery text — it is not automatically a performance boost.
हिंदी: CTE एक naming/readability tool है; recursive CTE बार-बार पिछली rows पर join करके hierarchy चलाता है।

---

## ⚡ Alternative Solution

```sql
-- Equivalent derived-table (subquery) form of example 1 — same plan in most cases:
SELECT e.name, e.dept, e.salary
FROM employees e
JOIN (SELECT dept, AVG(salary) AS avg_salary FROM employees GROUP BY dept) d
  ON d.dept = e.dept
WHERE e.salary > d.avg_salary;

-- PgSQL-only: control materialization (PG 12+). Run and accepted on PG 18:
WITH d AS MATERIALIZED     (SELECT dept, SUM(salary) AS s FROM employees GROUP BY dept) SELECT * FROM d;
WITH d AS NOT MATERIALIZED (SELECT dept, SUM(salary) AS s FROM employees GROUP BY dept) SELECT * FROM d;
-- Before PG 12 every CTE was an optimization fence (always materialized).

-- PgSQL-only: data-modifying CTE (INSERT/UPDATE/DELETE inside WITH) — see Q016.
-- MySQL: CTEs exist only from 8.0; MySQL 5.7 needs derived tables / temp tables.
-- Temp table is the better choice if you must reuse the result across many statements or index it.
```

---

## ⚠️ Common Mistake

```sql
-- ❌ Wrong: referencing a CTE in a later, separate statement
WITH dept_avg AS (SELECT dept, AVG(salary) a FROM employees GROUP BY dept)
SELECT * FROM dept_avg;
SELECT * FROM dept_avg;           -- ERROR: table doesn't exist — CTE lives for ONE statement only

-- ❌ Wrong: recursive CTE without termination (cyclic data) => infinite loop / hits recursion limit
-- ✅ Correct: add a depth guard:  WHERE o.lvl < 20   (MySQL: cte_max_recursion_depth = 1000 by default)

-- ❌ Wrong: assuming a CTE is cached/faster than a subquery. MySQL and PG>=12 usually inline it;
--    referenced twice, PG may compute it once (materialize) — check EXPLAIN.
```

---

## 🎯 Interview Tip (1 line)
Say: "I use CTEs for readability and recursion, but I know they're not a performance tool — PostgreSQL 12+ inlines single-use CTEs, MySQL treats them as derived tables, and I verify with EXPLAIN or use a temp table when I need indexing or reuse."

---

## 🔗 Related Questions
→ Q019 (Recursive CTE) | Q016 (RETURNING + data-modifying CTE) | Q075 (Top-N per group with window + CTE) | Q020 (UNION vs UNION ALL — used inside recursive CTEs)
