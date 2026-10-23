---

# Q075. Top N Per Group — ROW_NUMBER Pattern
# Category: Aggregations & Window Functions
# Difficulty: ⭐⭐⭐ Hard
# DB: Both (MySQL 8.0+ | PostgreSQL)

---

## ❓ Question
Get the top 3 highest-paid employees per department. Also show: top 3 most recent orders per user, and how to get the "latest record per group" (1 row per group). Handle ties.

---

## 💡 Quick Concept (2 lines only)
ROW_NUMBER() with PARTITION BY assigns per-group row numbers. Filter WHERE rn <= N in an outer query. Use DENSE_RANK instead of ROW_NUMBER when ties should all appear (top 3 salary tiers, not top 3 employees).
हिंदी: ROW_NUMBER + PARTITION BY = per-group numbering। Outer query में WHERE rn <= N filter करो। Ties चाहिए तो DENSE_RANK use करो।

---

## ✅ Answer / Solution

```sql
-- ============================================
-- SETUP
-- ============================================

CREATE TABLE employees (
  id      INT PRIMARY KEY,
  name    VARCHAR(100),
  dept    VARCHAR(50),
  salary  DECIMAL(10,2),
  hire_date DATE
);

INSERT INTO employees VALUES
  (1, 'Alice',  'Engineering', 120000, '2020-01-15'),
  (2, 'Bob',    'Engineering',  95000, '2021-03-20'),
  (3, 'Carol',  'Engineering',  95000, '2019-07-01'),  -- tied with Bob
  (4, 'Dave',   'Engineering',  85000, '2022-05-10'),
  (5, 'Eve',    'Engineering',  80000, '2023-01-05'),
  (6, 'Frank',  'Sales',        90000, '2020-02-28'),
  (7, 'Grace',  'Sales',        75000, '2021-08-15'),
  (8, 'Heidi',  'Sales',        75000, '2020-11-30'),  -- tied with Grace
  (9, 'Ivan',   'Sales',        60000, '2022-04-10'),
  (10,'Judy',   'Marketing',   100000, '2019-05-01'),
  (11,'Kevin',  'Marketing',    80000, '2020-09-15'),
  (12,'Lisa',   'Marketing',    80000, '2021-02-20');  -- tied with Kevin

-- ============================================
-- TOP 3 PER DEPARTMENT — ROW_NUMBER (strict top 3, handles ties arbitrarily)
-- ============================================

SELECT dept, name, salary, rn
FROM (
  SELECT
    dept,
    name,
    salary,
    ROW_NUMBER() OVER (
      PARTITION BY dept
      ORDER BY salary DESC, id ASC   -- id ASC = deterministic tiebreaker
    ) AS rn
  FROM employees
) ranked
WHERE rn <= 3
ORDER BY dept, rn;

-- Output:
-- dept        | name    | salary   | rn
-- Engineering | Alice   | 120000   | 1
-- Engineering | Bob     | 95000    | 2   ← Bob got rn=2 (Carol rn=3)
-- Engineering | Carol   | 95000    | 3   ← Carol got rn=3 (tied, id=3 > id=2)
-- Marketing   | Judy    | 100000   | 1
-- Marketing   | Kevin   | 80000    | 2   ← arbitrary between Kevin/Lisa
-- Marketing   | Lisa    | 80000    | 3
-- Sales       | Frank   | 90000    | 1
-- Sales       | Grace   | 75000    | 2   ← arbitrary between Grace/Heidi
-- Sales       | Heidi   | 75000    | 3

-- ============================================
-- TOP 3 SALARY TIERS PER DEPT — DENSE_RANK (all ties included)
-- ============================================

SELECT dept, name, salary, dr
FROM (
  SELECT
    dept,
    name,
    salary,
    DENSE_RANK() OVER (
      PARTITION BY dept
      ORDER BY salary DESC
    ) AS dr
  FROM employees
) ranked
WHERE dr <= 3
ORDER BY dept, dr, name;

-- Output (may return more than 3 rows per dept when ties exist!):
-- Engineering | Alice  | 120000 | 1
-- Engineering | Bob    | 95000  | 2
-- Engineering | Carol  | 95000  | 2   ← BOTH included at rank 2
-- Engineering | Dave   | 85000  | 3
-- Sales       | Frank  | 90000  | 1
-- Sales       | Grace  | 75000  | 2
-- Sales       | Heidi  | 75000  | 2   ← BOTH included at rank 2
-- Sales       | Ivan   | 60000  | 3

-- Use DENSE_RANK when: "top 3 salary levels" (ties should all appear)
-- Use ROW_NUMBER when: "exactly 3 employees per dept" (guaranteed 3 rows max)

-- ============================================
-- LATEST RECORD PER GROUP (most common use: "latest order per user")
-- ============================================

CREATE TABLE orders (
  id         INT PRIMARY KEY AUTO_INCREMENT,
  user_id    INT,
  amount     DECIMAL(10,2),
  status     VARCHAR(20),
  created_at DATETIME
);

INSERT INTO orders VALUES
  (1, 101, 49.99,  'completed', '2024-01-10 10:00:00'),
  (2, 101, 149.99, 'completed', '2024-02-15 14:30:00'),
  (3, 101, 29.99,  'pending',   '2024-03-01 09:00:00'),  -- latest for user 101
  (4, 102, 99.99,  'completed', '2024-01-20 11:00:00'),
  (5, 102, 199.99, 'refunded',  '2024-02-28 16:00:00'),  -- latest for user 102
  (6, 103, 59.99,  'completed', '2024-03-05 13:00:00');  -- only order for user 103

-- Get each user's most recent order:
SELECT user_id, id AS order_id, amount, status, created_at
FROM (
  SELECT *,
    ROW_NUMBER() OVER (
      PARTITION BY user_id
      ORDER BY created_at DESC
    ) AS rn
  FROM orders
) ranked
WHERE rn = 1;

-- Output:
-- user_id | order_id | amount | status   | created_at
-- 101     | 3        | 29.99  | pending  | 2024-03-01 09:00:00
-- 102     | 5        | 199.99 | refunded | 2024-02-28 16:00:00
-- 103     | 6        | 59.99  | completed| 2024-03-05 13:00:00

-- ============================================
-- ALTERNATIVE: LATERAL JOIN (PgSQL — elegant)
-- ============================================

-- PgSQL: LATERAL gets most recent order per user without CTE:
SELECT u.id AS user_id, o.id AS order_id, o.amount, o.created_at
FROM users u
JOIN LATERAL (
  SELECT id, amount, status, created_at
  FROM orders
  WHERE user_id = u.id
  ORDER BY created_at DESC
  LIMIT 1                    -- ← 1 row per user!
) o ON true;

-- LATERAL is conceptually: "for each user, run this subquery and take 1 row"
-- Uses index on (user_id, created_at DESC) efficiently — each subquery is index seek
-- Great for: latest message per conversation, latest event per device

-- ============================================
-- OLD MySQL (pre-8.0) — Subquery trick (no window functions)
-- ============================================

-- Top 1 per group (MySQL < 8.0):
SELECT e1.*
FROM employees e1
LEFT JOIN employees e2
  ON e1.dept = e2.dept
  AND e1.salary < e2.salary   -- is there someone in same dept with higher salary?
WHERE e2.id IS NULL;          -- no one has higher salary → this is the top earner
-- ← Only works for TOP 1 (max). Becomes complex for top N.

-- Top N using variables (MySQL 5.7 style — unreliable with certain plans):
-- Avoid! Use MySQL 8.0 window functions instead.

-- ============================================
-- TOP N WITH ADDITIONAL FILTER
-- ============================================

-- Top 2 completed orders per user:
SELECT user_id, order_id, amount, status
FROM (
  SELECT
    user_id,
    id AS order_id,
    amount,
    status,
    ROW_NUMBER() OVER (
      PARTITION BY user_id
      ORDER BY created_at DESC
    ) AS rn
  FROM orders
  WHERE status = 'completed'   -- ← filter BEFORE window function
) ranked
WHERE rn <= 2
ORDER BY user_id, rn;

-- Filter inside window (WHERE in inner query) vs outside (HAVING in outer):
-- Inner WHERE filters BEFORE partitioning → affects which rows get rn=1, rn=2
-- Outer WHERE rn <= 2 filters AFTER → just takes top rows per partition

-- ============================================
-- FIRST_VALUE / LAST_VALUE (alternative to row_number for single column)
-- ============================================

-- Get each employee's salary AND their dept's highest salary in one query:
SELECT
  dept,
  name,
  salary,
  FIRST_VALUE(salary) OVER (PARTITION BY dept ORDER BY salary DESC) AS dept_max_salary,
  FIRST_VALUE(name) OVER (PARTITION BY dept ORDER BY salary DESC) AS dept_top_earner
FROM employees
ORDER BY dept, salary DESC;

-- FIRST_VALUE gets value from first row of the window (top salary after ORDER BY DESC)
-- No need for self-join or subquery!
```

---

## 🔍 Why This Works (3 lines max)
PARTITION BY creates independent windows per department — ROW_NUMBER restarts from 1 for each. The outer WHERE filters to top N without collapsing groups like GROUP BY would. DENSE_RANK is preferred when ties should all appear (top 3 salary tiers may return 4+ employees); ROW_NUMBER when you need exactly N rows per group with a deterministic tiebreaker.
हिंदी: PARTITION BY = per-group independent window। ROW_NUMBER restarts हर group में। DENSE_RANK = ties सब आते हैं। ROW_NUMBER = exactly N rows guaranteed।

---

## ⚡ Alternative Solution

```sql
-- CTE approach (same performance, more readable):
WITH ranked_employees AS (
  SELECT *,
    ROW_NUMBER() OVER (PARTITION BY dept ORDER BY salary DESC, id) AS rn
  FROM employees
)
SELECT dept, name, salary FROM ranked_employees WHERE rn <= 3;

-- PgSQL: DISTINCT ON (PostgreSQL-specific shortcut for top 1 per group):
SELECT DISTINCT ON (dept) dept, name, salary
FROM employees
ORDER BY dept, salary DESC;
-- Returns exactly 1 row per dept (the one with highest salary after ORDER BY)
-- Can't do top N with DISTINCT ON — only works for top 1
-- Add tiebreaker: ORDER BY dept, salary DESC, id ASC
```

---

## ⚠️ Common Mistake

```sql
-- ❌ Wrong: GROUP BY for "top N per group" — loses individual row data
SELECT dept, MAX(salary) FROM employees GROUP BY dept;
-- Returns max salary per dept, but NOT the employee name!
-- Can't easily get the employee details with GROUP BY

-- ❌ Wrong: Non-deterministic ROW_NUMBER without tiebreaker
ROW_NUMBER() OVER (PARTITION BY dept ORDER BY salary DESC)
-- Bob and Carol both have salary 95000 → which gets rn=2 vs rn=3 is random!
-- ✅ Add tiebreaker: ORDER BY salary DESC, id ASC (or hire_date ASC)
-- Makes results deterministic across runs

-- ❌ Wrong: Using RANK instead of ROW_NUMBER for "exactly N rows"
-- RANK: Bob=2, Carol=2, Dave=4 (skips 3)
-- WHERE rank <= 3 → returns Bob, Carol but NOT Dave (rank 4 > 3)!
-- Returns only 2 Engineering employees instead of 3
-- ✅ Use ROW_NUMBER for exactly N, DENSE_RANK for top N tiers

-- ❌ Wrong: Filtering on window function in WHERE directly
SELECT *, ROW_NUMBER() OVER (PARTITION BY dept ORDER BY salary DESC) AS rn
FROM employees
WHERE rn <= 3;  -- ← ERROR! Can't use window function alias in WHERE
-- ✅ Must wrap in subquery or CTE:
SELECT * FROM (SELECT *, ROW_NUMBER() ... AS rn FROM ...) t WHERE rn <= 3;
```

---

## 🎯 Interview Tip (1 line)
Say: "For top N per group I use ROW_NUMBER with PARTITION BY and filter in an outer query — ROW_NUMBER guarantees exactly N rows with a deterministic tiebreaker. If ties should all appear (top 3 salary levels, not top 3 employees), I switch to DENSE_RANK. For 'latest record per group', the same ROW_NUMBER pattern with ORDER BY created_at DESC and WHERE rn=1 is my go-to."

---

## 🔗 Related Questions
→ Q066 (ROW_NUMBER vs RANK vs DENSE_RANK) | Q067 (LEAD/LAG) | Q055 (Nth highest salary) | Q185 (LATERAL join PgSQL)
