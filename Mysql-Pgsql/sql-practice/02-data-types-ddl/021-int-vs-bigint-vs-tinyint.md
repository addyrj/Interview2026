---

# Q021. INT vs BIGINT vs TINYINT — When to Use
# Category: Data Types & DDL
# Difficulty: ⭐ Easy
# DB: Both (TINYINT is MySQL only — PgSQL uses SMALLINT)

---

## ❓ Question
What are the ranges and storage sizes of TINYINT, SMALLINT, INT and BIGINT? How do you pick one for ids, flags and counters? What happens on overflow, and what is the PostgreSQL equivalent of TINYINT?

---

## 💡 Quick Concept (2 lines only)
Integer types trade range for space: TINYINT 1 byte, SMALLINT 2, INT 4, BIGINT 8. Pick the smallest type that safely fits the data for its whole lifetime — but use BIGINT for ids of tables that can grow large (INT overflows at about 2.14 billion, UNSIGNED at about 4.29 billion).
हिंदी: छोटा type = कम space, लेकिन growth सोचकर चुनो; बड़ी tables के id के लिए BIGINT सुरक्षित है।

---

## ✅ Answer / Solution

```sql
-- ============================================
-- SETUP (MySQL) — run this first
-- ============================================
--  type      bytes   signed range                          unsigned (MySQL only)
--  TINYINT     1     -128 .. 127                            0 .. 255
--  SMALLINT    2     -32,768 .. 32,767                      0 .. 65,535
--  INT         4     -2,147,483,648 .. 2,147,483,647        0 .. 4,294,967,295
--  BIGINT      8     -9.22e18 .. 9.22e18                    0 .. 1.84e19
-- PgSQL: SMALLINT / INTEGER / BIGINT only (no TINYINT, no UNSIGNED).

CREATE TABLE page_views (
  id          BIGINT UNSIGNED NOT NULL PRIMARY KEY,   -- high-volume event table => BIGINT
  user_id     INT NOT NULL,                           -- bounded by user count
  rating      TINYINT UNSIGNED,                       -- 0..255 is plenty for a 1-5 score
  is_bot      TINYINT(1) NOT NULL DEFAULT 0,          -- MySQL "boolean" (BOOLEAN is an alias)
  http_status SMALLINT                                -- 100..599
);

-- ============================================
-- SOLUTION
-- ============================================

INSERT INTO page_views VALUES (1, 100, 5, 0, 200);
INSERT INTO page_views VALUES (2, 2147483647, 255, 1, 404);   -- exactly at the maximums
SELECT * FROM page_views;

-- Overflow in strict mode (default sql_mode) is an ERROR, not silent truncation:
INSERT INTO page_views VALUES (4, 1, 256, 0, 200);
-- ERROR 1264 (22003): Out of range value for column 'rating' at row 1
INSERT INTO page_views VALUES (5, 1, 5, 0, 40000);
-- ERROR 1264 (22003): Out of range value for column 'http_status' at row 1
INSERT INTO page_views VALUES (3, 2147483648, 5, 0, 200);
-- ERROR 1264 (22003): Out of range value for column 'user_id' at row 1

-- Literal arithmetic is promoted automatically in MySQL:
SELECT 2147483647 + 1 AS lit;        -- 2147483648

-- ============================================
-- EXPECTED OUTPUT
-- ============================================
-- SELECT * FROM page_views;
-- id | user_id    | rating | is_bot | http_status
-- 1  | 100        | 5      | 0      | 200
-- 2  | 2147483647 | 255    | 1      | 404
--
-- (all three errors above were produced by MySQL 9.1.0 exactly as written)
-- With sql_mode='' the same inserts are clamped silently with only a warning:
--   user_id -> 2147483647, rating -> 255, http_status -> 32767   (verified)

-- ============================================
-- PostgreSQL version
-- ============================================
CREATE TABLE page_views (
  id          BIGINT PRIMARY KEY,
  user_id     INT NOT NULL,
  rating      SMALLINT CHECK (rating BETWEEN 0 AND 255),   -- emulate TINYINT UNSIGNED
  is_bot      BOOLEAN NOT NULL DEFAULT false,              -- real boolean type
  http_status SMALLINT
);
INSERT INTO page_views VALUES (1,100,5,false,200),(2,2147483647,255,true,404);
INSERT INTO page_views VALUES (3,2147483648,5,false,200);  -- ERROR: integer out of range
INSERT INTO page_views VALUES (4,1,5,false,40000);         -- ERROR: smallint out of range
SELECT 2147483647 + 1;                                     -- ERROR: integer out of range (int + int stays int!)
SELECT 2147483647::bigint + 1;                             -- 2147483648
SELECT pg_column_size(1::smallint) s, pg_column_size(1::int) i, pg_column_size(1::bigint) b;
-- s | i | b
-- 2 | 4 | 8            (verified on PostgreSQL 18 via PGlite)
```

---

## 🔍 Why This Works (3 lines max)
Each type has a fixed width, so the engine can reject values outside the range (strict mode) and index/page sizes shrink with smaller types — every secondary index in InnoDB also carries the primary key, so a BIGINT PK makes all indexes wider. Overflow of an AUTO_INCREMENT id is a hard outage, which is why high-growth tables start with BIGINT.
हिंदी: Fixed width से range तय होती है; PK बड़ा हो तो हर secondary index भी बड़ा होता है।

---

## ⚡ Alternative Solution

```sql
-- What happens when an AUTO_INCREMENT INT is exhausted (MySQL 9.1.0, verified):
CREATE TABLE t (id INT AUTO_INCREMENT PRIMARY KEY);
ALTER TABLE t AUTO_INCREMENT = 2147483647;
INSERT INTO t VALUES ();          -- gets 2147483647
INSERT INTO t VALUES ();          -- ERROR 1062: Duplicate entry '2147483647' for key 't.PRIMARY'

-- Changing the type later = full table rebuild on a big table (use online tools: gh-ost / pt-osc)
ALTER TABLE page_views MODIFY user_id BIGINT NOT NULL;

-- Rule of thumb for sizing:
--   flags / small enums / ratings ........ TINYINT (MySQL) or SMALLINT (PgSQL)
--   status codes, small counters ......... SMALLINT
--   most FKs, bounded business ids ....... INT (UNSIGNED in MySQL doubles headroom)
--   events, logs, orders, messages ....... BIGINT
-- MySQL display width, e.g. INT(11), is cosmetic only (deprecated) — it does NOT limit digits.
-- PgSQL: prefer GENERATED ... AS IDENTITY on BIGINT (see Q029).
```

---

## ⚠️ Common Mistake

```sql
-- ❌ Wrong: believing INT(3) stores only 3 digits
CREATE TABLE x (qty INT(3));      -- still a full 4-byte INT, 1000 is accepted; width is deprecated

-- ❌ Wrong: signed INT primary key on a table taking ~10k inserts/sec
--          (2.1 billion / 10,000 per sec = ~2.5 days); ids also burn on rolled-back / failed inserts.
-- ❌ Wrong: signed INT for a value that is never negative, wasting half the range
-- ✅ Correct: BIGINT (UNSIGNED) for growth tables; UNSIGNED where negatives are impossible (MySQL).

-- ❌ Wrong (PgSQL): CREATE TABLE t (flag TINYINT);   -- ERROR: type "tinyint" does not exist
-- ✅ Correct: SMALLINT or BOOLEAN
```

---

## 🎯 Interview Tip (1 line)
Say: "I size by growth, not today's rows: BIGINT for any event/order id, INT for bounded lookups, TINYINT/SMALLINT for flags — because migrating an exhausted INT primary key on a billion-row table is a painful online schema change."

---

## 🔗 Related Questions
→ Q022 (VARCHAR vs TEXT vs CHAR) | Q023 (DECIMAL vs FLOAT) | Q028 (UUID vs BIGINT PK) | Q029 (SERIAL vs IDENTITY vs AUTO_INCREMENT)
