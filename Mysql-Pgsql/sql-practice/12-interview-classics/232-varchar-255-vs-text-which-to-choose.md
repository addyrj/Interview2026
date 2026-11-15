---

# Q232. VARCHAR(255) vs TEXT — Which to Choose?
# Category: Interview Classics
# Difficulty: ⭐⭐ Medium
# DB: Both (MySQL + PostgreSQL)

---

## ❓ Question
When should you use VARCHAR(255) and when TEXT? Is 255 a magic number? Compare the behaviour in MySQL (InnoDB) and PostgreSQL: indexing, defaults, row-size limits, overflow handling, and performance.

---

## 💡 Quick Concept (2 lines only)
MySQL: VARCHAR(n) is stored inline and can be fully indexed (up to 3072 bytes); TEXT is stored off-page for large values, needs a prefix length to be indexed, and cannot have a plain DEFAULT. PostgreSQL: VARCHAR(n) and TEXT are the same storage and speed — VARCHAR(n) just adds a length check, so TEXT (+ CHECK if needed) is idiomatic.
हिंदी: MySQL में VARCHAR indexable और inline, TEXT में prefix index चाहिए; PostgreSQL में दोनों बराबर हैं, VARCHAR(n) सिर्फ length check जोड़ता है।

---

## ✅ Answer / Solution

```sql
-- ============================================
-- SETUP — MySQL 9.1 (every result below was run)
-- ============================================

CREATE TABLE articles (
  id    INT PRIMARY KEY,
  title VARCHAR(10) NOT NULL,   -- small bounded value
  body  TEXT                    -- unbounded content
);

-- ============================================
-- SOLUTION — behaviour tests
-- ============================================

-- 1) Length enforcement
INSERT INTO articles VALUES (1, 'Short', 'x');                       -- OK
INSERT INTO articles VALUES (2, 'This title is far too long', 'x');
-- MySQL strict mode (default): ERROR 1406 (22001): Data too long for column 'title' at row 1

SET SESSION sql_mode = '';       -- non-strict (legacy) mode
INSERT INTO articles VALUES (3, 'This title is far too long', 'x');
SELECT id, title FROM articles;
-- Result: id=1 'Short' ; id=3 'This title'   <- SILENTLY TRUNCATED (only a warning)

-- 2) Indexing
CREATE INDEX idx_body ON articles (body);
-- ERROR 1170 (42000): BLOB/TEXT column 'body' used in key specification without a key length
CREATE INDEX idx_body ON articles (body(20));    -- prefix index works

-- 3) Default value
CREATE TABLE d (id INT, b TEXT DEFAULT 'x');
-- ERROR 1101 (42000): BLOB, TEXT, GEOMETRY or JSON column 'b' can't have a default value
CREATE TABLE d2 (id INT, b TEXT DEFAULT ('x'));  -- expression default works in 8.0.13+
-- Result: INSERT (id) VALUES (1) -> b = 'x'

-- 4) Row size limit: all VARCHARs share ~65,535 bytes per row
CREATE TABLE wide (id INT, a VARCHAR(16000), b VARCHAR(16000));   -- utf8mb4 = 4 bytes/char
-- ERROR 1118 (42000): Row size too large. The maximum row size ... is 65535 ...
-- TEXT columns count only ~9-12 bytes each toward that limit.

-- 5) Index key length limit (InnoDB 3072 bytes, utf8mb4 = 4 bytes per char)
CREATE TABLE ix (id INT, a VARCHAR(1000), KEY(a));
-- ERROR 1071 (42000): Specified key was too long; max key length is 3072 bytes

-- 6) Characters vs bytes
SELECT CHAR_LENGTH('héllo') AS chars, LENGTH('héllo') AS bytes;
-- Result: chars=5, bytes=6   (n in VARCHAR(n) counts CHARACTERS)

-- ============================================
-- POSTGRESQL (verified on PGlite)
-- ============================================

CREATE TABLE articles (
  id    INT PRIMARY KEY,
  title VARCHAR(10) NOT NULL,
  slug  TEXT NOT NULL,
  body  TEXT
);
INSERT INTO articles VALUES (2, 'This title is far too long', 'x', 'x');
-- ERROR: value too long for type character varying(10)   (always an error, never truncates)

CREATE INDEX idx_body ON articles (body);        -- OK: TEXT indexes without prefix (limit ~2.7KB per entry for btree)

ALTER TABLE articles ADD CONSTRAINT slug_len CHECK (char_length(slug) <= 50);
INSERT INTO articles VALUES (4, 'ok', repeat('a', 51), 'x');
-- ERROR: new row for relation "articles" violates check constraint "slug_len"

SELECT pg_column_size('abc'::varchar(10)) AS v, pg_column_size('abc'::text) AS t;
-- Result: v=7, t=7        <- identical storage

CREATE TABLE big (b TEXT);
INSERT INTO big VALUES (repeat('x', 1000000));
SELECT length(b), pg_column_size(b) FROM big;
-- Result: 1000000 | 11452     <- 1 MB value auto-compressed (TOAST) to ~11 KB

CREATE TABLE d (b TEXT DEFAULT 'x');             -- plain default on TEXT is fine in PG
```

---

## 🔍 Why This Works (3 lines max)
In MySQL the choice changes physical layout and limits (inline vs off-page, index prefix, row size, default), so VARCHAR for bounded/indexed fields and TEXT for bodies. In PostgreSQL both types use the same varlena storage with TOAST, so the length limit is only a constraint — and 255 is a legacy 1-byte-length-prefix boundary from old MySQL, not a real optimum.
हिंदी: MySQL में layout बदलता है, इसलिए सोच-समझकर चुनो; PostgreSQL में दोनों same हैं और 255 सिर्फ पुरानी आदत है।

---

## ⚡ Alternative Solution

```sql
-- Use the limit that matches the business rule, not 255:
--   email   VARCHAR(254)   (RFC max)
--   country CHAR(2)        (ISO code)
--   url     VARCHAR(2048)  (practical browser limit)

-- PostgreSQL: bounded text via DOMAIN so the rule lives in one place
CREATE DOMAIN short_title AS TEXT CHECK (char_length(VALUE) <= 100);
CREATE TABLE posts (id INT PRIMARY KEY, title short_title);

-- MySQL: large body in a separate table keeps hot rows small
CREATE TABLE article_bodies (article_id INT PRIMARY KEY, body MEDIUMTEXT);
-- TEXT = 64 KB, MEDIUMTEXT = 16 MB, LONGTEXT = 4 GB (MySQL); PostgreSQL TEXT = up to ~1 GB
```

---

## ⚠️ Common Mistake

```sql
-- ❌ Wrong: VARCHAR(255) everywhere "by habit", then email addresses / names get truncated
--   in non-strict mode, or index creation fails once utf8mb4 (4 bytes/char) pushes keys past 3072 bytes.

-- ❌ Wrong: assuming VARCHAR(n) is faster than TEXT in PostgreSQL (it is not; same storage)
-- ❌ Wrong: SELECT * on tables with huge TEXT columns -> drags large values over the network
-- ✅ Correct: size VARCHAR by the real rule, keep strict sql_mode on, select only needed columns,
--    use TEXT (MySQL: in a side table if rarely read) for unbounded content.
```

---

## 🎯 Interview Tip (1 line)
Say: "255 is not magic — in MySQL I pick VARCHAR for bounded, indexed columns because TEXT needs prefix indexes, has no plain DEFAULT and is stored off-page, while in PostgreSQL VARCHAR(n) and TEXT perform identically so I use TEXT with a CHECK constraint when I need a limit; and I keep strict sql_mode so overflows error instead of truncating silently."

---

## 🔗 Related Questions
→ Q231 (PRIMARY KEY vs UNIQUE) | Q223 (B-Tree index) | Q008 (CAST types) | Q230 (InnoDB vs MyISAM)
