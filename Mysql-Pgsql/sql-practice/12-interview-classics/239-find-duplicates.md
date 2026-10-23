---

# Q239. Find Duplicate Rows — Multiple Approaches
# Category: Interview Classics
# Difficulty: ⭐⭐ Medium
# DB: Both (MySQL + PostgreSQL)

---

## ❓ Question
Find all duplicate emails in a users table. Then: find and DELETE duplicates keeping only the row with the lowest id. Show 3 approaches.

---

## 💡 Quick Concept (2 lines only)
Duplicates = GROUP BY + HAVING COUNT(*) > 1. Delete keeping one = delete WHERE id NOT IN (SELECT MIN(id) GROUP BY duplicate_key). MySQL needs the double-subquery wrapper because MySQL can't reference the same table in DELETE subquery directly.
हिंदी: Duplicates = GROUP BY + HAVING COUNT > 1। Delete = keep MIN(id), बाकी delete करो। MySQL = double subquery wrapper।

---

## ✅ Answer / Solution

```sql
-- ============================================
-- SETUP
-- ============================================

CREATE TABLE users (
  id    INT PRIMARY KEY AUTO_INCREMENT,
  name  VARCHAR(100),
  email VARCHAR(255)
);

INSERT INTO users (name, email) VALUES
  ('Alice',  'alice@example.com'),
  ('Alice2', 'alice@example.com'),  -- duplicate email!
  ('Alice3', 'alice@example.com'),  -- third duplicate!
  ('Bob',    'bob@example.com'),
  ('Carol',  'carol@example.com'),
  ('Carol2', 'carol@example.com');  -- duplicate!

-- ============================================
-- STEP 1: FIND DUPLICATES
-- ============================================

-- Which emails are duplicated?
SELECT email, COUNT(*) AS occurrences
FROM users
GROUP BY email
HAVING COUNT(*) > 1
ORDER BY occurrences DESC;

-- Output:
-- email             | occurrences
-- alice@example.com | 3
-- carol@example.com | 2

-- Get ALL rows that have a duplicate email:
SELECT *
FROM users
WHERE email IN (
  SELECT email FROM users GROUP BY email HAVING COUNT(*) > 1
)
ORDER BY email, id;

-- Output:
-- id | name   | email
--  1 | Alice  | alice@example.com
--  2 | Alice2 | alice@example.com
--  3 | Alice3 | alice@example.com
--  5 | Carol  | carol@example.com
--  6 | Carol2 | carol@example.com

-- ============================================
-- STEP 2: FIND DUPLICATES — WHICH ID TO KEEP
-- ============================================

-- Show min(id) to keep per duplicate group:
SELECT email, MIN(id) AS keep_id, COUNT(*) AS count
FROM users
GROUP BY email
HAVING COUNT(*) > 1;

-- Output:
-- email             | keep_id | count
-- alice@example.com | 1       | 3      ← keep id=1, delete 2 and 3
-- carol@example.com | 5       | 2      ← keep id=5, delete 6

-- ============================================
-- APPROACH 1: DELETE WITH SUBQUERY (MySQL-safe)
-- ============================================

-- MySQL can't: DELETE FROM t WHERE id NOT IN (SELECT ... FROM t)
-- Must wrap in another subquery to avoid "can't specify target table" error:

DELETE FROM users
WHERE id NOT IN (
  SELECT id FROM (                       -- ← double subquery (MySQL workaround!)
    SELECT MIN(id) AS id
    FROM users
    GROUP BY email
  ) keep_ids
);

-- What this does:
-- Inner query: SELECT MIN(id) FROM users GROUP BY email → {1, 4, 5} (one id per email to keep)
-- Middle wrapper: makes it a derived table (MySQL needs this)
-- Outer DELETE: delete any user whose id is NOT in the keep list
-- After: only ids 1, 4, 5 remain

-- PostgreSQL version (simpler — no double-subquery needed):
DELETE FROM users
WHERE id NOT IN (
  SELECT MIN(id) FROM users GROUP BY email
);

-- ============================================
-- APPROACH 2: DELETE WITH SELF-JOIN (works everywhere)
-- ============================================

-- Keep the row with MIN(id) per email, delete rows with higher id:
DELETE u1
FROM users u1
JOIN users u2
  ON u1.email = u2.email      -- same email
  AND u1.id > u2.id;          -- u1 has higher id than u2 (so u1 is a duplicate)
-- MySQL DELETE with JOIN syntax
-- Deletes Alice2 (id=2 > id=1) and Alice3 (id=3 > id=1) etc.

-- PostgreSQL equivalent with USING:
DELETE FROM users u1
USING users u2
WHERE u1.email = u2.email
  AND u1.id > u2.id;

-- ============================================
-- APPROACH 3: ROW_NUMBER + CTE (most readable)
-- ============================================

-- PgSQL:
WITH duplicates AS (
  SELECT id,
    ROW_NUMBER() OVER (PARTITION BY email ORDER BY id ASC) AS rn
  FROM users
)
DELETE FROM users
WHERE id IN (
  SELECT id FROM duplicates WHERE rn > 1  -- rn=1 is the keeper (lowest id), delete rn>1
);

-- Output: Deletes ids 2, 3, 6 — keeps 1, 4, 5

-- MySQL (8.0+ with window functions):
WITH to_delete AS (
  SELECT id FROM (
    SELECT id,
      ROW_NUMBER() OVER (PARTITION BY email ORDER BY id) AS rn
    FROM users
  ) ranked
  WHERE rn > 1
)
DELETE FROM users WHERE id IN (SELECT id FROM to_delete);
-- MySQL: can't DELETE from a table referenced in CTE directly
-- The extra nesting makes it a derived table → MySQL allows it

-- ============================================
-- FIND DUPLICATE ROWS (ALL COLUMNS MUST MATCH)
-- ============================================

-- Exact duplicate rows where ALL columns (except id) are the same:
SELECT name, email, COUNT(*) AS cnt
FROM users
GROUP BY name, email
HAVING COUNT(*) > 1;

-- Or using window function to find exact duplicates:
SELECT *
FROM (
  SELECT *,
    COUNT(*) OVER (PARTITION BY name, email) AS dup_count
  FROM users
) x
WHERE dup_count > 1;

-- ============================================
-- PREVENT FUTURE DUPLICATES WITH UNIQUE CONSTRAINT
-- ============================================

-- After cleanup, add a unique constraint to prevent re-occurrence:
ALTER TABLE users ADD UNIQUE INDEX idx_unique_email (email);

-- PgSQL:
ALTER TABLE users ADD CONSTRAINT users_email_unique UNIQUE (email);

-- Now: INSERT of duplicate email → ERROR: Duplicate entry / unique constraint violation
-- Or use UPSERT to handle gracefully:
-- MySQL:
INSERT INTO users (name, email) VALUES ('Bob2', 'bob@example.com')
ON DUPLICATE KEY UPDATE name = VALUES(name);

-- PgSQL:
INSERT INTO users (name, email) VALUES ('Bob2', 'bob@example.com')
ON CONFLICT (email) DO UPDATE SET name = EXCLUDED.name;

-- ============================================
-- FIND DUPLICATES ACROSS MULTIPLE COLUMNS
-- ============================================

-- Employees with same name AND department (but different id):
SELECT name, dept, COUNT(*) AS cnt
FROM employees
GROUP BY name, dept
HAVING COUNT(*) > 1;

-- Get all rows including duplicates:
SELECT e1.*
FROM employees e1
JOIN (
  SELECT name, dept FROM employees GROUP BY name, dept HAVING COUNT(*) > 1
) dups ON e1.name = dups.name AND e1.dept = dups.dept
ORDER BY e1.name, e1.dept, e1.id;
```

---

## 🔍 Why This Works (3 lines max)
`GROUP BY + HAVING COUNT(*) > 1` identifies which values have duplicates by collapsing rows and counting. `MIN(id) GROUP BY email` finds the one row to keep per group. The self-join approach `u1.id > u2.id` works by deleting any row where another row with the same email has a lower id — the MIN-id row will never be deleted.
हिंदी: GROUP BY + HAVING = duplicates find करो। MIN(id) = keeper। Self-join u1.id > u2.id = higher id wale rows delete करो।

---

## ⚡ Alternative Solution

```sql
-- Move duplicates to archive before deleting (safer):
CREATE TABLE users_duplicate_archive LIKE users;

-- Archive first:
INSERT INTO users_duplicate_archive
SELECT u1.* FROM users u1
JOIN users u2 ON u1.email = u2.email AND u1.id > u2.id;

-- Verify archive looks right
SELECT * FROM users_duplicate_archive;

-- THEN delete:
DELETE u1 FROM users u1
JOIN users u2 ON u1.email = u2.email AND u1.id > u2.id;

-- Rollback option: INSERT INTO users SELECT * FROM users_duplicate_archive;
-- if DELETE went wrong, restore from archive
```

---

## ⚠️ Common Mistake

```sql
-- ❌ Wrong: MySQL "can't specify target table" error
DELETE FROM users WHERE id NOT IN (
  SELECT MIN(id) FROM users GROUP BY email
);
-- MySQL ERROR: You can't specify target table 'users' for update in FROM clause
-- ✅ Fix: wrap in a derived table:
DELETE FROM users WHERE id NOT IN (
  SELECT id FROM (SELECT MIN(id) AS id FROM users GROUP BY email) t
);

-- ❌ Wrong: Deleting from large table without index on duplicate column
-- DELETE based on email scan = full table scan for every row!
-- ✅ Ensure index on the column used to identify duplicates:
CREATE INDEX idx_email ON users(email);

-- ❌ Wrong: Not verifying before DELETE
-- Always run the SELECT version first:
-- SELECT * FROM users WHERE id NOT IN (SELECT MIN(id) ... GROUP BY email)
-- ← See what WOULD be deleted before running DELETE
-- Then run inside a transaction with a check:
BEGIN;
  DELETE FROM users WHERE id NOT IN (SELECT id FROM (...) t);
  SELECT COUNT(*) FROM users;  -- verify expected row count
ROLLBACK;  -- only COMMIT when you're sure!
```

---

## 🎯 Interview Tip (1 line)
Say: "I find duplicates with `GROUP BY email HAVING COUNT(*) > 1`, then delete keeping `MIN(id)` per group. In MySQL I need the double-subquery wrapper to avoid the 'can't specify target table' error. I always archive duplicates before deleting in production, and then add a UNIQUE constraint to prevent future occurrences."

---

## 🔗 Related Questions
→ Q066 (ROW_NUMBER) | Q075 (top N per group) | Q055 (Nth highest salary) | Q240 (consecutive date ranges)
