---

# Q032. ALTER TABLE — Add Column With Default Value (Online vs Offline)
# Category: Data Types & DDL
# Difficulty: ⭐⭐⭐ Hard
# DB: Both (MySQL 8.0+ | PostgreSQL 11+)

---

## ❓ Question
You must add `status VARCHAR(20) NOT NULL DEFAULT 'active'` to a 200M-row `users` table in production. When is this a metadata-only change (instant), when does it rewrite the table, and how do you do it safely on MySQL and PostgreSQL?

---

## 💡 Quick Concept (2 lines only)
MySQL 8.0.12+ `ALGORITHM=INSTANT` and PostgreSQL 11+ both store a constant default in the catalog, so ADD COLUMN is O(1). A volatile default (`random()`, `now()` in PG) or a type change forces a full table rewrite.
हिंदी: Constant default = सिर्फ metadata change (instant); volatile default या type change = पूरी table rewrite।

---

## ✅ Answer / Solution

```sql
-- ============================================
-- SETUP (run this first)
-- ============================================

CREATE TABLE users (
  id         INT PRIMARY KEY,
  email      VARCHAR(100) NOT NULL,
  created_at DATE
);

INSERT INTO users VALUES
  (1,'a@x.com','2024-01-01'),
  (2,'b@x.com','2024-02-01'),
  (3,'c@x.com','2024-03-01');

-- ============================================
-- SOLUTION — MySQL 8.0+ (verified on 9.1.0)
-- ============================================

-- Step 1: ask for INSTANT explicitly -> if impossible, MySQL ERRORS instead of silently copying the table
ALTER TABLE users
  ADD COLUMN status VARCHAR(20) NOT NULL DEFAULT 'active',
  ALGORITHM=INSTANT;

-- Step 2: INPLACE + LOCK=NONE also works (no copy-lock), may be slower on huge tables
ALTER TABLE users
  ADD COLUMN score INT NOT NULL DEFAULT 0,
  ALGORITHM=INPLACE, LOCK=NONE;

-- Things that CANNOT be instant (MySQL refuses because we asked for it explicitly):
ALTER TABLE users ADD COLUMN tmp_calc INT DEFAULT (id*2), ALGORITHM=INSTANT;      -- expression default
-- ERROR 1845 (0A000): ALGORITHM=INSTANT is not supported for this operation. Try ALGORITHM=COPY/INPLACE.
ALTER TABLE users MODIFY email VARCHAR(50) NOT NULL, ALGORITHM=INSTANT;           -- type/length change
-- ERROR 1846 (0A000): ALGORITHM=INSTANT is not supported. Reason: Need to rebuild the table to change column type.
ALTER TABLE users ADD COLUMN bad INT, ALGORITHM=COPY, LOCK=NONE;                  -- COPY always locks writes
-- ERROR 1846 (0A000): LOCK=NONE is not supported. Reason: COPY algorithm requires a lock. Try LOCK=SHARED.

SELECT * FROM users ORDER BY id;

-- ============================================
-- EXPECTED OUTPUT (MySQL 9.1.0)
-- ============================================

-- id | email   | created_at | status | score
-- 1  | a@x.com | 2024-01-01 | active | 0
-- 2  | b@x.com | 2024-02-01 | active | 0
-- 3  | c@x.com | 2024-03-01 | active | 0
```

---

## 🔍 Why This Works (3 lines max)
For a constant default the engine records the default in the table metadata and fills it lazily when old rows are read, so no row is touched. Naming `ALGORITHM=` makes the DDL fail fast instead of silently falling back to a blocking copy.
हिंदी: Constant default metadata में store होता है, rows touch नहीं होते; `ALGORITHM=` लिखने से गलत fallback की जगह error मिलता है।

---

## ⚡ Alternative Solution

```sql
-- PostgreSQL 11+ (verified on PGlite = PostgreSQL 18.6, using relfilenode to detect a rewrite)
SELECT relfilenode FROM pg_class WHERE relname = 'users';          -- 16384
ALTER TABLE users ADD COLUMN status VARCHAR(20) NOT NULL DEFAULT 'active';
SELECT relfilenode FROM pg_class WHERE relname = 'users';          -- 16384  (unchanged = NO rewrite, instant)

ALTER TABLE users ADD COLUMN token DOUBLE PRECISION NOT NULL DEFAULT random();   -- volatile default
SELECT relfilenode FROM pg_class WHERE relname = 'users';          -- 16395  (changed = full table rewrite, ACCESS EXCLUSIVE lock held)
-- (exact relfilenode numbers differ per run; only changed/unchanged matters)

-- Safe pattern for a NOT NULL column with a non-constant value, on both engines:
--  1) add nullable column (instant)           ALTER TABLE users ADD COLUMN flag BOOLEAN;
--  2) backfill in small batches               UPDATE users SET flag = false WHERE id BETWEEN ? AND ?;
--  3) PgSQL: add constraint without full scan lock, then validate separately
ALTER TABLE users ADD CONSTRAINT chk_flag CHECK (flag IS NOT NULL) NOT VALID;   -- new writes checked, old rows not
ALTER TABLE users VALIDATE CONSTRAINT chk_flag;    -- ERROR while some row is still NULL; passes once backfilled
--  PgSQL 12+: validated CHECK (col IS NOT NULL) lets SET NOT NULL skip its full scan.
--  MySQL: for table rewrites use gh-ost / pt-online-schema-change (NOT run here), or INPLACE where allowed.
```

---

## ⚠️ Common Mistake
```sql
-- ❌ Wrong: running ALTER without ALGORITHM/LOCK clauses on a big MySQL table
ALTER TABLE users ADD COLUMN status VARCHAR(20) NOT NULL DEFAULT 'active';
-- On a case that is not instant-capable this silently becomes a COPY -> writes blocked for hours
-- ✅ Correct: always state the intent; the DDL fails fast if the guarantee can't be met
ALTER TABLE users ADD COLUMN status VARCHAR(20) NOT NULL DEFAULT 'active', ALGORITHM=INSTANT;

-- ❌ Wrong (PgSQL): no lock_timeout -> ALTER waits behind a long transaction and queues ALL other queries behind itself
-- ✅ Correct (PgSQL): SET lock_timeout = '3s'; retry the ALTER in a loop
-- ❌ Wrong: ADD COLUMN ... DEFAULT now() on PG / MySQL <8.0.12 and assuming it's instant
```

---

## 🎯 Interview Tip (1 line)
Say: "I check whether the change is metadata-only — constant default on MySQL 8.0.12+ or PG 11+ is instant — I pin `ALGORITHM=INSTANT` so it fails instead of copying, set `lock_timeout` on PG so I don't block the queue behind a long transaction, and for rewrites I use gh-ost/pt-osc or add-nullable, batch backfill, then validate the constraint."

---

## 🔗 Related Questions
→ Q033 (Add index zero downtime) | Q034 (Generated columns) | Q037 (CHECK constraints) | Q245 (Migrate 100M rows zero downtime)
