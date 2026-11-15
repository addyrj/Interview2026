---

# Q042. LEFT JOIN with NULL Detection
# Category: Joins
# Difficulty: ⭐⭐ Medium
# DB: Both (MySQL 8.0+ | PostgreSQL)

---

## ❓ Question
Find (a) departments that have no employees, (b) employees whose department does not exist (orphans or NULL dept). Explain why a filter in WHERE vs ON changes a LEFT JOIN, and why `NOT IN` can return nothing.

---

## 💡 Quick Concept (2 lines only)
LEFT JOIN keeps every left row and fills right columns with NULL when nothing matches; `WHERE right.pk IS NULL` then isolates the unmatched ("anti-join"). Filters on right-table columns belong in ON, or the LEFT JOIN turns into an INNER JOIN.
हिंदी: LEFT JOIN में unmatched right columns NULL आते हैं; `WHERE right.pk IS NULL` से unmatched rows मिलती हैं।

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
-- SOLUTION
-- ============================================

-- (a) Departments with no employees (anti-join)
SELECT d.dept_id, d.dept_name
FROM departments d
LEFT JOIN employees e ON e.dept_id = d.dept_id
WHERE e.emp_id IS NULL            -- test the right table's PRIMARY KEY, never a nullable column
ORDER BY d.dept_id;

-- (b) Employees without a valid department
SELECT e.emp_id, e.emp_name, e.dept_id
FROM employees e
LEFT JOIN departments d ON d.dept_id = e.dept_id
WHERE d.dept_id IS NULL
ORDER BY e.emp_id;

-- (c) WHERE vs ON for a right-table filter (salary > 100000)
SELECT d.dept_name, e.emp_name FROM departments d
LEFT JOIN employees e ON e.dept_id = d.dept_id
WHERE e.salary > 100000 ORDER BY 1,2;            -- WHERE: HR/Legal/Sales vanish (becomes inner join)

SELECT d.dept_name, e.emp_name FROM departments d
LEFT JOIN employees e ON e.dept_id = d.dept_id AND e.salary > 100000
ORDER BY 1,2;                                    -- ON: all departments kept

-- ============================================
-- EXPECTED OUTPUT (identical on MySQL 9.1 and PostgreSQL 18)
-- ============================================

-- (a)  dept_id | dept_name       (b)  emp_id | emp_name | dept_id
--      30      | HR                   5      | Emil     | NULL
--      40      | Legal                6      | Farah    | 99
--
-- (c) WHERE version:                (c) ON version:
--      Engineering | Asha                Engineering | Asha
--      Engineering | Bilal               Engineering | Bilal
--      Engineering | Gopal               Engineering | Gopal
--                                          HR          | NULL
--                                          Legal       | NULL
--                                          Sales       | NULL
```

---

## 🔍 Why This Works (3 lines max)
Unmatched left rows survive with all right columns NULL, so a NULL primary key on the right can only mean "no match". A WHERE condition on a right column is evaluated after the join, and NULL fails `> 100000`, so those preserved rows are thrown away; in ON the filter only decides what matches.
हिंदी: Right-table का filter WHERE में डालोगे तो NULL rows हट जाती हैं; ON में डालो तो LEFT JOIN बना रहता है।

---

## ⚡ Alternative Solution

```sql
-- NOT EXISTS: same result as the anti-join, NULL-safe, often the clearest (verified: HR, Legal)
SELECT d.dept_name FROM departments d
WHERE NOT EXISTS (SELECT 1 FROM employees e WHERE e.dept_id = d.dept_id) ORDER BY 1;

-- Count per department: COUNT(e.emp_id) not COUNT(*)
SELECT d.dept_name, COUNT(*) AS wrong_count, COUNT(e.emp_id) AS right_count
FROM departments d LEFT JOIN employees e ON e.dept_id = d.dept_id
GROUP BY d.dept_name ORDER BY 1;
-- Engineering | 3 | 3
-- HR          | 1 | 0     <- COUNT(*) counts the NULL-extended row
-- Legal       | 1 | 0
-- Sales       | 2 | 2

-- Syntax: identical on MySQL and PgSQL. PgSQL could also use EXCEPT; MySQL supports EXCEPT from 8.0.31.
```

---

## ⚠️ Common Mistake
```sql
-- ❌ Wrong: NOT IN with a subquery that contains NULL -> returns ZERO rows (verified on both engines)
SELECT dept_name FROM departments WHERE dept_id NOT IN (SELECT dept_id FROM employees);
-- employees.dept_id contains NULL (Emil), so "dept_id <> NULL" is unknown for every row
-- ✅ Correct: NOT EXISTS or LEFT JOIN ... IS NULL

-- ❌ Wrong: WHERE e.dept_id IS NULL after LEFT JOIN from departments (checks a nullable FK, may hide real matches)
-- ❌ Wrong: COUNT(*) after LEFT JOIN -> counts unmatched rows as 1
```

---

## 🎯 Interview Tip (1 line)
Say: "For 'rows with no match' I use NOT EXISTS or LEFT JOIN with IS NULL on the right table's primary key, never NOT IN over a nullable column, and I put right-table filters in the ON clause so the LEFT JOIN semantics survive."

---

## 🔗 Related Questions
→ Q041 (INNER JOIN) | Q043 (RIGHT JOIN) | Q044 (FULL OUTER JOIN) | Q239 (Find duplicates)
