---

# Q015. DELETE vs TRUNCATE vs DROP
# Category: Fundamentals
# Difficulty: ⭐⭐ Medium
# DB: Both (MySQL + PostgreSQL)

---

## ❓ Question
Explain the difference between DELETE, TRUNCATE and DROP: what each removes, whether it can use WHERE, whether it can be rolled back, what happens to AUTO_INCREMENT / SERIAL counters, and how foreign keys affect TRUNCATE. The key trap: TRUNCATE is transactional in PostgreSQL but not in MySQL.

---

## 💡 Quick Concept (2 lines only)
DELETE removes rows (DML, supports WHERE, row-by-row, fully logged); TRUNCATE empties the whole table quickly (DDL-like, no WHERE); DROP removes the table itself (structure, indexes, data). MySQL TRUNCATE and DROP auto-commit; PostgreSQL TRUNCATE and DROP can be rolled back.
हिंदी: DELETE = rows हटाओ (WHERE चलता है), TRUNCATE = पूरी table खाली (तेज़, WHERE नहीं), DROP = table ही खत्म। MySQL में TRUNCATE rollback नहीं होता, PostgreSQL में होता है।

---

## ✅ Answer / Solution

```sql
-- ============================================
-- SETUP (MySQL version; PostgreSQL: use  id SERIAL PRIMARY KEY  instead of INT ... AUTO_INCREMENT)
-- ============================================

CREATE TABLE audit_log (
  id  INT PRIMARY KEY AUTO_INCREMENT,
  msg VARCHAR(30)
);
INSERT INTO audit_log (msg) VALUES ('a'), ('b'), ('c');          -- ids 1,2,3

-- ============================================
-- SOLUTION: DELETE is transactional and counter-preserving
-- ============================================

START TRANSACTION;                               -- PostgreSQL: BEGIN;
DELETE FROM audit_log WHERE id <= 2;             -- 2 rows affected
ROLLBACK;
SELECT COUNT(*) FROM audit_log;                  -- 3  (rolled back, nothing lost)

DELETE FROM audit_log;                           -- remove all rows, keep the counter
INSERT INTO audit_log (msg) VALUES ('d');
SELECT id FROM audit_log;                        -- id = 4 on BOTH engines (counter NOT reset)

-- ============================================
-- SOLUTION: TRUNCATE inside a transaction
-- ============================================

START TRANSACTION;                               -- PostgreSQL: BEGIN;
TRUNCATE TABLE audit_log;
ROLLBACK;
SELECT COUNT(*) FROM audit_log;
-- MySQL 9.1.0 : 0  <- TRUNCATE caused an implicit COMMIT; ROLLBACK did nothing
-- PGlite (PG) : 1  <- TRUNCATE rolled back, row 'd' is back

-- ============================================
-- EXPECTED OUTPUT: counters after TRUNCATE
-- ============================================

-- MySQL:      TRUNCATE resets AUTO_INCREMENT -> next INSERT gets id = 1
-- PostgreSQL: TRUNCATE keeps the sequence      -> next INSERT got id = 5 (verified)
--             TRUNCATE TABLE audit_log RESTART IDENTITY  -> next INSERT got id = 1 (verified)
--
-- Summary table:
-- Feature            | DELETE          | TRUNCATE                   | DROP
-- WHERE clause       | yes             | no                         | no
-- Removes structure  | no              | no                         | yes
-- Rollback MySQL     | yes (InnoDB)    | NO (implicit commit)       | NO
-- Rollback PgSQL     | yes             | yes                        | yes
-- Resets counter     | no              | MySQL yes / PgSQL opt-in   | n/a
-- Row triggers fire  | yes             | no                         | no
```

---

## 🔍 Why This Works (3 lines max)
DELETE marks each row as deleted and logs it, so it can be filtered, rolled back and fire triggers - but it is slow on millions of rows. TRUNCATE deallocates the table's storage instead of touching rows, which is why it is fast and ignores WHERE. DROP deletes the table definition and everything attached to it.
हिंदी: DELETE हर row को log करके हटाता है (धीमा पर rollback-safe); TRUNCATE storage free करता है (तेज़); DROP table की definition तक हटा देता है।

---

## ⚡ Alternative Solution

```sql
-- Foreign keys block TRUNCATE (verified on both engines):
CREATE TABLE parent (id INT PRIMARY KEY);
CREATE TABLE child  (id INT PRIMARY KEY, parent_id INT, FOREIGN KEY (parent_id) REFERENCES parent(id));
INSERT INTO parent VALUES (1);  INSERT INTO child VALUES (1, 1);

TRUNCATE TABLE parent;
-- MySQL 9.1.0: ERROR 1701: Cannot truncate a table referenced in a foreign key constraint
--              (still fails after emptying child! MySQL checks the constraint, not the data)
--              workaround: DELETE FROM parent;   or  SET FOREIGN_KEY_CHECKS = 0; TRUNCATE ...; SET FOREIGN_KEY_CHECKS = 1;
-- PGlite:      ERROR: cannot truncate a table referenced in a foreign key constraint
TRUNCATE TABLE parent CASCADE;                -- PostgreSQL only: also empties child (child_rows = 0, verified)
-- PostgreSQL multi-table:  TRUNCATE TABLE parent, child;  works when both are listed together (not run)

-- DROP, with safety:
DROP TABLE IF EXISTS audit_log;               -- no error if missing (both engines)
-- After DROP: SELECT COUNT(*) FROM audit_log;
--   MySQL: ERROR 1146 Table 'd.audit_log' doesn't exist | PGlite: ERROR relation "audit_log" does not exist
-- PostgreSQL DROP TABLE parent CASCADE also drops dependent FKs/views (MySQL has no CASCADE for DROP TABLE).

-- Big deletes in production: batch them so locks and the undo log stay small
-- DELETE FROM audit_log WHERE created_at < '2023-01-01' LIMIT 10000;  -- MySQL: repeat until 0 rows (LIMIT on DELETE is MySQL-only)
-- PostgreSQL: DELETE ... WHERE id IN (SELECT id FROM audit_log WHERE ... LIMIT 10000);  -- repeat (not run)
```

---

## ⚠️ Common Mistake

```sql
-- ❌ Wrong: "TRUNCATE is just a fast DELETE, so I can roll it back" (true only in PostgreSQL)
START TRANSACTION; TRUNCATE TABLE audit_log; ROLLBACK;     -- MySQL: data is already gone

-- ❌ Wrong: DELETE FROM audit_log without WHERE in an interactive session
-- ✅ Write the WHERE first, run SELECT COUNT(*) with the same WHERE, then DELETE inside a transaction

-- ❌ Wrong: expecting DELETE to free disk space. InnoDB / PostgreSQL keep the space until
--    OPTIMIZE TABLE (MySQL) / VACUUM FULL (PostgreSQL); TRUNCATE and DROP release it immediately.
-- ❌ Wrong: using TRUNCATE on a table with audit/cascade triggers - triggers do NOT fire
```

---

## 🎯 Interview Tip (1 line)
Say: "DELETE for selective, transactional, trigger-firing removal; TRUNCATE to reset a whole table fast - remembering it auto-commits in MySQL but is transactional in PostgreSQL and blocked by FKs; DROP removes the object itself - and on prod I take a backup or run it in a PostgreSQL transaction first."

---

## 🔗 Related Questions
→ Q014 (UPDATE with JOIN) | Q013 (Upsert) | Q239 (Find duplicates, DELETE) | Q242 (SELECT FOR UPDATE)
