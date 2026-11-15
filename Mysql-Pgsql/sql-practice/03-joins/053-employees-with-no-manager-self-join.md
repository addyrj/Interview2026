---

# Q053. Employees With No Manager (Self Join)
# Category: Joins
# Difficulty: ⭐⭐ Medium
# DB: Both (MySQL + PostgreSQL)

---

## ❓ Question
In an employees table where manager_id points to another employee, list employees who have no manager (top of the org). Also list employees whose manager_id points to a row that does not exist (orphans), and show each employee with their manager's name.

---

## 💡 Quick Concept (2 lines only)
A self join aliases the same table twice (e for employee, m for manager) on `e.manager_id = m.employee_id`. "No manager" is simply `manager_id IS NULL` - no join needed; "orphans" need a LEFT self join where the manager side comes back NULL.
हिंदी: Self join = वही table दो alias से। "No manager" = manager_id IS NULL। Orphan ढूँढने के लिए LEFT JOIN + manager side NULL।

---

## ✅ Answer / Solution

```sql
-- ============================================
-- SETUP (run this first)
-- ============================================

CREATE TABLE employees (
  employee_id INT PRIMARY KEY,
  name        VARCHAR(100),
  title       VARCHAR(50),
  manager_id  INT,                       -- NULL = top of the hierarchy
  FOREIGN KEY (manager_id) REFERENCES employees (employee_id)
);

INSERT INTO employees VALUES (1, 'Neha',   'CEO',          NULL);   -- no manager
INSERT INTO employees VALUES (2, 'Arjun',  'VP Eng',       1);
INSERT INTO employees VALUES (3, 'Kavya',  'Eng Manager',  2);
INSERT INTO employees VALUES (4, 'Dev',    'Engineer',     3);
INSERT INTO employees VALUES (5, 'Isha',   'Engineer',     3);
INSERT INTO employees VALUES (6, 'Sameer', 'Contractor',   NULL);   -- also no manager

-- ============================================
-- SOLUTION 1: employees with no manager
-- ============================================

SELECT employee_id, name, title
FROM employees
WHERE manager_id IS NULL        -- use IS NULL, never = NULL
ORDER BY employee_id;
-- Output:
-- employee_id | name   | title
-- 1           | Neha   | CEO
-- 6           | Sameer | Contractor

-- ============================================
-- SOLUTION 2: every employee with manager name (LEFT self join keeps the top people)
-- ============================================

SELECT e.name       AS employee,
       e.title,
       m.name       AS manager        -- NULL for Neha and Sameer
FROM employees e
LEFT JOIN employees m ON m.employee_id = e.manager_id
ORDER BY e.employee_id;
-- Output:
-- employee | title       | manager
-- Neha     | CEO         | NULL
-- Arjun    | VP Eng      | Neha
-- Kavya    | Eng Manager | Arjun
-- Dev      | Engineer    | Kavya
-- Isha     | Engineer    | Kavya
-- Sameer   | Contractor  | NULL

-- ============================================
-- SOLUTION 3: the same "no manager" via the join (works for any data shape)
-- ============================================

SELECT e.name
FROM employees e
LEFT JOIN employees m ON m.employee_id = e.manager_id
WHERE m.employee_id IS NULL            -- true for NULL manager_id AND for orphaned ids
ORDER BY e.employee_id;
-- Output:
-- name
-- Neha
-- Sameer

-- ============================================
-- MANAGERS ONLY: employees who have at least one report
-- ============================================

SELECT m.name AS manager, COUNT(e.employee_id) AS direct_reports
FROM employees m
JOIN employees e ON e.manager_id = m.employee_id
GROUP BY m.employee_id, m.name
ORDER BY m.name;
-- Output:
-- manager | direct_reports
-- Arjun   | 1
-- Kavya   | 2
-- Neha    | 1

-- ============================================
-- LEAF EMPLOYEES: nobody reports to them
-- ============================================

SELECT e.name
FROM employees e
WHERE NOT EXISTS (SELECT 1 FROM employees r WHERE r.manager_id = e.employee_id)
ORDER BY e.employee_id;
-- Output:
-- name
-- Dev
-- Isha
-- Sameer
```

---

## 🔍 Why This Works (3 lines max)
Aliasing the table twice lets one row play "employee" and another play "manager". Because the top-level rows have no manager, the join must be LEFT or they vanish; with the FK in place, `manager_id IS NULL` is the simplest root test, while `m.employee_id IS NULL` after the LEFT JOIN also catches dangling ids.
हिंदी: एक table दो बार alias करके employee और manager बनते हैं। Top लोगों के लिए LEFT JOIN ज़रूरी, वरना वे result से गायब।

---

## ⚡ Alternative Solution

```sql
-- Walk the whole tree from the roots with a recursive CTE (MySQL 8+ and PostgreSQL), with depth
WITH RECURSIVE chain AS (
  SELECT employee_id, name, manager_id, 0 AS depth
  FROM employees
  WHERE manager_id IS NULL                        -- anchor: the roots
  UNION ALL
  SELECT e.employee_id, e.name, e.manager_id, c.depth + 1
  FROM employees e
  JOIN chain c ON e.manager_id = c.employee_id    -- walk down
)
SELECT employee_id, name, depth FROM chain ORDER BY depth, employee_id;
-- Output:
-- employee_id | name   | depth
-- 1           | Neha   | 0
-- 6           | Sameer | 0
-- 2           | Arjun  | 1
-- 3           | Kavya  | 2
-- 4           | Dev    | 3
-- 5           | Isha   | 3

-- Syntax note: PostgreSQL requires the RECURSIVE keyword; MySQL 8+ accepts it too (and requires it).
-- Orphans (manager_id pointing nowhere) only exist if the FK is missing; Solution 3 would list them.
```

---

## ⚠️ Common Mistake

```sql
-- ❌ Wrong: comparing to NULL with =
SELECT * FROM employees WHERE manager_id = NULL;     -- always 0 rows (UNKNOWN)
-- ✅ WHERE manager_id IS NULL

-- ❌ Wrong: INNER self join to list everyone with manager name
SELECT e.name, m.name FROM employees e JOIN employees m ON m.employee_id = e.manager_id;
-- Neha and Sameer disappear (no manager row to match)
-- ✅ LEFT JOIN

-- ❌ Wrong: using 0 or -1 instead of NULL for "no manager" -> breaks the foreign key
```

---

## 🎯 Interview Tip (1 line)
Say: "Roots are `manager_id IS NULL` - no join needed; for the full tree I use a LEFT self join for one level or a recursive CTE for arbitrary depth, and I enforce the hierarchy with a self-referencing foreign key plus an index on manager_id."

---

## 🔗 Related Questions
→ Q045 (SELF JOIN hierarchical data) | Q042 (LEFT JOIN with NULL detection) | Q052 (A not in B) | Q049 (JOIN vs subquery)
