---

# Q030. Constraints — PRIMARY KEY, UNIQUE, NOT NULL, CHECK, DEFAULT
# Category: Data Types & DDL
# Difficulty: ⭐⭐ Medium
# DB: Both (CHECK enforced from MySQL 8.0.16)

---

## ❓ Question
Define an `employees` table using PRIMARY KEY, UNIQUE, NOT NULL, CHECK, DEFAULT and a FOREIGN KEY. Show what error each constraint raises, how NULLs behave in UNIQUE and CHECK, and the MySQL vs PostgreSQL differences.

---

## 💡 Quick Concept (2 lines only)
Constraints make the database itself reject bad data: PRIMARY KEY (unique + not null, one per table), UNIQUE (no duplicate non-NULL values), NOT NULL, CHECK (boolean rule per row), DEFAULT (value when omitted) and FOREIGN KEY (row must reference an existing parent). They are your last line of defence when application code has bugs.
हिंदी: Constraints database लेवल पर गलत data रोकते हैं — PK/UNIQUE/NOT NULL/CHECK/DEFAULT/FK।

---

## ✅ Answer / Solution

```sql
-- ============================================
-- SETUP (run this first; MySQL 8.0.16+ / PostgreSQL — for PgSQL write NUMERIC instead of DECIMAL if you prefer)
-- ============================================

CREATE TABLE departments (
  id   INT PRIMARY KEY,
  name VARCHAR(50) NOT NULL UNIQUE
);

CREATE TABLE employees (
  id         INT PRIMARY KEY,                               -- unique + NOT NULL, one per table
  email      VARCHAR(100) NOT NULL,
  name       VARCHAR(100) NOT NULL,
  salary     DECIMAL(10,2) NOT NULL DEFAULT 30000.00,       -- DEFAULT used when column is omitted
  status     VARCHAR(10)   NOT NULL DEFAULT 'active',
  dept_id    INT,                                           -- nullable FK = "no department yet"
  joined_on  DATE,
  CONSTRAINT uq_emp_email   UNIQUE (email),                 -- name constraints: error messages & ALTER get clearer
  CONSTRAINT chk_emp_salary CHECK (salary >= 0),
  CONSTRAINT chk_emp_status CHECK (status IN ('active','inactive')),
  CONSTRAINT fk_emp_dept    FOREIGN KEY (dept_id) REFERENCES departments(id)
);

INSERT INTO departments VALUES (1, 'Engineering'), (2, 'Sales');
INSERT INTO employees (id, email, name, dept_id) VALUES (1, 'asha@corp.com', 'Asha', 1);

SELECT id, email, salary, status FROM employees;
-- id | email         | salary   | status
-- 1  | asha@corp.com | 30000.00 | active          <- salary and status came from DEFAULT

-- ============================================
-- SOLUTION: each violation and its error (each statement run on its own)
-- ============================================

-- PRIMARY KEY duplicate
INSERT INTO employees (id,email,name) VALUES (1,'x@corp.com','X');
-- MySQL: ERROR 1062 (23000): Duplicate entry '1' for key 'employees.PRIMARY'
-- PgSQL: ERROR: duplicate key value violates unique constraint "employees_pkey"

-- UNIQUE duplicate
INSERT INTO employees (id,email,name) VALUES (2,'asha@corp.com','Dup');
-- MySQL: ERROR 1062 (23000): Duplicate entry 'asha@corp.com' for key 'employees.uq_emp_email'
-- PgSQL: ERROR: duplicate key value violates unique constraint "uq_emp_email"

-- NOT NULL
INSERT INTO employees (id,email,name) VALUES (3,NULL,'NoEmail');
-- MySQL: ERROR 1048 (23000): Column 'email' cannot be null
-- PgSQL: ERROR: null value in column "email" of relation "employees" violates not-null constraint

-- CHECK
INSERT INTO employees (id,email,name,salary) VALUES (4,'neg@corp.com','Neg',-5);
-- MySQL: ERROR 3819 (HY000): Check constraint 'chk_emp_salary' is violated.
-- PgSQL: ERROR: new row for relation "employees" violates check constraint "chk_emp_salary"
INSERT INTO employees (id,email,name,status) VALUES (5,'st@corp.com','St','retired');
-- MySQL: ERROR 3819 ... 'chk_emp_status' is violated.   PgSQL: ... violates check constraint "chk_emp_status"

-- FOREIGN KEY: child side and parent side
INSERT INTO employees (id,email,name,dept_id) VALUES (6,'fk@corp.com','Fk',99);
-- MySQL: ERROR 1452 (23000): Cannot add or update a child row: a foreign key constraint fails (...)
-- PgSQL: ERROR: insert or update on table "employees" violates foreign key constraint "fk_emp_dept"
DELETE FROM departments WHERE id = 1;
-- MySQL: ERROR 1451 (23000): Cannot delete or update a parent row: a foreign key constraint fails (...)
-- PgSQL: ERROR: update or delete on table "departments" violates foreign key constraint "fk_emp_dept" on table "employees"

-- NULL is allowed in UNIQUE (multiple NULLs OK) — and passes CHECK (NULL = unknown, not false)
-- (here joined_on is NULL for both rows; the UNIQUE one is shown with a composite key below)
INSERT INTO employees (id,email,name,joined_on) VALUES (7,'ok1@corp.com','Ok1',NULL);
INSERT INTO employees (id,email,name,joined_on) VALUES (8,'ok2@corp.com','Ok2',NULL);

CREATE TABLE tmp_u (a INT, b INT, UNIQUE (a,b));
INSERT INTO tmp_u VALUES (1,NULL),(1,NULL);
SELECT COUNT(*) AS rows_with_null_dups FROM tmp_u;
-- rows_with_null_dups = 2          (both engines)

SELECT id, email, salary, status FROM employees ORDER BY id;
-- id | email         | salary   | status
-- 1  | asha@corp.com | 30000.00 | active
-- 7  | ok1@corp.com  | 30000.00 | active
-- 8  | ok2@corp.com  | 30000.00 | active

-- ============================================
-- EXPECTED OUTPUT
-- ============================================
-- Every error message above is the real text from MySQL 9.1.0 and PostgreSQL 18 (PGlite),
-- with the setup using DECIMAL(10,2) on MySQL and NUMERIC(10,2) on PGlite (identical in PgSQL).
-- In MySQL the FK error text also lists `q30`.`employees` etc. (schema name) — trimmed with "(...)".
```

---

## 🔍 Why This Works (3 lines max)
Constraints are checked per statement inside the engine, atomically with the write, so no race or buggy client can bypass them. UNIQUE and CHECK use SQL three-valued logic: a NULL makes a UNIQUE comparison "unknown" (so it never conflicts) and a CHECK evaluate to unknown (which passes) — you must add NOT NULL when NULL should be rejected.
हिंदी: Constraint engine के अंदर चलते हैं; NULL UNIQUE में duplicate नहीं गिना जाता और CHECK में pass हो जाता है।

---

## ⚡ Alternative Solution

```sql
-- Adding / removing constraints on an existing table
ALTER TABLE employees ADD CONSTRAINT chk_future CHECK (joined_on <= CURRENT_DATE) NOT VALID;  -- PgSQL: skip scanning old rows
ALTER TABLE employees VALIDATE CONSTRAINT chk_future;                                          -- PgSQL: validate later, weak lock
ALTER TABLE employees DROP CONSTRAINT chk_emp_salary;                                          -- both (MySQL 8.0.19+ for CHECK)
-- MySQL drops: DROP PRIMARY KEY / DROP INDEX uq_emp_email / DROP FOREIGN KEY fk_emp_dept (older syntax)
-- MySQL: CHECK ... NOT ENFORCED is possible, but expressions are restricted (CURDATE() is disallowed:
--        ERROR 3814 "contains disallowed function: curdate") — use deterministic expressions only.

-- PgSQL 15+: treat NULLs as equal in UNIQUE
CREATE TABLE tmp_u2 (a INT, b INT, UNIQUE NULLS NOT DISTINCT (a,b));
INSERT INTO tmp_u2 VALUES (1,NULL),(1,NULL);
-- ERROR: duplicate key value violates unique constraint "tmp_u2_a_b_key"     (MySQL has no equivalent; use a generated column)

-- FK actions: ON DELETE CASCADE | SET NULL | RESTRICT (default NO ACTION); MySQL InnoDB only.
-- Partial uniqueness (PgSQL): CREATE UNIQUE INDEX ON employees (email) WHERE status = 'active';
-- MySQL < 8.0.16 parsed CHECK but IGNORED it (silently) — old servers need triggers.
-- Always index FK columns yourself in PgSQL (MySQL creates the index automatically).
```

---

## ⚠️ Common Mistake

```sql
-- ❌ Wrong: relying on CHECK to reject NULL
salary DECIMAL(10,2) CHECK (salary >= 0)        -- NULL passes! (verified: INSERT NULL succeeds in both)
-- ✅ Correct: salary DECIMAL(10,2) NOT NULL CHECK (salary >= 0)

-- ❌ Wrong: expecting UNIQUE(email) to forbid multiple NULL emails (it allows them) — use NOT NULL
-- ❌ Wrong: enforcing uniqueness only in application code (race: two concurrent inserts both pass the SELECT check)
-- ❌ Wrong: unnamed constraints => cryptic generated names in errors and migrations
-- ❌ Wrong: adding a FOREIGN KEY with mismatched types (INT vs BIGINT / signed vs unsigned) — fails or is slow

-- ✅ Correct: name every constraint, combine NOT NULL + CHECK, and keep the DB as source of truth
```

---

## 🎯 Interview Tip (1 line)
Say: "I enforce invariants in the database — PK, UNIQUE, NOT NULL, CHECK and FKs with explicit names — because app-level checks race; I remember NULL passes CHECK and UNIQUE, so I pair them with NOT NULL, and on MySQL I confirm the version since CHECK was ignored before 8.0.16."

---

## 🔗 Related Questions
→ Q026 (ENUM vs CHECK vs lookup table) | Q029 (IDENTITY / AUTO_INCREMENT) | Q028 (UUID PKs) | Q239 (Find duplicates before adding UNIQUE)
