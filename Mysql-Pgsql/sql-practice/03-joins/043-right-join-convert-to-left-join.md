---

# Q043. RIGHT JOIN — Convert to LEFT JOIN
# Category: Joins
# Difficulty: ⭐ Easy
# DB: Both (MySQL 8.0+ | PostgreSQL)

---

## ❓ Question
Rewrite `employees RIGHT JOIN departments` as a LEFT JOIN that returns the same rows. Why do most teams standardise on LEFT JOIN only, and what traps appear when converting with WHERE filters?

---

## 💡 Quick Concept (2 lines only)
`A RIGHT JOIN B` is exactly `B LEFT JOIN A`: swap the table order and keep the ON condition. Only the table that must keep all its rows changes position.
हिंदी: `A RIGHT JOIN B` = `B LEFT JOIN A`; बस tables की जगह बदलो, ON condition वही रहती है।

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

-- Step 1: original - keep ALL departments, show employees where present
SELECT d.dept_name, e.emp_name
FROM employees e
RIGHT JOIN departments d ON e.dept_id = d.dept_id
ORDER BY d.dept_id, e.emp_id;

-- Step 2: converted - swap the table order, change RIGHT to LEFT, same ON
SELECT d.dept_name, e.emp_name
FROM departments d
LEFT JOIN employees e ON e.dept_id = d.dept_id
ORDER BY d.dept_id, e.emp_id;

-- Step 3: unmatched-only variant keeps the same trick
SELECT d.dept_name
FROM employees e
RIGHT JOIN departments d ON e.dept_id = d.dept_id
WHERE e.emp_id IS NULL
ORDER BY 1;

-- ============================================
-- EXPECTED OUTPUT (identical for Step 1 and Step 2; verified on MySQL 9.1.0)
-- ============================================

-- dept_name   | emp_name
-- Engineering | Asha
-- Engineering | Bilal
-- Engineering | Gopal
-- Sales       | Chen
-- Sales       | Divya
-- HR          | NULL
-- Legal       | NULL
--
-- Step 3:  HR, Legal
-- (Emil and Farah are absent: they belong to no department, and the left side - departments - drives the result.)
```

---

## 🔍 Why This Works (3 lines max)
The "preserved" table is the one that keeps unmatched rows; RIGHT JOIN preserves the right-hand table, LEFT JOIN the left-hand one. Moving that table to the left and flipping the keyword preserves identical semantics while leaving the ON condition untouched.
हिंदी: जो table पूरी रखनी है उसे बाईं तरफ लाओ और RIGHT की जगह LEFT लिखो।

---

## ⚡ Alternative Solution

```sql
-- Chained joins: convert carefully. Keep the "driving" table first and keep reading order left-to-right.
-- Filter trap: this is NOT the same as the original when the WHERE hits the non-preserved table
SELECT d.dept_name, e.emp_name
FROM employees e RIGHT JOIN departments d ON e.dept_id = d.dept_id
WHERE e.salary > 100000 ORDER BY 1,2;
-- Engineering | Asha / Bilal / Gopal  (HR, Legal, Sales dropped: e.salary is NULL there -> it behaves like an INNER JOIN)
-- Fix: move the condition into ON:  RIGHT JOIN departments d ON e.dept_id = d.dept_id AND e.salary > 100000

-- Syntax: RIGHT JOIN is valid and identical in MySQL and PostgreSQL (both verified).
-- Using 'RIGHT OUTER JOIN' (the OUTER keyword is optional) is also accepted by both.
```

---

## ⚠️ Common Mistake
```sql
-- ❌ Wrong: flipping only the keyword and not the table order
SELECT * FROM employees e LEFT JOIN departments d ON e.dept_id = d.dept_id;
-- This is a DIFFERENT query: keeps all employees (incl. Emil, Farah), drops HR/Legal
-- ✅ Correct: FROM departments d LEFT JOIN employees e ON ...

-- ❌ Wrong: mixing LEFT and RIGHT joins in one query -> readers must mentally track which side is preserved
```

---

## 🎯 Interview Tip (1 line)
Say: "RIGHT JOIN is just a mirrored LEFT JOIN; I standardise on LEFT JOIN so the 'main' table is always first and the query reads top to bottom — and I double-check that WHERE filters on the optional table don't accidentally turn the outer join into an inner one."

---

## 🔗 Related Questions
→ Q041 (INNER JOIN) | Q042 (LEFT JOIN NULL detection) | Q044 (FULL OUTER JOIN) | Q045 (SELF JOIN)
