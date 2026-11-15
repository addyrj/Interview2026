---

# Q172. MySQL 8.0 CTEs (WITH and WITH RECURSIVE)
# Category: MySQL Specific
# Difficulty: ⭐⭐ Medium
# DB: MySQL (8.0+) — PostgreSQL differences noted

---

## ❓ Question
Show non-recursive and recursive CTEs in MySQL 8.0: (a) reuse a monthly-totals CTE, (b) walk an employee hierarchy with a level and path, (c) generate a number series. What stops an infinite recursion? How do MySQL and PostgreSQL CTEs differ?

---

## 💡 Quick Concept (2 lines only)
A CTE (`WITH name AS (...)`) is a named temporary result scoped to one statement; `WITH RECURSIVE` = anchor query UNION ALL recursive member that references itself. MySQL gained both in 8.0 (5.7 had neither).
हिंदी: CTE एक statement-level temporary named result है; RECURSIVE में anchor + खुद को call करने वाला हिस्सा होता है।

---

## ✅ Answer / Solution

```sql
-- ============================================
-- SETUP (verified on MySQL 9.1.0)
-- ============================================

CREATE TABLE sales (id INT PRIMARY KEY, region VARCHAR(20), sale_date DATE, amount DECIMAL(10,2));
INSERT INTO sales VALUES
(1,'North','2024-01-05',1000),(2,'North','2024-01-12',1500),(3,'North','2024-02-03',1500),
(4,'South','2024-01-20', 800),(5,'South','2024-02-11',1200),(6,'South','2024-03-02', 950),
(7,'North','2024-03-15',2000);

CREATE TABLE emp (id INT PRIMARY KEY, name VARCHAR(30), manager_id INT);
INSERT INTO emp VALUES (1,'Priya (CEO)',NULL),(2,'Rahul',1),(3,'Sneha',1),
                       (4,'Amit',2),(5,'Neha',2),(6,'Vikram',4);

-- ============================================
-- (a) Non-recursive CTEs: months above the average month
-- ============================================

WITH monthly AS (
  SELECT DATE_FORMAT(sale_date,'%Y-%m') AS ym, SUM(amount) AS tot
  FROM sales GROUP BY ym
),
avg_all AS (SELECT AVG(tot) AS a FROM monthly)     -- 2nd CTE can use the 1st
SELECT m.ym, m.tot, ROUND(a.a,2) AS avg_tot
FROM monthly m, avg_all a
WHERE m.tot > a.a;

-- Result:
-- ym      | tot     | avg_tot
-- 2024-01 | 3300.00 | 2983.33

-- ============================================
-- (b) Recursive CTE: org chart with level + path
-- ============================================

WITH RECURSIVE org AS (
  SELECT id, name, manager_id, 0 AS lvl,
         CAST(name AS CHAR(200)) AS path           -- cast so column is wide enough for later rows
  FROM emp WHERE manager_id IS NULL                -- anchor: the root
  UNION ALL
  SELECT e.id, e.name, e.manager_id, o.lvl + 1,
         CONCAT(o.path, ' > ', e.name)
  FROM emp e JOIN org o ON e.manager_id = o.id     -- recursive member
)
SELECT * FROM org ORDER BY path;

-- Result:
-- id | name        | manager_id | lvl | path
-- 1  | Priya (CEO) | NULL       | 0   | Priya (CEO)
-- 2  | Rahul       | 1          | 1   | Priya (CEO) > Rahul
-- 4  | Amit        | 2          | 2   | Priya (CEO) > Rahul > Amit
-- 6  | Vikram      | 4          | 3   | Priya (CEO) > Rahul > Amit > Vikram
-- 5  | Neha        | 2          | 2   | Priya (CEO) > Rahul > Neha
-- 3  | Sneha       | 1          | 1   | Priya (CEO) > Sneha

-- ============================================
-- (c) Number series (MySQL has no generate_series)
-- ============================================

WITH RECURSIVE nums AS (SELECT 1 AS n UNION ALL SELECT n + 1 FROM nums WHERE n < 5)
SELECT * FROM nums;
-- Result: n = 1,2,3,4,5

-- ============================================
-- Runaway recursion guard
-- ============================================

SHOW VARIABLES LIKE 'cte_max_recursion_depth';   -- 1000 by default
SET SESSION cte_max_recursion_depth = 10;
WITH RECURSIVE r AS (SELECT 1 AS n UNION ALL SELECT n + 1 FROM r) SELECT COUNT(*) FROM r;
-- ERROR 3636 (HY000): Recursive query aborted after 11 iterations.
--   Try increasing @@cte_max_recursion_depth to a larger value.
-- NOTE: for 5000 rows via recursion you must raise it (e.g. 10000) — also verified.
```

---

## 🔍 Why This Works (3 lines max)
The anchor runs once; the recursive member then runs repeatedly on the rows produced by the previous iteration until it returns nothing. MySQL aborts when iterations exceed `cte_max_recursion_depth` (default 1000) — a safety net against cycles.
हिंदी: Anchor एक बार चलता है, फिर recursive हिस्सा तब तक जब तक नई row न मिले; depth limit से infinite loop रुकता है।

---

## ⚡ Alternative Solution

```sql
-- MySQL: CTE with DML (verified: works for DELETE/UPDATE target subqueries)
WITH x AS (SELECT id FROM emp WHERE manager_id = 2)
DELETE FROM emp WHERE id IN (SELECT id FROM x);       -- removes Amit, Neha

-- PostgreSQL differences:
--  * PG 12+ inlines a CTE referenced once; use WITH x AS MATERIALIZED (...) to force a fence.
--    MySQL decides itself: merges it like a derived table, or materializes if referenced multiple times.
--  * PG supports data-modifying CTEs: WITH d AS (DELETE ... RETURNING *) INSERT INTO archive SELECT * FROM d;
--    MySQL has no RETURNING and no DML inside a CTE body.
--  * PG: generate_series(1,5) replaces the recursive number trick.
--  * PG has SEARCH / CYCLE clauses (14+) for recursion; MySQL: track path yourself (as above).
```

---

## ⚠️ Common Mistake

```sql
-- ❌ Forgetting RECURSIVE keyword in MySQL (self-reference -> table 'org' doesn't exist)
WITH org AS (SELECT ... UNION ALL SELECT ... FROM emp JOIN org ...) SELECT * FROM org;
-- ✅ WITH RECURSIVE org AS (...)

-- ❌ Column too narrow: anchor 'path' = CHAR from short name -> later rows truncated / error 1406
-- ✅ CAST(name AS CHAR(200)) in the anchor

-- ❌ Cyclic data (A manages B manages A) -> loops until depth limit hits
-- ✅ Track visited ids in a path string and add WHERE NOT FIND_IN_SET(e.id, o.path_ids)
```

---

## 🎯 Interview Tip (1 line)
Say a CTE is not a performance feature by itself: in MySQL 8 it's merged or materialized like a derived table, so check EXPLAIN; use recursive CTEs for trees/graphs, guard with cte_max_recursion_depth, and for very deep or hot hierarchies consider closure tables or path columns.

---

## 🔗 Related Questions
→ Q018 (Common table expressions) | Q171 (MySQL 8.0 window functions) | Q075 (Top N per group)
