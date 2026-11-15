---

# Q110. Query Rewrite: Correlated Subquery → Window Function
# Category: Query Optimization
# Difficulty: ⭐⭐⭐ Hard
# DB: Both (MySQL 8.0+ | PostgreSQL)

---

## ❓ Question
Find employees paid more than their department's average salary. The obvious correlated subquery re-runs an aggregate for every employee. Rewrite it with a window function and compare plans and timings in MySQL and PostgreSQL.

---

## 💡 Quick Concept (2 lines only)
A correlated subquery executes once per outer row (here 30,000 times). `AVG(salary) OVER (PARTITION BY dept_id)` computes every department average in one pass over the data and attaches it to each row, then an outer query filters.
हिंदी: Correlated subquery हर row के लिए दोबारा चलती है; window function एक ही pass में सारे group averages निकाल देता है।

---

## ✅ Answer / Solution

```sql
-- ============================================
-- SETUP — MySQL (verified on MySQL 9.1.0)
-- ============================================

CREATE TABLE employees (
  id      INT PRIMARY KEY AUTO_INCREMENT,
  name    VARCHAR(40) NOT NULL,
  dept_id INT NOT NULL,
  salary  DECIMAL(10,2) NOT NULL,
  KEY idx_dept (dept_id)
);
SET SESSION cte_max_recursion_depth = 30000;
INSERT INTO employees (name, dept_id, salary)
WITH RECURSIVE n AS (SELECT 1 i UNION ALL SELECT i+1 FROM n WHERE i < 30000)
SELECT CONCAT('Emp ', i), i % 300 + 1, 30000 + (i * 7919) % 90000 FROM n;   -- 300 depts x 100 employees
ANALYZE TABLE employees;

-- ============================================
-- SOLUTION
-- ============================================

-- Step 1: SLOW - correlated subquery in WHERE (runs 30,000 times)
SELECT e.id, e.dept_id, e.salary
FROM employees e
WHERE e.salary > (SELECT AVG(x.salary) FROM employees x WHERE x.dept_id = e.dept_id);

-- Step 2: FAST - window function computes the average once per partition
SELECT id, dept_id, salary
FROM (
  SELECT id, dept_id, salary,
         AVG(salary) OVER (PARTITION BY dept_id) AS dept_avg    -- one pass, sorted by dept_id
  FROM employees
) t
WHERE salary > dept_avg;

-- Step 3: prove both return the same rows, then compare plans
SELECT COUNT(*) FROM employees e WHERE e.salary > (SELECT AVG(x.salary) FROM employees x WHERE x.dept_id = e.dept_id);
SELECT COUNT(*) FROM (SELECT salary, AVG(salary) OVER (PARTITION BY dept_id) AS dept_avg FROM employees) t WHERE salary > dept_avg;
EXPLAIN ANALYZE SELECT e.id, e.dept_id, e.salary FROM employees e
WHERE e.salary > (SELECT AVG(x.salary) FROM employees x WHERE x.dept_id = e.dept_id);
EXPLAIN ANALYZE SELECT id, dept_id, salary FROM (
  SELECT id, dept_id, salary, AVG(salary) OVER (PARTITION BY dept_id) AS dept_avg FROM employees) t
WHERE salary > dept_avg;

-- ============================================
-- EXPECTED OUTPUT (real, MySQL 9.1.0)
-- ============================================
-- Step 3 counts: 14998 and 14998   (identical)
-- Step 1 plan: Filter (e.salary > (select #2)) actual time=0.559..1942 ms rows=14998
--                -> Table scan on e (30000 rows)
--                -> Select #2 (subquery in condition; dependent) Aggregate avg(x.salary) loops=30000
--                     -> Index lookup on x using idx_dept (dept_id = e.dept_id) rows=100 loops=30000
-- Step 2 plan: Filter (t.salary > t.dept_avg) actual time=29.1..32.4 ms rows=14998
--                -> Materialize -> Window aggregate with buffering: avg(salary) OVER (PARTITION BY dept_id)
--                   -> Sort: dept_id -> Table scan on employees
--   ~1942 ms vs ~32 ms  (about 60x faster; absolute times are machine dependent)
```

```sql
-- ============================================
-- POSTGRESQL (verified on PGlite = PostgreSQL 18.6; same data via generate_series)
-- ============================================
-- Correlated version: Seq Scan on employees  Filter: (salary > (SubPlan 1))
--   SubPlan 1: Aggregate loops=30000 -> Bitmap Heap Scan on employees x (rows=100, loops=30000) -> idx_dept
--   Rows Removed by Filter: 15002;  Heap Blocks: exact=3000000  (3 million page visits!)
-- Window version:   Subquery Scan on t  Filter: (t.salary > t.dept_avg)
--   -> WindowAgg  Window: w1 AS (PARTITION BY dept_id)  Storage: Memory 20kB
--      -> Index Scan using idx_dept on employees (actual rows=30000)   (already ordered by dept_id: no Sort)
-- Both return 14998 rows. PostgreSQL also does NOT decorrelate this subquery automatically.
```

---

## 🔍 Why This Works (3 lines max)
The window plan reads the table once, sorts/partitions by dept_id, and streams the running aggregate - O(n log n) vs O(n x group size) index lookups for the subquery. Because a window function cannot appear in WHERE, the outer query (derived table/CTE) applies the filter.
हिंदी: Window plan table को एक बार पढ़ता है; WHERE में window function नहीं चलता, इसलिए बाहर वाली query में filter करो।

---

## ⚡ Alternative Solution

```sql
-- Join to a pre-aggregated derived table (works on MySQL 5.7 and older, no window functions needed):
SELECT e.id, e.dept_id, e.salary
FROM employees e
JOIN (SELECT dept_id, AVG(salary) AS dept_avg FROM employees GROUP BY dept_id) d
  ON d.dept_id = e.dept_id
WHERE e.salary > d.dept_avg;                    -- one grouped scan + hash/index join (not timed here)

-- Many dialects: QUALIFY (not in MySQL/PostgreSQL). PostgreSQL only: LATERAL for "top row per group" rewrites.
-- Rule: use the window form when you also need dept_avg in the SELECT list; use the join form if the grouped
-- result is small and you want the optimizer to choose join order.
```

---

## ⚠️ Common Mistake

```sql
-- ❌ Putting the window function directly in WHERE (standard SQL forbids it; not run here)
SELECT * FROM employees WHERE salary > AVG(salary) OVER (PARTITION BY dept_id);   -- ERROR: not allowed in WHERE
-- ❌ Using a correlated subquery in the SELECT list too (runs again per row)
SELECT e.*, (SELECT AVG(x.salary) FROM employees x WHERE x.dept_id = e.dept_id) AS dept_avg FROM employees e;
-- ❌ Assuming "it has an index so it's fine": 30,000 index lookups x 100 rows each still took 1.9 s
-- ❌ Forgetting NULL salaries: AVG ignores NULLs, salary > NULL is unknown (row dropped) - same in both forms
```

---

## 🎯 Interview Tip (1 line)
Say: "A correlated subquery is a hidden nested loop - I check 'loops=' in EXPLAIN ANALYZE and rewrite with a window function or a pre-aggregated join so each group is computed once; I always verify both versions return the same rows."

---

## 🔗 Related Questions
→ Q066 (ROW_NUMBER vs RANK vs DENSE_RANK) | Q075 (Top N per group) | Q005 (IN vs EXISTS) | Q109 (Slow query diagnosis)
