---

# Q068. FIRST_VALUE() and LAST_VALUE()
# Category: Aggregations & Window Functions
# Difficulty: ⭐⭐ Medium
# DB: Both (MySQL 8.0+ | PostgreSQL) — verified on MySQL 9.1 and PGlite (PostgreSQL)

---

## ❓ Question
For each employee show the top earner's name in their department and the lowest-paid name in the department. Why does LAST_VALUE often return the current row instead of the last one?

---

## 💡 Quick Concept (2 lines only)
FIRST_VALUE/LAST_VALUE return an expression from the first/last row of the window FRAME. With ORDER BY and no explicit frame, the default frame ends at CURRENT ROW, so LAST_VALUE just returns the current row.
हिंदी: Default frame CURRENT ROW पर खत्म होता है, इसलिए LAST_VALUE को पूरा frame (UNBOUNDED FOLLOWING) देना पड़ता है।

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
 (4,'Dev','Sales',90000),(5,'Esha','Sales',75000),(6,'Farhan','Sales',60000);

-- ============================================
-- SOLUTION
-- ============================================

-- Step 1: FIRST_VALUE works with the default frame
-- Step 2: LAST_VALUE needs ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING

SELECT dept, name, salary,
  FIRST_VALUE(name) OVER w AS top_earner,
  LAST_VALUE(name)  OVER (PARTITION BY dept ORDER BY salary DESC
      ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS lowest_paid
FROM employees
WINDOW w AS (PARTITION BY dept ORDER BY salary DESC)
ORDER BY dept, salary DESC;

-- ============================================
-- EXPECTED OUTPUT
-- ============================================

-- dept  | name   | salary | top_earner | lowest_paid
-- ------+--------+--------+------------+------------
-- Eng   | Asha   | 120000 | Asha       | Chitra
-- Eng   | Bilal  |  95000 | Asha       | Chitra
-- Eng   | Chitra |  80000 | Asha       | Chitra
-- Sales | Dev    |  90000 | Dev        | Farhan
-- Sales | Esha   |  75000 | Dev        | Farhan
-- Sales | Farhan |  60000 | Dev        | Farhan

-- The trap: LAST_VALUE(name) OVER (PARTITION BY dept ORDER BY salary DESC) gives
--   Asha, Bilal, Chitra, Dev, Esha, Farhan  (= the current row's own name)
```

---

## 🔍 Why This Works (3 lines max)
With ORDER BY, the default frame is RANGE BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW, so "last row of the frame" is the current row. Widening the frame to UNBOUNDED FOLLOWING makes it the true last row of the partition.
हिंदी: Frame को UNBOUNDED FOLLOWING तक बढ़ाओ, तब LAST_VALUE partition की असली आखिरी row देगा।

---

## ⚡ Alternative Solution

```sql
-- Simplest: flip the sort and use FIRST_VALUE (default frame is enough)
SELECT dept, name, salary,
  FIRST_VALUE(name) OVER (PARTITION BY dept ORDER BY salary ASC) AS lowest_paid
FROM employees ORDER BY dept, salary DESC;
-- Same lowest_paid column as above (Chitra / Farhan)

-- NTH_VALUE has the same frame trap
SELECT name, NTH_VALUE(name, 2) OVER (PARTITION BY dept ORDER BY salary DESC
  ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS second_highest
FROM employees;
-- Eng rows -> Bilal, Sales rows -> Esha

-- MySQL vs PgSQL: syntax and results identical (named WINDOW clause works in both).
```

---

## ⚠️ Common Mistake

```sql
-- ❌ Wrong: LAST_VALUE with default frame
LAST_VALUE(name) OVER (PARTITION BY dept ORDER BY salary DESC)   -- returns current row

-- ✅ Correct: explicit full frame
LAST_VALUE(name) OVER (PARTITION BY dept ORDER BY salary DESC
   ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING)

-- ❌ Wrong: relying on RANGE default when salaries tie -- tied rows are peers and all see the same "current row end"
```

---

## 🎯 Interview Tip (1 line)
Say: "LAST_VALUE is the classic window trap: the default frame stops at the current row, so I either specify UNBOUNDED FOLLOWING or just reverse the ORDER BY and use FIRST_VALUE."

---

## 🔗 Related Questions
→ Q074 (ROWS vs RANGE) | Q075 (top N per group) | Q067 (LEAD/LAG)
