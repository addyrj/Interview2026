---

# Q014. UPDATE with JOIN (MySQL vs PgSQL Syntax Difference)
# Category: Fundamentals
# Difficulty: ⭐⭐ Medium
# DB: Both (MySQL + PostgreSQL)

---

## ❓ Question
Give every employee a raise equal to their department's `raise_pct`, only for departments with a raise greater than 0. Write it for MySQL and for PostgreSQL, show the portable correlated-subquery version, and update employees that have NO matching department.

---

## 💡 Quick Concept (2 lines only)
MySQL puts the join in the UPDATE itself: `UPDATE a JOIN b ON ... SET a.col = ...`. PostgreSQL uses `UPDATE a SET col = ... FROM b WHERE a.k = b.k` - the SET column is never table-qualified.
हिंदी: MySQL में `UPDATE a JOIN b ON ... SET a.col = ...`; PostgreSQL में `UPDATE a SET col = ... FROM b WHERE ...` और SET में column पर table prefix नहीं लगता।

---

## ✅ Answer / Solution

```sql
-- ============================================
-- SETUP (run this first - works on both engines)
-- ============================================

CREATE TABLE employees (
  id      INT PRIMARY KEY,
  name    VARCHAR(30),
  dept_id INT,
  salary  DECIMAL(10,2)
);

CREATE TABLE departments (
  id        INT PRIMARY KEY,
  name      VARCHAR(30),
  raise_pct DECIMAL(5,2)
);

INSERT INTO departments VALUES (1, 'Engineering', 10.00), (2, 'Sales', 5.00), (3, 'HR', 0.00);

INSERT INTO employees VALUES
  (1, 'Alice', 1,    100000),
  (2, 'Bob',   1,     90000),
  (3, 'Carol', 2,     70000),
  (4, 'Dave',  NULL,  50000),   -- no department
  (5, 'Eve',   9,     60000);   -- department 9 does not exist

-- ============================================
-- SOLUTION: MySQL
-- ============================================

UPDATE employees e
JOIN departments d ON d.id = e.dept_id                  -- inner join: only matching rows are touched
SET e.salary = e.salary * (1 + d.raise_pct / 100)       -- qualified target column is allowed
WHERE d.raise_pct > 0;
SELECT ROW_COUNT();                                      -- 3

-- ============================================
-- SOLUTION: PostgreSQL
-- ============================================

UPDATE employees e
SET salary = e.salary * (1 + d.raise_pct / 100)          -- NO "e." before the column being set
FROM departments d                                       -- the join table goes in FROM
WHERE d.id = e.dept_id                                   -- the join condition goes in WHERE
  AND d.raise_pct > 0;                                   -- PGlite: 3 rows affected

-- ============================================
-- EXPECTED OUTPUT (same final data on both engines)
-- ============================================

-- SELECT * FROM employees ORDER BY id;
-- id | name  | dept_id | salary
--  1 | Alice |       1 | 110000.00    <- +10%
--  2 | Bob   |       1 |  99000.00    <- +10%
--  3 | Carol |       2 |  73500.00    <- +5%
--  4 | Dave  |    NULL |  50000.00    <- unchanged (no dept)
--  5 | Eve   |       9 |  60000.00    <- unchanged (dept 9 missing)
```

---

## 🔍 Why This Works (3 lines max)
Both forms build the joined row set first, then update the target table's matching rows once per target row. Rows with no match (Dave, Eve) are never part of the inner join, so they are untouched. The WHERE filter on `raise_pct > 0` skips the HR department.
हिंदी: दोनों syntax पहले join बनाते हैं और फिर target table की matching rows update करते हैं; match न होने वाली rows (Dave, Eve) छूती नहीं।

---

## ⚡ Alternative Solution

```sql
-- Portable correlated subquery - runs on BOTH engines (note: set-to-NULL for unmatched rows if no WHERE guard!)
UPDATE employees
SET salary = salary * (1 + (SELECT d.raise_pct FROM departments d WHERE d.id = employees.dept_id) / 100)
WHERE dept_id IN (SELECT id FROM departments WHERE raise_pct > 0);
-- Same final data as above on MySQL 9.1.0 and PGlite (verified). The WHERE guard prevents NULL salaries.

-- Update rows with NO match (anti-join):
-- MySQL: LEFT JOIN + IS NULL
UPDATE employees e LEFT JOIN departments d ON d.id = e.dept_id SET e.salary = 0 WHERE d.id IS NULL;
-- MySQL result: Dave 0.00, Eve 0.00 (verified)
-- PostgreSQL / portable: NOT EXISTS
UPDATE employees e SET salary = 0 WHERE NOT EXISTS (SELECT 1 FROM departments d WHERE d.id = e.dept_id);
-- PGlite: 2 rows affected, Dave and Eve = 0.00 (verified)

-- Syntax cross-check (verified): the other engine's form is rejected
--   MySQL 9.1.0: UPDATE ... SET ... FROM departments d WHERE ...   -> ERROR 1064 near 'FROM departments'
--   PGlite:      UPDATE employees e JOIN departments d ...         -> ERROR: syntax error at or near "JOIN"
--   PGlite:      UPDATE employees e SET e.salary = 1 FROM ...      -> ERROR: column "e" of relation "employees" does not exist
-- MySQL also allows UPDATE ... ORDER BY ... LIMIT on single-table updates; PGlite: syntax error at "ORDER" (verified).
```

---

## ⚠️ Common Mistake

```sql
-- ❌ Wrong (PostgreSQL): forgetting the join condition in WHERE -> a cross join
UPDATE employees SET salary = salary * 1.1 FROM departments;
-- PGlite: 5 rows affected - EVERY employee got a raise, picked against an arbitrary department row
-- ✅ Always: ... FROM departments d WHERE d.id = employees.dept_id

-- ❌ Wrong: join matches MANY rows per target row (e.g. joining to a one-to-many table).
--    Both engines update the target row only ONCE and pick an arbitrary matching row - silent, nondeterministic.
-- ✅ Join to a de-duplicated / aggregated derived table so each target row matches at most one row

-- ❌ Wrong: running a big UPDATE-JOIN with no WHERE/transaction on production
-- ✅ Preview with SELECT using the same joins, wrap in BEGIN ... ROLLBACK first, check ROW_COUNT / affected rows
```

---

## 🎯 Interview Tip (1 line)
Say: "MySQL joins in the UPDATE clause, PostgreSQL uses UPDATE ... FROM with the join in WHERE; I always preview with a SELECT, make sure the join is one-to-one, and run it in a transaction."

---

## 🔗 Related Questions
→ Q013 (Upsert) | Q015 (DELETE vs TRUNCATE vs DROP) | Q005 (IN vs EXISTS) | Q239 (Find duplicates, DELETE with JOIN/USING)
