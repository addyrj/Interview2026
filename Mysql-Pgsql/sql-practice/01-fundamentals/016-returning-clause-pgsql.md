---

# Q016. RETURNING Clause (PgSQL) — What Does It Return?
# Category: Fundamentals
# Difficulty: ⭐⭐ Medium
# DB: PostgreSQL (MySQL has no RETURNING — workarounds shown)

---

## ❓ Question
What does `RETURNING` do in PostgreSQL? Show it with INSERT, UPDATE, DELETE and upsert. How do you get the same result in MySQL, which does not support it?

---

## 💡 Quick Concept (2 lines only)
`RETURNING` makes INSERT/UPDATE/DELETE hand back the affected rows (any columns or expressions, post-change values for INSERT/UPDATE, old values for DELETE) in the same round trip — no second SELECT.
हिंदी: RETURNING से INSERT/UPDATE/DELETE खुद affected rows वापस देता है, अलग SELECT की जरूरत नहीं।

---

## ✅ Answer / Solution

```sql
-- ============================================
-- SETUP (PostgreSQL) — run this first
-- ============================================

CREATE TABLE users (
  id     SERIAL PRIMARY KEY,
  email  VARCHAR(100) UNIQUE NOT NULL,
  name   VARCHAR(50),
  status VARCHAR(20) DEFAULT 'active'
);

CREATE TABLE users_archive (LIKE users);   -- same columns, used for the CTE example

-- ============================================
-- SOLUTION
-- ============================================

-- 1) INSERT ... RETURNING: get DB-generated id + defaults without a 2nd query
INSERT INTO users (email, name) VALUES ('a@x.com', 'Asha')
RETURNING id, email, status;
-- id | email   | status
-- 1  | a@x.com | active          <- 'active' came from the DEFAULT

-- 2) Multi-row insert returns one row per inserted row
INSERT INTO users (email, name) VALUES ('b@x.com', 'Bala'), ('c@x.com', 'Chitra')
RETURNING id, name;
-- id | name
-- 2  | Bala
-- 3  | Chitra

-- 3) UPDATE ... RETURNING returns the NEW values (aliases allowed)
UPDATE users SET status = 'suspended' WHERE id <= 2
RETURNING id, status AS new_status;
-- id | new_status
-- 1  | suspended
-- 2  | suspended

-- 4) DELETE ... RETURNING returns the deleted rows (RETURNING * = full row)
DELETE FROM users WHERE id = 3 RETURNING *;
-- id | email      | name   | status
-- 3  | c@x.com    | Chitra | active

-- 5) Upsert + RETURNING; (xmax = 0) is a common trick: true = inserted, false = updated
INSERT INTO users (email, name) VALUES ('a@x.com', 'Asha2')
ON CONFLICT (email) DO UPDATE SET name = EXCLUDED.name
RETURNING id, name, (xmax = 0) AS inserted;
-- id | name  | inserted
-- 1  | Asha2 | false

-- 6) Data-modifying CTE: move rows (delete + archive) atomically in ONE statement
WITH del AS (
  DELETE FROM users WHERE status = 'suspended' RETURNING *
)
INSERT INTO users_archive SELECT * FROM del RETURNING id, email;
-- id | email
-- 2  | b@x.com          <- row order is NOT guaranteed
-- 1  | a@x.com

-- 7) UPDATE matching 0 rows returns 0 rows (not an error)
UPDATE users SET name = 'X' WHERE id = 999 RETURNING id;
-- (0 rows)

-- ============================================
-- EXPECTED OUTPUT  (verified on PostgreSQL 18 via PGlite; each block's result shown above)
-- ============================================
-- SELECT count(*) FROM users;  ->  0   (everything moved to users_archive)
```

---

## 🔍 Why This Works (3 lines max)
PostgreSQL evaluates the RETURNING list against the rows the statement actually touched, so it sees generated ids, defaults and trigger-modified values. Because it is part of the same statement, it is atomic and saves a round trip and a race-prone follow-up SELECT.
हिंदी: RETURNING उसी statement की affected rows पर चलता है, इसलिए atomic है और extra query नहीं लगती।

---

## ⚡ Alternative Solution

```sql
-- MySQL (no RETURNING in MySQL 8.x / 9.x; MariaDB 10.5+ does have INSERT/DELETE ... RETURNING)

-- Get the generated id of the last single-row insert (per-connection, safe under concurrency):
INSERT INTO users (email, name) VALUES ('a@x.com', 'Asha');
SELECT LAST_INSERT_ID();            -- for multi-row inserts it returns the FIRST id generated

-- "Updated rows" = run SELECT in the same transaction; add FOR UPDATE to avoid races:
START TRANSACTION;
SELECT id, email FROM users WHERE status = 'active' FOR UPDATE;
UPDATE users SET status = 'suspended' WHERE status = 'active';
COMMIT;

-- Delete + archive in MySQL needs two statements inside one transaction:
START TRANSACTION;
INSERT INTO users_archive SELECT * FROM users WHERE status = 'suspended';
DELETE FROM users WHERE status = 'suspended';
COMMIT;
-- (MySQL alternative snippets above were not executed against a real table here;
--  the RETURNING examples were run on PGlite = PostgreSQL 18.)
```

---

## ⚠️ Common Mistake

```sql
-- ❌ Wrong: INSERT then SELECT MAX(id) to find the new id
INSERT INTO users (email) VALUES ('d@x.com');
SELECT MAX(id) FROM users;        -- race: another session may have inserted in between

-- ❌ Wrong: assuming RETURNING shows OLD values for UPDATE
UPDATE users SET status = 'x' WHERE id = 1 RETURNING status;   -- returns 'x', the NEW value
-- (PostgreSQL 18 added OLD./NEW. aliases in RETURNING if you need the previous value)

-- ✅ Correct: INSERT ... RETURNING id (PgSQL) / LAST_INSERT_ID() (MySQL)
```

---

## 🎯 Interview Tip (1 line)
Say: "I use RETURNING to avoid a read-after-write round trip and race, and combine it with a data-modifying CTE for atomic move/archive; in MySQL I use LAST_INSERT_ID() or a transactional SELECT ... FOR UPDATE."

---

## 🔗 Related Questions
→ Q017 (SELECT FOR UPDATE) | Q018 (CTE / WITH) | Q029 (SERIAL vs IDENTITY vs AUTO_INCREMENT)
