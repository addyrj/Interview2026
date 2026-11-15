---

# Q039. Collation — utf8 vs utf8mb4 (MySQL) — Emoji Problem
# Category: Data Types & DDL
# Difficulty: ⭐⭐ Medium
# DB: MySQL (PostgreSQL notes included)

---

## ❓ Question
A MySQL `utf8` column rejects or mangles an emoji (`😀`). Why? Show the failure, the fix, and explain collations (case/accent sensitivity). How does PostgreSQL differ?

---

## 💡 Quick Concept (2 lines only)
MySQL `utf8` (= `utf8mb3`) stores max 3 bytes per char, but emoji need 4, so you must use `utf8mb4`. Collation (e.g. `utf8mb4_0900_ai_ci`) decides comparison/sort rules: accent-insensitive, case-insensitive.
हिंदी: MySQL का `utf8` सिर्फ 3 byte देता है, emoji के लिए `utf8mb4` चाहिए; collation तय करता है कि compare कैसे होगा।

---

## ✅ Answer / Solution

```sql
-- ============================================
-- SETUP (MySQL 8.0+, verified on 9.1.0)
-- ============================================

SET NAMES utf8mb4;   -- client connection must also be utf8mb4

CREATE TABLE comments_legacy (id INT PRIMARY KEY, body VARCHAR(100))
  CHARACTER SET utf8mb3 COLLATE utf8mb3_general_ci;
CREATE TABLE comments_modern (id INT PRIMARY KEY, body VARCHAR(100))
  CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci;

INSERT INTO comments_modern VALUES (1,'Great product 😀'),(2,'café'),(3,'CAFE'),(4,'cafe');

-- ============================================
-- SOLUTION
-- ============================================

-- Step 1: the failure (strict sql_mode, the default)
INSERT INTO comments_legacy VALUES (1,'Great product 😀');
-- ERROR 1366 (HY000): Incorrect string value: '\xF0\x9F\x98\x80' for column 'body' at row 1

-- Step 1b: non-strict mode silently corrupts data instead (worse!)
SET SESSION sql_mode = '';
INSERT INTO comments_legacy VALUES (2,'Great product 😀');   -- Warning 1366, emoji becomes '?'
SET SESSION sql_mode = DEFAULT;
SELECT id, body, HEX(body) FROM comments_legacy;

-- Step 2: bytes vs chars on utf8mb4
SELECT id, body, CHAR_LENGTH(body) AS chars, LENGTH(body) AS bytes FROM comments_modern ORDER BY id;

-- Step 3: collation effects
SELECT id, body FROM comments_modern WHERE body = 'cafe' ORDER BY id;                              -- ai_ci: matches all 3
SELECT id, body FROM comments_modern WHERE body = 'cafe' COLLATE utf8mb4_0900_as_cs ORDER BY id;   -- exact match only

-- Step 4: the fix
ALTER TABLE comments_legacy CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci;
INSERT INTO comments_legacy VALUES (3,'Now works 😀');

-- ============================================
-- EXPECTED OUTPUT (MySQL 9.1.0)
-- ============================================

-- Step 1b:  id | body            | HEX(body)
--           2  | Great product ? | 47726561742070726F64756374203F      (emoji lost; 0x3F = '?')
-- Step 2:   id | body            | chars | bytes
--           1  | Great product 😀 | 15    | 18        (emoji = 4 bytes)
--           2  | café            | 4     | 5         (é = 2 bytes)
--           3  | CAFE            | 4     | 4
--           4  | cafe            | 4     | 4
-- Step 3a:  ids 2, 3, 4 (café, CAFE, cafe)       Step 3b: id 4 only
-- Step 4:   id 2 stays 'Great product ?' (already corrupted - conversion can't restore it), id 3 = 'Now works 😀'
```

---

## 🔍 Why This Works (3 lines max)
utf8mb4 is real UTF-8 (1-4 bytes); utf8mb3 can't hold code points above U+FFFF. A collation suffix means: `ai` accent-insensitive, `as` accent-sensitive, `ci` case-insensitive, `cs` case-sensitive. In MySQL 8.0+ the default is already `utf8mb4` / `utf8mb4_0900_ai_ci` (confirmed on 9.1.0).
हिंदी: utf8mb4 असली UTF-8 है; ai/as = accent, ci/cs = case sensitivity; 8.0+ में default पहले से utf8mb4 है।

---

## ⚡ Alternative Solution

```sql
-- Check what you have
SELECT @@character_set_server, @@collation_server;   -- utf8mb4 | utf8mb4_0900_ai_ci on 8.0+/9.x
SELECT TABLE_NAME, TABLE_COLLATION FROM information_schema.TABLES WHERE TABLE_SCHEMA = DATABASE();

-- Old MySQL 5.7 configs: set in my.cnf
-- [mysqld] character-set-server=utf8mb4  collation-server=utf8mb4_unicode_ci
-- Index-length trap: 5.7 InnoDB max key 767 bytes (older row formats) -> VARCHAR(255) utf8mb4 = 1020 bytes can fail to index;
-- 8.0 DYNAMIC row format allows 3072 bytes (not exercised here).

-- PostgreSQL (verified on PGlite 18.6): database encoding UTF8 already stores emoji natively, no utf8mb4 problem
--   SHOW server_encoding;  -> UTF8
--   chars/bytes for 'Great product 😀' = 15 / 18 (same as MySQL)
--   Default comparison is case-SENSITIVE: WHERE body = 'cafe' returns only id 4; 'a' = 'A' is false.
--   Case-insensitive options: WHERE lower(body) = 'cafe'  (returns ids 3,4 - accent still matters),
--   citext extension (not available in PGlite, not run), or a nondeterministic ICU collation:
CREATE COLLATION ci_ai (provider = icu, locale = 'und-u-ks-level1', deterministic = false);   -- accepted on PGlite
--   (nondeterministic collations can't be used with LIKE on older PG versions and have performance cost)
```

---

## ⚠️ Common Mistake
```sql
-- ❌ Wrong: ALTER DATABASE ... CHARACTER SET utf8mb4 and assuming existing tables changed (only NEW tables inherit it)
-- ✅ Correct: ALTER TABLE t CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci;  per table (rewrites the table!)

-- ❌ Wrong: table is utf8mb4 but the connection is still latin1/utf8 -> emoji arrive as '?' -> use SET NAMES utf8mb4 / driver charset
-- ❌ Wrong: mixing collations in a JOIN/compare -> ERROR 1267 Illegal mix of collations; or index not used after COLLATE/CONVERT on the column
-- ❌ Wrong: disabling strict mode to "hide" error 1366 -> silent data loss (shown above)
```

---

## 🎯 Interview Tip (1 line)
Say: "Always utf8mb4 end to end — database, table, column and connection; MySQL's `utf8` is a 3-byte subset; mixed collations break joins and indexes; converting large tables rewrites them so I plan it as an online migration (gh-ost) — and Postgres is UTF-8 native, so there the discussion is case/accent-insensitive comparison via citext or ICU collations."

---

## 🔗 Related Questions
→ Q040 (Storage engines) | Q032 (ALTER TABLE online) | Q033 (Index on large table) | String functions
