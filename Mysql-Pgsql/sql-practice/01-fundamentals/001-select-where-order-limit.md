---

# Q001. SELECT with WHERE, ORDER BY, LIMIT
# Category: Fundamentals
# Difficulty: ⭐ Easy
# DB: Both (MySQL + PostgreSQL)

---

## ❓ Question
From an `employees` table, return the top 3 highest-paid people in Engineering or Sales who earn at least 90,000. Break salary ties deterministically, then show the "page 2" query (skip 2 rows, take 3) and explain the logical execution order of the clauses.

---

## 💡 Quick Concept (2 lines only)
Logical order is FROM → WHERE → GROUP BY → HAVING → SELECT → ORDER BY → LIMIT, so WHERE cannot see SELECT aliases but ORDER BY can. LIMIT without a total ORDER BY returns an arbitrary subset.
हिंदी: क्रम है FROM → WHERE → SELECT → ORDER BY → LIMIT; WHERE में alias नहीं चलता, और बिना ORDER BY के LIMIT random rows देता है।

---

## ✅ Answer / Solution

```sql
-- ============================================
-- SETUP (run this first)
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
  (4, 'Dave',  'Sales',        90000, '2022-05-10'),
  (5, 'Eve',   'Sales',        75000, '2023-01-05'),
  (6, 'Frank', 'Marketing',    80000, '2020-02-28'),
  (7, 'Grace', 'Marketing',    70000, '2021-08-15'),
  (8, 'Heidi', 'Support',      55000, '2020-11-30');

-- ============================================
-- SOLUTION
-- ============================================

-- Step 1: WHERE filters rows (dept list + salary floor)
-- Step 2: ORDER BY sorts; "id" is the tiebreaker so Bob/Carol order is stable
-- Step 3: LIMIT keeps only the first 3 sorted rows

SELECT id, name, dept, salary
FROM employees
WHERE dept IN ('Engineering', 'Sales')
  AND salary >= 90000
ORDER BY salary DESC, id ASC      -- id ASC = deterministic tiebreaker
LIMIT 3;

-- Page 2 style (skip 2, take 3) - same syntax in MySQL and PostgreSQL:
SELECT id, name, salary
FROM employees
ORDER BY salary DESC, id ASC
LIMIT 3 OFFSET 2;

-- ============================================
-- EXPECTED OUTPUT (identical on MySQL 9.1.0 and PGlite/PostgreSQL)
-- ============================================

-- Query 1:
-- id | name  | dept        | salary
-- ---+-------+-------------+-----------
--  1 | Alice | Engineering | 120000.00
--  2 | Bob   | Engineering |  95000.00
--  3 | Carol | Engineering |  95000.00
--
-- Query 2 (OFFSET 2):
-- id | name  | salary
-- ---+-------+----------
--  3 | Carol | 95000.00
--  4 | Dave  | 90000.00
--  6 | Frank | 80000.00
```

---

## 🔍 Why This Works (3 lines max)
WHERE trims rows before sorting, so the sort works on fewer rows. ORDER BY with a unique tiebreaker (`id`) gives a total order, so LIMIT/OFFSET is repeatable. ORDER BY runs after SELECT, which is why it can use aliases.
हिंदी: WHERE पहले rows छाँटता है, फिर ORDER BY unique tiebreaker के साथ sort और अंत में LIMIT।

---

## ⚡ Alternative Solution

```sql
-- MySQL-only shorthand: LIMIT offset, count   (PostgreSQL REJECTS this)
SELECT name, salary FROM employees ORDER BY salary DESC, id LIMIT 2, 3;
-- MySQL 9.1.0: works  | PGlite: ERROR: LIMIT #,# syntax is not supported

-- ANSI standard (PostgreSQL 8.4+ ; MySQL 9.1.0 -> syntax error on FETCH FIRST):
SELECT name FROM employees ORDER BY hire_date DESC FETCH FIRST 2 ROWS ONLY;
-- PGlite output: Eve, Dave.   MySQL: ERROR 1064 near 'FETCH FIRST'

-- Portable form that works on both: LIMIT n OFFSET m
```

---

## ⚠️ Common Mistake

```sql
-- ❌ Wrong: using a SELECT alias in WHERE
SELECT name, salary AS pay FROM employees WHERE pay > 90000;
-- MySQL:      ERROR 1054: Unknown column 'pay' in 'where clause'
-- PostgreSQL: ERROR: column "pay" does not exist
-- ✅ Repeat the expression: WHERE salary > 90000   (or wrap in a subquery/CTE)

-- ❌ Wrong: LIMIT without a total ORDER BY / tiebreaker
SELECT name, salary FROM employees ORDER BY salary DESC LIMIT 3;
-- Bob and Carol both earn 95000. In my PGlite run the order was Alice, Carol, Bob;
-- MySQL returned Alice, Bob, Carol. Tie order is NOT guaranteed -> pages can overlap/skip rows.
-- ✅ ORDER BY salary DESC, id ASC
```

---

## 🎯 Interview Tip (1 line)
Say: "LIMIT is only meaningful with a deterministic ORDER BY (add a unique tiebreaker), and for deep pages I switch from OFFSET to keyset pagination because OFFSET still reads and discards the skipped rows."

---

## 🔗 Related Questions
→ Q011 (Offset vs Keyset pagination) | Q012 (Keyset / cursor pagination) | Q007 (CASE WHEN) | Q075 (Top N per group)
