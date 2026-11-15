---

# Q145. Soft Delete — Design + Query Implications
# Category: Schema Design
# Difficulty: ⭐⭐ Medium
# DB: Both (MySQL 8.0+ | PostgreSQL) — run on MySQL 9.1.0 and PGlite

---

## ❓ Question
Instead of physically deleting users, mark them deleted with a `deleted_at` timestamp. What breaks (unique constraints, queries, foreign keys, indexes), and how do you fix each in MySQL and PostgreSQL?

---

## 💡 Quick Concept (2 lines only)
Soft delete = `UPDATE ... SET deleted_at = now()` instead of `DELETE`, so data can be restored or audited. The catch: every query must filter it, and UNIQUE constraints must ignore deleted rows.
हिंदी: Soft delete में row हटाने की जगह `deleted_at` भर देते हैं; पर हर query में filter लगाना पड़ता है और UNIQUE constraint को deleted rows ignore करनी पड़ती हैं।

---

## ✅ Answer / Solution

```sql
-- ============================================
-- SETUP (MySQL)
-- ============================================

CREATE TABLE users (
  user_id    INT PRIMARY KEY AUTO_INCREMENT,
  email      VARCHAR(100) NOT NULL,
  full_name  VARCHAR(80),
  deleted_at TIMESTAMP NULL DEFAULT NULL,       -- NULL = alive
  UNIQUE KEY uq_users_email (email)             -- the naive version
);

INSERT INTO users (email, full_name) VALUES
  ('asha@example.com', 'Asha'),
  ('ravi@example.com', 'Ravi');

-- ============================================
-- SOLUTION
-- ============================================

-- Step 1: "delete" Asha
UPDATE users SET deleted_at = '2024-06-01 10:00:00' WHERE email = 'asha@example.com';

-- Step 2: every read must exclude deleted rows
SELECT user_id, email, deleted_at FROM users WHERE deleted_at IS NULL;
-- user_id | email            | deleted_at
-- 2       | ravi@example.com | NULL

-- Step 3: Asha signs up again with the same email -> naive UNIQUE blocks it
INSERT INTO users (email, full_name) VALUES ('asha@example.com', 'Asha again');
-- MySQL: ERROR 1062 (23000): Duplicate entry 'asha@example.com' for key 'users.uq_users_email'

-- Step 4 (MySQL fix): unique only among ALIVE rows via a generated column.
-- MySQL has no partial indexes, but UNIQUE ignores NULLs, so expose email only when alive:
ALTER TABLE users DROP INDEX uq_users_email;
ALTER TABLE users
  ADD COLUMN active_email VARCHAR(100)
    GENERATED ALWAYS AS (CASE WHEN deleted_at IS NULL THEN email END) VIRTUAL,
  ADD UNIQUE KEY uq_users_active_email (active_email);

INSERT INTO users (email, full_name) VALUES ('asha@example.com', 'Asha again');   -- OK now
INSERT INTO users (email, full_name) VALUES ('asha@example.com', 'Asha third');
-- ERROR 1062 (23000): Duplicate entry 'asha@example.com' for key 'users.uq_users_active_email'

-- Step 5: hide the filter in a view so nobody forgets it
CREATE VIEW active_users AS
  SELECT user_id, email, full_name FROM users WHERE deleted_at IS NULL;
SELECT * FROM active_users ORDER BY user_id;

-- ============================================
-- EXPECTED OUTPUT (real MySQL 9.1.0)
-- ============================================

-- user_id | email            | full_name
-- 2       | ravi@example.com | Ravi
-- 4       | asha@example.com | Asha again      <- id 4, not 3: the failed INSERT burned id 3 (AUTO_INCREMENT gaps are normal)
--
-- SELECT COUNT(*) AS all_rows, SUM(deleted_at IS NULL) AS active_rows FROM users;
-- all_rows | active_rows
-- 3        | 2

-- ============================================
-- PostgreSQL: partial unique index (the clean way)
-- ============================================

CREATE TABLE users (
  user_id    SERIAL PRIMARY KEY,
  email      VARCHAR(100) NOT NULL,
  full_name  VARCHAR(80),
  deleted_at TIMESTAMPTZ NULL
);
CREATE UNIQUE INDEX uq_users_active_email ON users (email) WHERE deleted_at IS NULL;
-- same inserts/updates as above ->
-- re-signup after soft delete: OK ; second alive duplicate:
--   ERROR: duplicate key value violates unique constraint "uq_users_active_email"
-- active_users view returns: (2 Ravi) and (3 Asha again); all_rows = 3, active_rows = 2  (real PGlite)
```

---

## 🔍 Why This Works (3 lines max)
Uniqueness is enforced only on the "alive" subset: PgSQL does it with a partial index, MySQL by making the indexed value NULL for deleted rows (UNIQUE allows many NULLs). A view or default filter centralizes the `deleted_at IS NULL` rule.
हिंदी: Uniqueness सिर्फ "alive" rows पर लागू होती है: PgSQL में partial index से, MySQL में deleted rows के लिए NULL वाला generated column से।

---

## ⚡ Alternative Solution

```sql
-- 1) Archive table instead of flag: move rows to users_deleted in one transaction
BEGIN;
INSERT INTO users_deleted SELECT * FROM users WHERE user_id = 1;
DELETE FROM users WHERE user_id = 1;
COMMIT;                       -- main table stays small, constraints stay simple (users_deleted: not created above)

-- 2) Boolean is_deleted instead of timestamp: loses "when" and can't be used in the unique trick.

-- 3) Include deleted_at in the unique key: UNIQUE (email, deleted_at)
--    Works in MySQL only if deleted_at is NOT NULL for deleted AND alive rows share a sentinel
--    ('1970-01-01'); in PgSQL a NULL deleted_at never conflicts (NULLs are distinct) - so it silently
--    allows duplicate alive emails! (PgSQL 15+: UNIQUE NULLS NOT DISTINCT changes this.)

-- 4) PgSQL: index only alive rows to keep hot indexes small
CREATE INDEX idx_users_active_name ON users (full_name) WHERE deleted_at IS NULL;

-- 5) GDPR/"right to erasure": soft delete is NOT erasure - schedule a hard purge job
--    (DELETE ... WHERE deleted_at < now() - INTERVAL '30 days').
```

---

## ⚠️ Common Mistake

```sql
-- ❌ Wrong: forgetting the filter in one query (reports, joins, counts)
SELECT COUNT(*) FROM users;                 -- 3, counts the deleted Asha too
-- ✅ SELECT COUNT(*) FROM users WHERE deleted_at IS NULL;  -- 2   (or use the active_users view)

-- ❌ Wrong: JOIN to a soft-deleted parent: orders still point at a deleted user,
--    and FK ON DELETE CASCADE never fires (no real delete happens). Decide explicitly what
--    "deleted user" means for child rows (hide, anonymize, keep).

-- ❌ Wrong: ORM global scopes assumed everywhere - raw SQL, BI tools and other services bypass them.

-- ❌ Wrong: no index consideration - low-selectivity deleted_at at the front of an index is useless;
--    prefer partial indexes (PgSQL) or lead with the real filter column.

-- ❌ Wrong: table grows forever; plan archival/purge.
```

---

## 🎯 Interview Tip (1 line)
Say: "Soft delete costs you unique-constraint handling, a filter on every query, and cascade semantics; I use a partial unique index in Postgres (generated-column trick in MySQL), a view for reads, and a retention job for hard purge."

---

## 🔗 Related Questions
→ Q146 (Audit log table) | Q158 (Generated columns) | Q159 (CHECK constraints) | Q015 (DELETE vs TRUNCATE vs DROP)
