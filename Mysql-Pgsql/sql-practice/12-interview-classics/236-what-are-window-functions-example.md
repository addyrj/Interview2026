---

# Q236. What Are Window Functions? Give Example
# Category: Interview Classics
# Difficulty: ⭐⭐ Medium
# DB: Both (MySQL 8.0+ | PostgreSQL)

---

## ❓ Question
What is a window function, and how is it different from GROUP BY? Show: per-department average next to each employee, ranking within a department, a running total, previous-row comparison (LAG) and a moving average.

---

## 💡 Quick Concept (2 lines only)
A window function computes over a set of related rows (the "window", defined by OVER) but keeps every input row, unlike GROUP BY which collapses rows. Syntax: func() OVER (PARTITION BY ... ORDER BY ... ROWS/RANGE frame).
हिंदी: Window function हर row रखता है और साथ में group-level calculation देता है; GROUP BY rows को collapse कर देता है।

---

## ✅ Answer / Solution

```sql
-- ============================================
-- SETUP (run this first) — same on MySQL 8+ and PostgreSQL
-- ============================================

CREATE TABLE employees (
  id        INT PRIMARY KEY,
  name      VARCHAR(100),
  dept      VARCHAR(50),
  salary    DECIMAL(10,2),
  hire_date DATE
);

INSERT INTO employees VALUES
  (1, 'Alice', 'Engineering', 120000, '2020-01-15'),
  (2, 'Bob',   'Engineering',  95000, '2021-03-20'),
  (3, 'Carol', 'Engineering',  95000, '2019-07-01'),  -- tied with Bob
  (4, 'Dave',  'Sales',        90000, '2020-02-28'),
  (5, 'Eve',   'Sales',        75000, '2021-08-15'),
  (6, 'Frank', 'Sales',        60000, '2022-04-10');

-- ============================================
-- SOLUTION
-- ============================================

-- Step 1: GROUP BY collapses rows -> one row per dept (employee detail is lost)
SELECT dept, COUNT(*) AS emp_count, ROUND(AVG(salary), 2) AS avg_salary
FROM employees GROUP BY dept ORDER BY dept;

-- Result:
-- dept        | emp_count | avg_salary
-- Engineering | 3         | 103333.33
-- Sales       | 3         | 75000.00

-- Step 2: window AVG keeps all 6 rows AND shows the dept average beside each
SELECT name, dept, salary,
       ROUND(AVG(salary) OVER (PARTITION BY dept), 2)          AS dept_avg,
       ROUND(salary - AVG(salary) OVER (PARTITION BY dept), 2) AS diff_from_avg
FROM employees ORDER BY dept, id;

-- Result:
-- name  | dept        | salary    | dept_avg  | diff_from_avg
-- Alice | Engineering | 120000.00 | 103333.33 | 16666.67
-- Bob   | Engineering |  95000.00 | 103333.33 | -8333.33
-- Carol | Engineering |  95000.00 | 103333.33 | -8333.33
-- Dave  | Sales       |  90000.00 |  75000.00 | 15000.00
-- Eve   | Sales       |  75000.00 |  75000.00 |     0.00
-- Frank | Sales       |  60000.00 |  75000.00 | -15000.00

-- Step 3: ranking functions (named window w reused 3 times)
SELECT name, dept, salary,
       ROW_NUMBER() OVER w AS row_num,
       RANK()       OVER w AS rnk,
       DENSE_RANK() OVER w AS dense_rnk
FROM employees
WINDOW w AS (PARTITION BY dept ORDER BY salary DESC)
ORDER BY dept, salary DESC, id;

-- Result (Bob/Carol tie: row_num differs, rank stays 2):
-- name  | dept        | salary    | row_num | rnk | dense_rnk
-- Alice | Engineering | 120000.00 | 1       | 1   | 1
-- Bob   | Engineering |  95000.00 | 2       | 2   | 2
-- Carol | Engineering |  95000.00 | 3       | 2   | 2
-- Dave  | Sales       |  90000.00 | 1       | 1   | 1
-- Eve   | Sales       |  75000.00 | 2       | 2   | 2
-- Frank | Sales       |  60000.00 | 3       | 3   | 3

-- Step 4: running total (ORDER BY inside OVER makes it cumulative)
SELECT name, hire_date, salary,
       SUM(salary) OVER (ORDER BY hire_date, id) AS running_payroll
FROM employees ORDER BY hire_date, id;

-- Result:
-- name  | hire_date  | salary    | running_payroll
-- Carol | 2019-07-01 |  95000.00 |  95000.00
-- Alice | 2020-01-15 | 120000.00 | 215000.00
-- Dave  | 2020-02-28 |  90000.00 | 305000.00
-- Bob   | 2021-03-20 |  95000.00 | 400000.00
-- Eve   | 2021-08-15 |  75000.00 | 475000.00
-- Frank | 2022-04-10 |  60000.00 | 535000.00

-- Step 5: LAG = value from the previous row in window order
SELECT name, hire_date, salary,
       LAG(salary) OVER (ORDER BY hire_date, id)          AS prev_hire_salary,
       salary - LAG(salary) OVER (ORDER BY hire_date, id) AS salary_change
FROM employees ORDER BY hire_date, id;

-- Result:
-- name  | hire_date  | salary    | prev_hire_salary | salary_change
-- Carol | 2019-07-01 |  95000.00 | NULL             | NULL
-- Alice | 2020-01-15 | 120000.00 |  95000.00        |  25000.00
-- Dave  | 2020-02-28 |  90000.00 | 120000.00        | -30000.00
-- Bob   | 2021-03-20 |  95000.00 |  90000.00        |   5000.00
-- Eve   | 2021-08-15 |  75000.00 |  95000.00        | -20000.00
-- Frank | 2022-04-10 |  60000.00 |  75000.00        | -15000.00

-- Step 6: explicit frame = moving average of current + 1 previous row
SELECT name, hire_date, salary,
       ROUND(AVG(salary) OVER (ORDER BY hire_date, id
             ROWS BETWEEN 1 PRECEDING AND CURRENT ROW), 2) AS moving_avg_2
FROM employees ORDER BY hire_date, id;

-- Result: Carol 95000.00 | Alice 107500.00 | Dave 105000.00 | Bob 92500.00 | Eve 85000.00 | Frank 67500.00

-- Verified: all queries above ran on MySQL 9.1.0 and PostgreSQL (PGlite) with identical numbers.
-- Note: PostgreSQL returns hire_date as a date; the values shown are the same.
```

---

## 🔍 Why This Works (3 lines max)
OVER defines the window per row: PARTITION BY splits into groups, ORDER BY sets the sequence, and the frame (ROWS BETWEEN) limits which rows feed the aggregate. Without ORDER BY the aggregate covers the whole partition; with ORDER BY the default frame is "start of partition up to current row" (running total).
हिंदी: PARTITION BY = group, ORDER BY = क्रम, frame = कौन सी rows गिननी हैं; row हर बार बची रहती है।

---

## ⚡ Alternative Solution

```sql
-- Without window functions: correlated subquery / join (slower, re-scans the table per row)
SELECT e.name, e.dept, e.salary, d.avg_salary
FROM employees e
JOIN (SELECT dept, AVG(salary) AS avg_salary FROM employees GROUP BY dept) d
  ON d.dept = e.dept;

-- MySQL vs PgSQL differences:
-- * MySQL window functions need 8.0+ (5.7 has none). PostgreSQL has them since 8.4.
-- * "change" is a RESERVED word in MySQL (alias `change` gave a syntax error) -> avoid or backtick it.
-- * AVG() on DECIMAL: MySQL gives 6 decimals, PostgreSQL gives ~16 -> wrap in ROUND() for identical output.
-- * PostgreSQL also supports FILTER (WHERE ...) on window aggregates, GROUPS frames and EXCLUDE clauses.
```

---

## ⚠️ Common Mistake

```sql
-- ❌ Window function in WHERE (evaluated after WHERE, so it is not allowed)
SELECT name, salary FROM employees WHERE ROW_NUMBER() OVER (ORDER BY salary) <= 2;
-- MySQL:      ERROR 3593: You cannot use the window function 'row_number' in this context.
-- PostgreSQL: ERROR: window functions are not allowed in WHERE

-- ✅ Wrap in a subquery/CTE, then filter
SELECT name, salary
FROM (SELECT name, salary, ROW_NUMBER() OVER (ORDER BY salary) AS rn FROM employees) t
WHERE rn <= 2;

-- ❌ ORDER BY inside OVER without a tiebreaker -> non-deterministic ROW_NUMBER for ties (Bob/Carol)
-- ✅ Add a unique column: ORDER BY salary DESC, id
```

---

## 🎯 Interview Tip (1 line)
Say: "Window functions add per-row analytics without collapsing rows; execution order is FROM, WHERE, GROUP BY, HAVING, window, SELECT, ORDER BY, so I filter on a window result via a CTE, and I always give ROW_NUMBER a unique tiebreaker and an explicit frame (ROWS vs the default RANGE) for running totals."

---

## 🔗 Related Questions
→ Q066 (ROW_NUMBER vs RANK vs DENSE_RANK) | Q067 (LEAD/LAG) | Q075 (Top N per group) | Q240 (Consecutive dates)
