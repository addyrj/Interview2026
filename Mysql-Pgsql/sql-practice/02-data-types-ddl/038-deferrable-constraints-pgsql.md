---

# Q038. DEFERRABLE Constraints (PgSQL)
# Category: Data Types & DDL
# Difficulty: ⭐⭐⭐ Hard
# DB: PostgreSQL (MySQL has no deferred constraints)

---

## ❓ Question
How do you swap two rows' `position` values under a UNIQUE constraint, or insert two rows that reference each other (department head and employee), without violating the constraint mid-transaction? Explain DEFERRABLE, INITIALLY DEFERRED/IMMEDIATE and `SET CONSTRAINTS`, and how to do it on MySQL.

---

## 💡 Quick Concept (2 lines only)
A DEFERRABLE constraint can be checked at COMMIT instead of after each statement (`SET CONSTRAINTS name DEFERRED`). Only UNIQUE, PRIMARY KEY, FOREIGN KEY and EXCLUDE can be deferrable; CHECK and NOT NULL cannot.
हिंदी: DEFERRABLE constraint की जांच statement के बाद नहीं, COMMIT पर होती है — circular FK और swap के लिए ज़रूरी।

---

## ✅ Answer / Solution

```sql
-- ============================================
-- SETUP (PostgreSQL; verified on PGlite = PostgreSQL 18.6)
-- ============================================

CREATE TABLE playlist_def (
  id       INT PRIMARY KEY,
  position INT NOT NULL,
  title    TEXT,
  CONSTRAINT uq_pos_def UNIQUE (position) DEFERRABLE INITIALLY IMMEDIATE
);
INSERT INTO playlist_def VALUES (1,1,'Intro'),(2,2,'Verse'),(3,3,'Chorus');

-- ============================================
-- SOLUTION — swap positions of Verse and Chorus
-- ============================================

-- Step 1: IMMEDIATE (default) mode checks per statement -> the first UPDATE already collides
BEGIN;
UPDATE playlist_def SET position = 3 WHERE id = 2;
-- ERROR: duplicate key value violates unique constraint "uq_pos_def"
ROLLBACK;

-- Step 2: defer the check to COMMIT
BEGIN;
SET CONSTRAINTS uq_pos_def DEFERRED;
UPDATE playlist_def SET position = 3 WHERE id = 2;    -- temporarily duplicate: allowed
UPDATE playlist_def SET position = 2 WHERE id = 3;    -- now consistent again
COMMIT;                                               -- constraint checked here: passes

SELECT * FROM playlist_def ORDER BY position;

-- Step 3: bonus - a DEFERRABLE (even INITIALLY IMMEDIATE) UNIQUE is checked at END OF STATEMENT,
-- so a bulk shift works without any SET CONSTRAINTS:
UPDATE playlist_def SET position = position + 1 WHERE position >= 2;
SELECT * FROM playlist_def ORDER BY position;

-- ============================================
-- EXPECTED OUTPUT
-- ============================================

-- After the swap:
-- id | position | title
-- 1  | 1        | Intro
-- 3  | 2        | Chorus
-- 2  | 3        | Verse
--
-- After the bulk +1 shift (a NON-deferrable UNIQUE fails the same UPDATE with
-- "duplicate key value violates unique constraint" — verified):
-- id | position | title
-- 1  | 1        | Intro
-- 3  | 3        | Chorus
-- 2  | 4        | Verse
```

---

## 🔍 Why This Works (3 lines max)
Normal UNIQUE/FK checks happen immediately, row by row for non-deferrable unique indexes. A deferrable constraint queues its checks and runs them at COMMIT (or end of statement if IMMEDIATE), so intermediate states may be invalid as long as the final state is valid.
हिंदी: Intermediate state गलत हो सकती है, बस COMMIT पर final state सही होनी चाहिए।

---

## ⚡ Alternative Solution

```sql
-- Circular foreign keys (department.head -> employee, employee.dept -> department)
CREATE TABLE departments (id INT PRIMARY KEY, name TEXT NOT NULL, head_emp_id INT);
CREATE TABLE employees (
  id INT PRIMARY KEY, name TEXT NOT NULL, dept_id INT NOT NULL,
  CONSTRAINT fk_emp_dept FOREIGN KEY (dept_id) REFERENCES departments(id) DEFERRABLE INITIALLY IMMEDIATE
);
ALTER TABLE departments ADD CONSTRAINT fk_dept_head
  FOREIGN KEY (head_emp_id) REFERENCES employees(id) DEFERRABLE INITIALLY DEFERRED;

INSERT INTO departments VALUES (1,'Engineering',100);   -- ERROR (autocommit: checked at its own commit; employee 100 missing)
BEGIN;
INSERT INTO departments VALUES (1,'Engineering',100);   -- head 100 doesn't exist yet: OK, deferred
INSERT INTO employees   VALUES (100,'Asha',1);
COMMIT;                                                 -- both exist: passes
-- A transaction that never inserts employee 200 but inserts department (2,'Sales',200) fails AT COMMIT with the FK error.

-- Verified: a deferred duplicate (INSERT (9,1,'Dup')) passes the statement and errors at COMMIT.

-- MySQL (verified 9.1.0): no deferrable constraints. Setup: CREATE TABLE playlist (id INT PRIMARY KEY, position INT NOT NULL,
--   title VARCHAR(50), UNIQUE KEY uq_pos (position)); with the same 3 rows. Options:
UPDATE playlist SET position = position + 1 WHERE position >= 2 ORDER BY position DESC;   -- works: shift from the top
-- (without ORDER BY DESC: ERROR 1062 Duplicate entry '3' for key 'playlist.uq_pos')
--  * swap using a temporary value (e.g. 0 or -1), or
--  * SET FOREIGN_KEY_CHECKS=0 for circular FKs (DANGEROUS: disables validation, session-wide; verified it lets
--    the circular pair be inserted; you must re-verify data yourself)
```

---

## ⚠️ Common Mistake
```sql
-- ❌ Wrong: assuming constraints are deferrable by default (they are NOT; default is NOT DEFERRABLE)
-- ❌ Wrong: SET CONSTRAINTS outside a transaction block (no effect in autocommit)
-- ❌ Wrong: forgetting the bug is reported at COMMIT, not at the offending statement -> hard to debug
-- ✅ Correct: use INITIALLY IMMEDIATE + SET CONSTRAINTS ... DEFERRED only in the specific transaction that needs it
SET CONSTRAINTS ALL DEFERRED;   -- affects all deferrable constraints in the current transaction
```

---

## 🎯 Interview Tip (1 line)
Say: "In PostgreSQL I mark the constraint DEFERRABLE INITIALLY IMMEDIATE and defer it only inside the transaction that needs it — for row reordering or circular FKs — knowing errors then surface at COMMIT; on MySQL I'd use ORDER BY in the UPDATE, temp values, or restructure the model."

---

## 🔗 Related Questions
→ Q031 (Foreign keys) | Q037 (CHECK constraints) | Q242 (SELECT FOR UPDATE) | Transactions & isolation
