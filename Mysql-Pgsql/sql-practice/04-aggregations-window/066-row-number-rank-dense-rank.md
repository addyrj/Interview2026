---

# Q066. ROW_NUMBER() vs RANK() vs DENSE_RANK() — Output Question
# Category: Aggregations & Window Functions
# Difficulty: ⭐⭐ Medium
# DB: Both (MySQL 8.0+ | PostgreSQL)

---

## ❓ Question
Given the salaries table below, what is the output of ROW_NUMBER(), RANK(), and DENSE_RANK()? When would you use each in a real scenario?

```sql
-- employees table:
-- id | name    | dept    | salary
-- ---+---------+---------+--------
-- 1  | Alice   | Eng     | 90000
-- 2  | Bob     | Eng     | 85000
-- 3  | Carol   | Eng     | 85000
-- 4  | Dave    | Eng     | 80000
-- 5  | Eve     | Sales   | 70000
-- 6  | Frank   | Sales   | 70000
-- 7  | Grace   | Sales   | 65000
```

---

## 💡 Quick Concept (2 lines only)
ROW_NUMBER = always unique sequential (1,2,3,4 — ties get different numbers). RANK = ties get same rank, next rank SKIPS (1,2,2,4). DENSE_RANK = ties get same rank, next rank is CONSECUTIVE (1,2,2,3 — no skip).
हिंदी: ROW_NUMBER = हमेशा unique (1,2,3,4)। RANK = ties same rank, फिर skip (1,2,2,4)। DENSE_RANK = ties same rank, no skip (1,2,2,3)।

---

## ✅ Answer / Solution

```sql
-- ============================================
-- SETUP
-- ============================================

CREATE TABLE employees (
  id     INT PRIMARY KEY,
  name   VARCHAR(50),
  dept   VARCHAR(20),
  salary DECIMAL(10,2)
);

INSERT INTO employees VALUES
  (1,'Alice','Eng', 90000),
  (2,'Bob',  'Eng', 85000),
  (3,'Carol','Eng', 85000),
  (4,'Dave', 'Eng', 80000),
  (5,'Eve',  'Sales',70000),
  (6,'Frank','Sales',70000),
  (7,'Grace','Sales',65000);

-- ============================================
-- THE QUERY
-- ============================================

SELECT
  name,
  dept,
  salary,
  ROW_NUMBER() OVER (PARTITION BY dept ORDER BY salary DESC) AS row_num,
  RANK()       OVER (PARTITION BY dept ORDER BY salary DESC) AS rnk,
  DENSE_RANK() OVER (PARTITION BY dept ORDER BY salary DESC) AS dense_rnk
FROM employees
ORDER BY dept, salary DESC;

-- ============================================
-- EXPECTED OUTPUT
-- ============================================

/*
name  | dept  | salary | row_num | rnk | dense_rnk
------+-------+--------+---------+-----+-----------
Alice | Eng   | 90000  |    1    |  1  |     1      ← unique top
Bob   | Eng   | 85000  |    2    |  2  |     2      ← tied with Carol
Carol | Eng   | 85000  |    3    |  2  |     2      ← same rank (tied)
Dave  | Eng   | 80000  |    4    |  4  |     3      ← RANK skips to 4, DENSE stays 3

Eve   | Sales | 70000  |    1    |  1  |     1      ← tied with Frank
Frank | Sales | 70000  |    2    |  1  |     1      ← same rank (tied)
Grace | Sales | 65000  |    3    |  3  |     2      ← RANK skips to 3, DENSE stays 2

KEY DIFFERENCE:
Bob vs Carol (salary 85000 — tied):
  ROW_NUMBER: 2, 3    ← arbitrary order within tie
  RANK:       2, 2    ← both get rank 2
  DENSE_RANK: 2, 2    ← both get rank 2

Dave (salary 80000 — next after tie):
  RANK:       4       ← skips 3 (because two people had rank 2)
  DENSE_RANK: 3       ← consecutive, never skips
*/

-- ============================================
-- PRACTICAL USE CASES
-- ============================================

-- ROW_NUMBER: Get exactly 1 row per group (no duplicates)
-- Use: Top product per category, latest order per customer

SELECT *
FROM (
  SELECT *,
    ROW_NUMBER() OVER (PARTITION BY dept ORDER BY salary DESC) AS rn
  FROM employees
) ranked
WHERE rn = 1;   -- ← Get EXACTLY ONE employee per dept (highest paid)
-- Even if tied: arbitrarily picks one (use ORDER BY id as tiebreaker for determinism)

-- Output:
-- Alice | Eng   | 90000   ← only 1 per Eng
-- Eve   | Sales | 70000   ← only 1 per Sales (Eve or Frank, non-deterministic without tiebreaker)

-- Add tiebreaker for determinism:
ROW_NUMBER() OVER (PARTITION BY dept ORDER BY salary DESC, id ASC)

-- ─────────────────────────────────────────────

-- RANK: Medal-style ranking (Gold/Silver/Bronze), allow ties
-- Use: Leaderboards, sports rankings

SELECT name, salary,
  RANK() OVER (ORDER BY salary DESC) AS medal_rank
FROM employees;
-- Alice = 1st (Gold)
-- Bob, Carol = 2nd (Silver, Silver)  ← both get 2
-- Dave = 4th                         ← 3rd doesn't exist (skip)

-- ─────────────────────────────────────────────

-- DENSE_RANK: When you want "2nd highest" to always mean "2nd distinct value"
-- Use: "Find all employees earning the 2nd highest salary"

SELECT name, salary
FROM (
  SELECT name, salary,
    DENSE_RANK() OVER (ORDER BY salary DESC) AS dr
  FROM employees
) ranked
WHERE dr = 2;

-- Output:
-- Bob   | 85000   ← both have DENSE_RANK = 2
-- Carol | 85000

-- With RANK() instead: WHERE rank = 2 would also work here,
-- but WHERE rank = 3 would return nothing (rank 3 was skipped!)
-- With DENSE_RANK(): WHERE dr = 3 → returns Dave (no gaps!)
```

---

## 🔍 Why This Works (3 lines max)
PARTITION BY restarts numbering for each department group. ORDER BY within the OVER clause determines the ranking order. The difference: ROW_NUMBER never repeats, RANK gives same number to ties but skips the next, DENSE_RANK gives same number to ties and never skips.
हिंदी: PARTITION BY हर department के लिए separately rank करता है। ROW_NUMBER कभी repeat नहीं होता, RANK ties पर same number देता है फिर skip, DENSE_RANK skip नहीं करता।

---

## ⚡ Alternative Solution

```sql
-- Old MySQL way (before 8.0 — no window functions):
-- Simulate ROW_NUMBER with variable:
SET @row_num = 0;
SELECT name, salary, (@row_num := @row_num + 1) AS row_num
FROM employees
ORDER BY salary DESC;
-- This is the old way — unreliable with certain query plans
-- Always prefer window functions (MySQL 8.0+, PgSQL always supported)

-- NTILE() — related function, divide into N buckets:
SELECT name, salary,
  NTILE(4) OVER (ORDER BY salary DESC) AS quartile
FROM employees;
-- Divides employees into 4 equal groups (Q1=top, Q4=bottom)
-- Useful for: segmenting customers into revenue buckets
```

---

## ⚠️ Common Mistake

```sql
-- ❌ Wrong: Confusing RANK with DENSE_RANK for "Nth highest" problem
-- "Find 2nd highest salary"
SELECT salary FROM employees
WHERE salary = (
  SELECT DISTINCT salary FROM employees
  ORDER BY salary DESC
  LIMIT 1 OFFSET 1   -- MySQL: 2nd distinct salary
);
-- This works but doesn't handle ties elegantly

-- Better: DENSE_RANK approach
SELECT DISTINCT salary FROM (
  SELECT salary,
    DENSE_RANK() OVER (ORDER BY salary DESC) AS dr
  FROM employees
) x WHERE dr = 2;

-- ❌ Wrong: Using ROW_NUMBER when ties should get same number
-- ROW_NUMBER arbitrarily picks one of the tied rows
-- For leaderboards → use RANK or DENSE_RANK

-- ❌ Wrong: Expecting deterministic output from ROW_NUMBER without tiebreaker
-- ROW_NUMBER() OVER (PARTITION BY dept ORDER BY salary DESC)
-- ← Bob and Carol both have 85000: which gets row 2 vs row 3?
-- Undefined! Add a tiebreaker: ORDER BY salary DESC, id ASC
```

---

## 🎯 Interview Tip (1 line)
Say: "ROW_NUMBER for exactly-one-per-group queries, DENSE_RANK for 'Nth highest value' queries (no gaps), RANK for medal-style leaderboards — and always add a tiebreaker column in ORDER BY when using ROW_NUMBER to get deterministic results."

---

## 🔗 Related Questions
→ Q075 (top N per group) | Q067 (LEAD/LAG) | Q073 (PARTITION BY vs GROUP BY) | Q239 (2nd highest salary classic)
