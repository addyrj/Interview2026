---

# Q041. INNER JOIN Output Question
# Category: Joins
# Difficulty: ⭐ Easy
# DB: Both (MySQL 8.0+ | PostgreSQL)

---

## ❓ Question
Given `employees` (7 rows, one with NULL `dept_id`, one with a `dept_id` that does not exist) and `departments` (4 rows, two with no employees), how many rows and which rows does `employees INNER JOIN departments ON dept_id` return? What changes if you forget the join condition?

---

## 💡 Quick Concept (2 lines only)
INNER JOIN returns only rows where the ON condition is TRUE in both tables; unmatched rows on either side and NULL keys disappear. A missing condition produces a Cartesian product (rows A x rows B).
हिंदी: INNER JOIN सिर्फ matching rows देता है; NULL या unmatched rows गायब; condition भूले तो Cartesian product।

---

## ✅ Answer / Solution

```sql
-- ============================================
-- SETUP (run this first) — same SQL for MySQL and PostgreSQL
-- ============================================

CREATE TABLE departments (
  dept_id   INT PRIMARY KEY,
  dept_name VARCHAR(50) NOT NULL
);
CREATE TABLE employees (
  emp_id     INT PRIMARY KEY,
  emp_name   VARCHAR(50) NOT NULL,
  dept_id    INT NULL,              -- no FK on purpose, so we can have orphans
  salary     INT NOT NULL,
  manager_id INT NULL
);

INSERT INTO departments VALUES (10,'Engineering'),(20,'Sales'),(30,'HR'),(40,'Legal');
INSERT INTO employees VALUES
  (1,'Asha', 10,150000,NULL),
  (2,'Bilal',10,120000,1),
  (3,'Chen', 20, 90000,1),
  (4,'Divya',20, 85000,3),
  (5,'Emil', NULL,70000,3),   -- NULL dept
  (6,'Farah',99, 65000,2),    -- dept 99 doesn't exist
  (7,'Gopal',10,110000,2);

-- ============================================
-- SOLUTION
-- ============================================

-- Step 1: inner join on the key
SELECT e.emp_name, d.dept_name
FROM employees e
INNER JOIN departments d ON e.dept_id = d.dept_id
ORDER BY e.emp_id;

-- Step 2: counts - inner join vs old comma syntax vs no condition
SELECT COUNT(*) AS cnt FROM employees e INNER JOIN departments d ON e.dept_id = d.dept_id;   -- 5
SELECT COUNT(*) AS cnt FROM employees e, departments d WHERE e.dept_id = d.dept_id;           -- 5 (same, old syntax)
SELECT COUNT(*) AS cross_rows FROM employees e CROSS JOIN departments d;                      -- 7 x 4 = 28

-- Step 3: aggregate over the join
SELECT d.dept_name, COUNT(*) AS headcount, SUM(e.salary) AS payroll
FROM employees e JOIN departments d ON d.dept_id = e.dept_id
GROUP BY d.dept_name ORDER BY d.dept_name;

-- ============================================
-- EXPECTED OUTPUT (identical on MySQL 9.1 and PostgreSQL 18)
-- ============================================

-- Step 1:
-- emp_name | dept_name
-- Asha     | Engineering
-- Bilal    | Engineering
-- Chen     | Sales
-- Divya    | Sales
-- Gopal    | Engineering
--
-- Step 2:  cnt = 5,  cnt = 5,  cross_rows = 28
--
-- Step 3:
-- dept_name   | headcount | payroll
-- Engineering | 3         | 380000
-- Sales       | 2         | 175000
```

---

## 🔍 Why This Works (3 lines max)
Emil (NULL dept) never matches because `NULL = anything` is unknown, and Farah (dept 99) has no partner, so both vanish; HR and Legal vanish for the same reason on the other side. Output rows = number of matching pairs (5).
हिंदी: NULL = कुछ भी हमेशा unknown होता है, इसलिए Emil match नहीं होता; Farah का dept 99 मौजूद ही नहीं।

---

## ⚡ Alternative Solution

```sql
-- USING shortcut when the column names are identical (MySQL + PgSQL):
SELECT emp_name, dept_name FROM employees JOIN departments USING (dept_id);   -- needs same column name in both tables

-- NATURAL JOIN exists but is dangerous: it silently joins on ALL same-named columns.
-- Join on NULL keys needs explicit handling (verified: still 5 rows, nothing extra matches since departments has no NULL key):
SELECT COUNT(*) FROM employees e
INNER JOIN departments d ON e.dept_id = d.dept_id OR (e.dept_id IS NULL AND d.dept_id IS NULL);   -- 5

-- Syntax differences: none for INNER JOIN. MySQL permits `JOIN` without ON (acts like CROSS JOIN);
-- PostgreSQL requires ON/USING for INNER JOIN and errors otherwise (stated from docs; not run).
```

---

## ⚠️ Common Mistake
```sql
-- ❌ Wrong: forgetting the join condition -> 28 rows instead of 5, and SUM() is wildly inflated
SELECT COUNT(*) FROM employees e, departments d;
-- ❌ Wrong: expecting Emil / Farah in an inner-join report; they were silently dropped
-- ✅ Correct: use LEFT JOIN from employees if you must keep every employee (see Q042)
-- ❌ Wrong: putting filters on the joined table in WHERE and assuming it is the same as ON for LEFT joins (it's fine for INNER, not for LEFT)
```

---

## 🎯 Interview Tip (1 line)
Say: "For an INNER JOIN I count the expected rows first: matching pairs only, NULL keys never match, and a one-to-many key multiplies rows — so I always sanity-check COUNT(*) before and after a join to catch fan-out and silently dropped orphans."

---

## 🔗 Related Questions
→ Q042 (LEFT JOIN with NULL detection) | Q043 (RIGHT JOIN) | Q044 (FULL OUTER JOIN) | Q045 (SELF JOIN)
