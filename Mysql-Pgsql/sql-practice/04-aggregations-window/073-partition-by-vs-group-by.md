---

# Q073. PARTITION BY vs GROUP BY — Difference
# Category: Aggregations & Window Functions
# Difficulty: ⭐⭐ Medium
# DB: Both (MySQL 8.0+ | PostgreSQL) — verified on MySQL 9.1 and PGlite (PostgreSQL)

---

## ❓ Question
What is the difference between GROUP BY and a window `PARTITION BY`? List employees earning more than their department average.

---

## 💡 Quick Concept (2 lines only)
GROUP BY collapses each group into ONE row; PARTITION BY computes the aggregate per group but KEEPS every original row.
हिंदी: GROUP BY rows को घटाकर एक कर देता है, PARTITION BY सारी rows रखकर साथ में aggregate दिखाता है।

---

## ✅ Answer / Solution

```sql
-- ============================================
-- SETUP (run this first)
-- ============================================

CREATE TABLE employees (
  id     INT PRIMARY KEY,
  name   VARCHAR(50),
  dept   VARCHAR(30),
  salary INT
);

INSERT INTO employees VALUES
 (1,'Asha','Eng',120000),(2,'Bilal','Eng',95000),(3,'Chitra','Eng',80000),
 (4,'Dev','Sales',90000),(5,'Esha','Sales',60000);

-- ============================================
-- SOLUTION
-- ============================================

-- GROUP BY: 2 rows out (one per dept)
SELECT dept, COUNT(*) AS headcount, AVG(salary) AS avg_salary
FROM employees GROUP BY dept ORDER BY dept;
-- dept  | headcount | avg_salary
-- Eng   | 3         | 98333.33
-- Sales | 2         | 75000.00

-- PARTITION BY: 5 rows out (every employee kept), aggregate beside each row
SELECT name, dept, salary,
       COUNT(*) OVER (PARTITION BY dept) AS headcount,
       AVG(salary) OVER (PARTITION BY dept) AS avg_salary,
       salary - AVG(salary) OVER (PARTITION BY dept) AS diff_from_avg
FROM employees ORDER BY dept, id;
-- name   | dept  | salary | headcount | avg_salary | diff_from_avg
-- Asha   | Eng   | 120000 | 3         | 98333.33   |  21666.67
-- Bilal  | Eng   |  95000 | 3         | 98333.33   |  -3333.33
-- Chitra | Eng   |  80000 | 3         | 98333.33   | -18333.33
-- Dev    | Sales |  90000 | 2         | 75000.00   |  15000.00
-- Esha   | Sales |  60000 | 2         | 75000.00   | -15000.00
-- (MySQL prints 4 decimals, PostgreSQL 12; values shown rounded to 2)

-- Employees above their dept average: wrap the window in a subquery (window results can't go in WHERE)
SELECT name, dept, salary
FROM (SELECT name, dept, salary, AVG(salary) OVER (PARTITION BY dept) AS avg_salary FROM employees) t
WHERE salary > avg_salary ORDER BY dept;
-- Asha | Eng | 120000
-- Dev  | Sales | 90000
```

---

## 🔍 Why This Works (3 lines max)
Window functions are evaluated after WHERE/GROUP BY/HAVING and never reduce the row count, so detail and aggregate sit side by side. Because they run late, they can only appear in SELECT and ORDER BY.
हिंदी: Window function बाद में चलता है और rows नहीं घटाता, इसीलिए WHERE में नहीं लिख सकते।

---

## ⚡ Alternative Solution

```sql
-- Same as PARTITION BY but with GROUP BY + JOIN (older style, two passes)
SELECT e.name, e.dept, e.salary, d.avg_salary
FROM employees e
JOIN (SELECT dept, AVG(salary) AS avg_salary FROM employees GROUP BY dept) d ON d.dept = e.dept
ORDER BY e.id;

-- Window + GROUP BY together is legal: GROUP BY runs first, window runs on its output
SELECT dept, name, SUM(salary) OVER (PARTITION BY dept) AS dept_total
FROM employees GROUP BY dept, name, salary ORDER BY dept, name;
-- Eng 295000 x3, Sales 150000 x2

-- MySQL vs PgSQL: identical behaviour.
```

---

## ⚠️ Common Mistake

```sql
-- ❌ Wrong: window function in WHERE
SELECT name FROM employees WHERE salary > AVG(salary) OVER (PARTITION BY dept);
-- MySQL: ERROR 3593 You cannot use the window function 'avg' in this context
-- PgSQL: ERROR: window functions are not allowed in WHERE
-- ✅ Wrap in a subquery/CTE as shown above

-- ❌ Wrong: selecting a non-grouped column with GROUP BY
SELECT name, salary FROM employees GROUP BY dept;
-- MySQL 9.1 (ONLY_FULL_GROUP_BY): ERROR 1055; PgSQL: ERROR column "employees.name" must appear in the GROUP BY clause
```

---

## 🎯 Interview Tip (1 line)
Say: "GROUP BY changes the grain of the result; PARTITION BY keeps the grain and adds an aggregate column - so for 'compare each row to its group' I use a window, for 'one row per group' I use GROUP BY."

---

## 🔗 Related Questions
→ Q061 (HAVING vs WHERE) | Q072 (percent of total) | Q075 (top N per group)
