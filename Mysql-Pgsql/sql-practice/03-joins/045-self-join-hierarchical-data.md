---

# Q045. SELF JOIN — Hierarchical Data
# Category: Joins
# Difficulty: ⭐⭐ Medium
# DB: Both (MySQL 8.0+ | PostgreSQL)

---

## ❓ Question
In `employees(emp_id, emp_name, salary, manager_id)`, list each employee with their manager, find employees who earn more than their manager, count direct reports per manager, find same-department pairs, and print the full org chart path.

---

## 💡 Quick Concept (2 lines only)
A self join joins a table to itself using two aliases (`e` = employee, `m` = manager) with `e.manager_id = m.emp_id`. Use LEFT JOIN to keep the top boss (NULL manager); use a recursive CTE for unlimited depth.
हिंदी: Self join में एक ही table को दो alias देकर जोड़ते हैं; पूरी hierarchy के लिए recursive CTE चाहिए।

---

## ✅ Answer / Solution

```sql
-- ============================================
-- SETUP (run this first) — same SQL for MySQL and PostgreSQL
-- ============================================

CREATE TABLE departments (dept_id INT PRIMARY KEY, dept_name VARCHAR(50) NOT NULL);
CREATE TABLE employees (
  emp_id INT PRIMARY KEY, emp_name VARCHAR(50) NOT NULL,
  dept_id INT NULL, salary INT NOT NULL, manager_id INT NULL
);
INSERT INTO departments VALUES (10,'Engineering'),(20,'Sales'),(30,'HR'),(40,'Legal');
INSERT INTO employees VALUES
  (1,'Asha', 10,150000,NULL),
  (2,'Bilal',10,120000,1),
  (3,'Chen', 20, 90000,1),
  (4,'Divya',20, 85000,3),
  (5,'Emil', NULL,70000,3),
  (6,'Farah',99, 65000,2),
  (7,'Gopal',10,130000,2);     -- earns more than his manager Bilal (120000)

-- ============================================
-- SOLUTION
-- ============================================

-- 1) Employee -> manager (LEFT JOIN keeps Asha, who has no manager)
SELECT e.emp_name AS employee, m.emp_name AS manager
FROM employees e
LEFT JOIN employees m ON e.manager_id = m.emp_id
ORDER BY e.emp_id;

-- 2) Employees who earn more than their manager
SELECT e.emp_name AS employee, e.salary, m.emp_name AS manager, m.salary AS manager_salary
FROM employees e
JOIN employees m ON e.manager_id = m.emp_id
WHERE e.salary > m.salary;

-- 3) Direct reports per manager (COUNT a column of the child side, not *)
SELECT m.emp_name AS manager, COUNT(e.emp_id) AS direct_reports
FROM employees m
LEFT JOIN employees e ON e.manager_id = m.emp_id
GROUP BY m.emp_id, m.emp_name
ORDER BY direct_reports DESC, m.emp_name;

-- 4) Pairs of colleagues in the same department (a.emp_id < b.emp_id removes mirror pairs and self-pairs)
SELECT a.emp_name AS emp_a, b.emp_name AS emp_b, a.dept_id
FROM employees a
JOIN employees b ON a.dept_id = b.dept_id AND a.emp_id < b.emp_id
ORDER BY a.emp_id, b.emp_id;

-- ============================================
-- EXPECTED OUTPUT (identical on MySQL 9.1 and PostgreSQL 18.6)
-- ============================================

-- 1) employee | manager      2) employee | salary | manager | manager_salary
--    Asha     | NULL            Gopal    | 130000 | Bilal   | 120000
--    Bilal    | Asha
--    Chen     | Asha         3) manager | direct_reports      4) emp_a | emp_b | dept_id
--    Divya    | Chen            Asha    | 2                      Asha  | Bilal | 10
--    Emil     | Chen            Bilal   | 2                      Asha  | Gopal | 10
--    Farah    | Bilal           Chen    | 2                      Bilal | Gopal | 10
--    Gopal    | Bilal           Divya, Emil, Farah, Gopal | 0    Chen  | Divya | 20
```

---

## 🔍 Why This Works (3 lines max)
Two aliases make the optimizer treat one table as two row sources: `e` supplies the child row and `m` the parent matched on `manager_id = emp_id`. The `<` in the pair query keeps each unordered pair once and excludes a row paired with itself.
हिंदी: दो alias = एक ही table दो बार; `a.emp_id < b.emp_id` से duplicate और self pairs हट जाते हैं।

---

## ⚡ Alternative Solution

```sql
-- Whole hierarchy with unlimited depth: recursive CTE (MySQL 8.0+ and PostgreSQL)
WITH RECURSIVE org AS (
  SELECT emp_id, emp_name, manager_id, 0 AS depth,
         CAST(emp_name AS CHAR(200)) AS path            -- PgSQL: CAST(emp_name AS TEXT)
  FROM employees WHERE manager_id IS NULL                -- anchor: the root
  UNION ALL
  SELECT e.emp_id, e.emp_name, e.manager_id, o.depth + 1,
         CONCAT(o.path, ' > ', e.emp_name)              -- PgSQL: o.path || ' > ' || e.emp_name
  FROM employees e JOIN org o ON e.manager_id = o.emp_id
)
SELECT emp_id, emp_name, depth, path FROM org ORDER BY path;
-- emp_id | emp_name | depth | path
-- 1      | Asha     | 0     | Asha
-- 2      | Bilal    | 1     | Asha > Bilal
-- 6      | Farah    | 2     | Asha > Bilal > Farah
-- 7      | Gopal    | 2     | Asha > Bilal > Gopal
-- 3      | Chen     | 1     | Asha > Chen
-- 4      | Divya    | 2     | Asha > Chen > Divya
-- 5      | Emil     | 2     | Asha > Chen > Emil

-- Fixed depth: chain self joins (employee -> manager -> grand-manager)
SELECT e.emp_name AS employee, g.emp_name AS grand_manager
FROM employees e JOIN employees m ON e.manager_id = m.emp_id JOIN employees g ON m.manager_id = g.emp_id;
-- Divya, Emil, Farah, Gopal -> Asha

-- Differences (both verified): on PostgreSQL, the anchor column type must match the recursive term exactly:
-- CAST(emp_name AS VARCHAR(200)) failed there with "column 5 has type character varying(200) in non-recursive term but type character varying overall" -> use TEXT.
-- MySQL also needs cte_max_recursion_depth (default 1000) raised for very deep trees; PostgreSQL has no such limit (cycles loop forever -> add a depth guard).
```

---

## ⚠️ Common Mistake
```sql
-- ❌ Wrong: INNER JOIN for the employee-manager list -> the CEO (NULL manager) disappears
-- ✅ Correct: LEFT JOIN employees m ON e.manager_id = m.emp_id

-- ❌ Wrong: a.emp_id <> b.emp_id for pairs -> every pair appears twice (A,B) and (B,A)
-- ✅ Correct: a.emp_id < b.emp_id

-- ❌ Wrong: COUNT(*) in the direct-reports query with a LEFT JOIN -> managers with no reports show 1
-- ❌ Wrong: forgetting aliases ("ambiguous column name") or comparing e.emp_id = m.manager_id (reversed direction)
```

---

## 🎯 Interview Tip (1 line)
Say: "A self join gives one level of hierarchy; for arbitrary depth I use a recursive CTE with a depth guard against cycles, and for read-heavy trees I'd consider closure tables, materialised path or nested sets instead of adjacency lists."

---

## 🔗 Related Questions
→ Q041 (INNER JOIN) | Q042 (LEFT JOIN NULL detection) | Q044 (FULL OUTER JOIN) | Q055 (Nth highest salary)
