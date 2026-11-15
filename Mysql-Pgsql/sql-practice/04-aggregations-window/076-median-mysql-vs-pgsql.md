---

# Q076. Median Calculation in MySQL vs PgSQL
# Category: Aggregations & Window Functions
# Difficulty: ⭐⭐⭐ Hard
# DB: Both (MySQL 8.0+ window approach | PostgreSQL `PERCENTILE_CONT`) — verified on MySQL 9.1 and PGlite

---

## ❓ Question
Find the median salary overall and per department. PostgreSQL has a built-in; how do you do it in MySQL, which has no MEDIAN function?

---

## 💡 Quick Concept (2 lines only)
Median = middle value (average of the two middle values when the count is even). PostgreSQL: PERCENTILE_CONT(0.5) WITHIN GROUP; MySQL: ROW_NUMBER + COUNT, then average the middle row(s).
हिंदी: Median = बीच की value; PostgreSQL में PERCENTILE_CONT(0.5), MySQL में ROW_NUMBER से बीच की row(s) निकालो।

---

## ✅ Answer / Solution

```sql
-- ============================================
-- SETUP (run this first)
-- ============================================

CREATE TABLE emp_salary (
  id     INT PRIMARY KEY,
  dept   VARCHAR(30),
  salary INT
);

INSERT INTO emp_salary VALUES
 (1,'Eng',50000),(2,'Eng',60000),(3,'Eng',70000),(4,'Eng',100000),   -- 4 rows: even count
 (5,'Sales',40000),(6,'Sales',45000),(7,'Sales',90000);              -- 3 rows: odd count

-- ============================================
-- SOLUTION 1 - PostgreSQL
-- ============================================

SELECT dept,
       PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY salary) AS median_salary,  -- interpolates
       PERCENTILE_DISC(0.5) WITHIN GROUP (ORDER BY salary) AS median_disc     -- an actual value
FROM emp_salary GROUP BY dept ORDER BY dept;
-- dept  | median_salary | median_disc
-- Eng   | 65000         | 60000
-- Sales | 45000         | 45000
-- Overall (no GROUP BY): 60000

-- ============================================
-- SOLUTION 2 - MySQL 8.0+ (also works in PostgreSQL with 2.0 caveat below)
-- ============================================

SELECT dept, AVG(salary) AS median_salary
FROM (
  SELECT dept, salary,
         ROW_NUMBER() OVER (PARTITION BY dept ORDER BY salary) AS rn,
         COUNT(*)     OVER (PARTITION BY dept)                 AS cnt
  FROM emp_salary
) t
WHERE rn IN (FLOOR((cnt + 1) / 2), CEIL((cnt + 1) / 2))   -- 1 middle row if odd, 2 if even
GROUP BY dept ORDER BY dept;

-- ============================================
-- EXPECTED OUTPUT (MySQL)
-- ============================================

-- dept  | median_salary
-- Eng   | 65000.0000
-- Sales | 45000.0000
-- Overall median (same query without PARTITION BY / GROUP BY) = 60000.0000
-- Mean for comparison: Eng 70000, Sales 58333.33 -> median is robust to the 100000 / 90000 outliers.
```

---

## 🔍 Why This Works (3 lines max)
For n rows the middle positions are floor((n+1)/2) and ceil((n+1)/2): one row if n is odd, two if even, and AVG of those gives the median. PERCENTILE_CONT does the same interpolation internally.
हिंदी: n rows में बीच की positions floor((n+1)/2) और ceil((n+1)/2) हैं; उनका AVG median है।

---

## ⚡ Alternative Solution

```sql
-- MySQL has no PERCENTILE_CONT / WITHIN GROUP (verified):
SELECT PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY salary) FROM emp_salary;
-- ERROR 1064 (42000): You have an error in your SQL syntax ... near '(ORDER BY salary)'

-- MySQL: odd-count only shortcut (lower median for even counts)
SELECT salary FROM (SELECT salary, ROW_NUMBER() OVER (ORDER BY salary) rn, COUNT(*) OVER () cnt FROM emp_salary) t
WHERE rn = FLOOR((cnt + 1) / 2);      -- 60000 (lower-middle value of 7 rows)

-- PostgreSQL gotcha: the MySQL query works in PostgreSQL, but "/" on INTEGERs truncates.
-- With FLOOR((cnt + 1) / 2) and CEIL((cnt + 1) / 2) both become the same number -> Eng median returned 60000 (wrong; correct = 65000).
-- Fix: divide by 2.0:  rn IN (FLOOR((cnt + 1) / 2.0), CEIL((cnt + 1) / 2.0))  -> Eng 65000 (verified).
```

---

## ⚠️ Common Mistake

```sql
-- ❌ Wrong: AVG(salary) as "median" -- the mean is pulled by outliers
-- ❌ Wrong: taking the middle row only (ignores the even-count case)
-- ❌ Wrong (PostgreSQL): integer division in the position formula (see above)
-- ❌ Wrong: ORDER BY without a stable tiebreaker doesn't matter for values, but NULL salaries
--    must be filtered first: COUNT(*) counts NULLs while ordering puts them at the end -> use WHERE salary IS NOT NULL
--    (PERCENTILE_CONT ignores NULLs automatically)
```

---

## 🎯 Interview Tip (1 line)
Say: "PostgreSQL has PERCENTILE_CONT(0.5) WITHIN GROUP; MySQL needs ROW_NUMBER and COUNT to pick the middle one or two rows - I watch the even-count case, NULLs and integer division, and mention median is better than mean for skewed salaries."

---

## 🔗 Related Questions
→ Q069 (NTILE) | Q066 (ROW_NUMBER) | Q055 (Nth highest salary) | Q077 (mode)
