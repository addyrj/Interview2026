---

# Q044. FULL OUTER JOIN (MySQL Workaround)
# Category: Joins
# Difficulty: ⭐⭐ Medium
# DB: Both (MySQL has no FULL JOIN | PostgreSQL native)

---

## ❓ Question
List every employee and every department together, matched where possible: employees without a department AND departments without employees must both appear. PostgreSQL has `FULL OUTER JOIN`; how do you do it in MySQL?

---

## 💡 Quick Concept (2 lines only)
FULL OUTER JOIN = LEFT JOIN rows + RIGHT JOIN rows with duplicates removed. MySQL lacks the keyword, so emulate with `LEFT JOIN UNION RIGHT JOIN` (or UNION ALL plus an anti-join to avoid duplicates).
हिंदी: FULL OUTER JOIN = LEFT + RIGHT का union; MySQL में keyword नहीं है, इसलिए UNION से बनाओ।

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
  (1,'Asha',10,150000,NULL),(2,'Bilal',10,120000,1),(3,'Chen',20,90000,1),(4,'Divya',20,85000,3),
  (5,'Emil',NULL,70000,3),(6,'Farah',99,65000,2),(7,'Gopal',10,110000,2);

-- ============================================
-- SOLUTION — MySQL (works on PostgreSQL too)
-- ============================================

-- Step 1: LEFT JOIN gives all employees; RIGHT JOIN gives all departments; UNION removes the duplicated matches.
-- Wrapped in a subquery so the NULL ordering is explicit and portable.
SELECT * FROM (
  SELECT e.emp_name, d.dept_name
  FROM employees e LEFT JOIN departments d ON e.dept_id = d.dept_id
  UNION
  SELECT e.emp_name, d.dept_name
  FROM employees e RIGHT JOIN departments d ON e.dept_id = d.dept_id
) fo
ORDER BY emp_name IS NULL, emp_name, dept_name;   -- NULLs last on both engines

-- Step 2: lighter variant - UNION ALL + anti-join (no dedupe sort; safe when rows aren't fully identical)
SELECT e.emp_name, d.dept_name
FROM employees e LEFT JOIN departments d ON e.dept_id = d.dept_id
UNION ALL
SELECT NULL, d.dept_name
FROM departments d LEFT JOIN employees e ON e.dept_id = d.dept_id
WHERE e.emp_id IS NULL;

-- ============================================
-- EXPECTED OUTPUT (Step 1; verified on MySQL 9.1.0 and PostgreSQL 18.6)
-- ============================================

-- emp_name | dept_name
-- Asha     | Engineering
-- Bilal    | Engineering
-- Chen     | Sales
-- Divya    | Sales
-- Emil     | NULL          <- employee, no department
-- Farah    | NULL          <- employee, dept 99 doesn't exist
-- Gopal    | Engineering
-- NULL     | HR            <- department, no employees
-- NULL     | Legal
```

---

## 🔍 Why This Works (3 lines max)
LEFT JOIN covers (matched + employee-only), RIGHT JOIN covers (matched + department-only); UNION merges and drops the duplicated "matched" rows. Step 2 avoids UNION's dedupe by adding only department-only rows from a second anti-join.
हिंदी: LEFT और RIGHT का union करने से matched rows एक बार और बाकी दोनों तरफ की unmatched rows आ जाती हैं।

---

## ⚡ Alternative Solution

```sql
-- PostgreSQL (native, verified on 18.6)
SELECT e.emp_name, d.dept_name
FROM employees e FULL OUTER JOIN departments d ON e.dept_id = d.dept_id
ORDER BY e.emp_name NULLS LAST, d.dept_name;     -- same 9 rows

-- Tag which side each row comes from:
SELECT e.emp_name, d.dept_name,
  CASE WHEN e.emp_id IS NULL THEN 'dept only' WHEN d.dept_id IS NULL THEN 'emp only' ELSE 'both' END AS side
FROM employees e FULL JOIN departments d ON e.dept_id = d.dept_id;

-- Only the mismatches (symmetric difference):
SELECT e.emp_name, d.dept_name FROM employees e FULL JOIN departments d ON e.dept_id = d.dept_id
WHERE e.emp_id IS NULL OR d.dept_id IS NULL;
-- Emil|NULL, Farah|NULL, NULL|HR, NULL|Legal

-- MySQL 9.1.0 on FULL JOIN / FULL OUTER JOIN: ERROR 1064 (42000) You have an error in your SQL syntax  (verified)
-- Ordering note: MySQL sorts NULLs FIRST in ASC order, PostgreSQL sorts them LAST - that's why Step 1 uses ORDER BY x IS NULL.
-- PgSQL caveat: FULL JOIN only works with merge-joinable/hashable conditions (equality); not with arbitrary ON expressions.
```

---

## ⚠️ Common Mistake
```sql
-- ❌ Wrong: UNION ALL of LEFT JOIN and RIGHT JOIN -> 14 rows instead of 9 (the 5 matched pairs appear twice; verified)
-- ❌ Wrong: UNION when rows may legitimately repeat (two identical employee/department pairs) -> UNION collapses real duplicates
-- ✅ Correct: LEFT JOIN UNION ALL (right anti-join) as in Step 2, which never collapses legitimate duplicates
-- ❌ Wrong: relying on default ORDER with NULLs and expecting the same order on MySQL and PostgreSQL
```

---

## 🎯 Interview Tip (1 line)
Say: "MySQL has no FULL JOIN, so I emulate it with LEFT JOIN UNION ALL a right-side anti-join to keep legitimate duplicates; on PostgreSQL I use native FULL OUTER JOIN, usually for reconciliation between two systems — finding rows missing on either side."

---

## 🔗 Related Questions
→ Q041 (INNER JOIN) | Q042 (LEFT JOIN NULL detection) | Q043 (RIGHT JOIN) | Q045 (SELF JOIN)
