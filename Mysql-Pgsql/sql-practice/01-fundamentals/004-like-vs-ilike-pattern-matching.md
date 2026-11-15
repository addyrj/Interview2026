---

# Q004. LIKE vs ILIKE (PgSQL) - Pattern Matching
# Category: Fundamentals
# Difficulty: ⭐ Easy
# DB: Both (MySQL + PostgreSQL)

---

## ❓ Question
Search a `products` table for names starting with "apple", containing "apple", and matching case-insensitively. Explain `%` vs `_`, escaping literal `%` / `_`, why MySQL and PostgreSQL behave differently on case, and why `LIKE '%x%'` cannot use a normal B-tree index.

---

## 💡 Quick Concept (2 lines only)
`%` = any run of characters, `_` = exactly one character. MySQL's LIKE is case-insensitive under the default `_ci` collation; PostgreSQL's LIKE is case-sensitive, so it adds `ILIKE` (or use `LOWER(col) LIKE ...`).
हिंदी: `%` = कितने भी अक्षर, `_` = एक अक्षर। MySQL में LIKE default case-insensitive है, PostgreSQL में case-sensitive, वहाँ ILIKE चाहिए।

---

## ✅ Answer / Solution

```sql
-- ============================================
-- SETUP (run this first)
-- ============================================

CREATE TABLE products (
  id   INT PRIMARY KEY,
  name VARCHAR(100),
  sku  VARCHAR(30)
);

INSERT INTO products VALUES
  (1, 'Apple iPhone 15',   'IP-15'),
  (2, 'apple watch',       'AW-9'),
  (3, 'Pineapple Juice',   'PJ_01'),
  (4, 'Samsung Galaxy',    'SG-24'),
  (5, '100% Cotton Shirt', 'SH-100'),
  (6, 'Applesauce',        'AS-1');

-- ============================================
-- SOLUTION
-- ============================================

-- Step 1: starts-with (prefix pattern, can use a B-tree index)
SELECT id, name FROM products WHERE name LIKE 'apple%' ORDER BY id;

-- Step 2: contains (leading % = no B-tree index)
SELECT id, name FROM products WHERE name LIKE '%apple%' ORDER BY id;

-- Step 3: portable case-insensitive search (works on BOTH engines)
SELECT id, name FROM products WHERE LOWER(name) LIKE 'apple%' ORDER BY id;

-- Step 4: single-character wildcard
SELECT id, name FROM products WHERE name LIKE '_pple%' ORDER BY id;

-- ============================================
-- EXPECTED OUTPUT
-- ============================================

-- Step 1  MySQL 9.1.0 (case-insensitive default collation): ids 1, 2, 6
--         PostgreSQL/PGlite (case-sensitive):               id 2 only  (apple watch)
-- Step 2  MySQL: ids 1, 2, 3, 6        PostgreSQL: ids 2, 3
-- Step 3  BOTH engines: ids 1, 2, 6  (Apple iPhone 15, apple watch, Applesauce)
-- Step 4  MySQL: ids 1, 2, 6           PostgreSQL: ids 1, 2, 6  ('_' matches A or a)
```

---

## 🔍 Why This Works (3 lines max)
LIKE compares using the column's collation: MySQL defaults to a case-insensitive one, PostgreSQL's default is case-sensitive. Lowercasing the column makes both behave the same, at the cost of defeating a plain index (use a functional index on `LOWER(name)`). A prefix pattern has a fixed start, so a B-tree can range-scan it; a leading `%` forces a full scan.
हिंदी: LIKE collation के हिसाब से चलता है; दोनों में same result चाहिए तो LOWER() लगाओ, और leading `%` पर normal index काम नहीं करता।

---

## ⚡ Alternative Solution

```sql
-- PostgreSQL ONLY: ILIKE and regex operators
SELECT id, name FROM products WHERE name ILIKE 'apple%' ORDER BY id;   -- ids 1, 2, 6 (verified in PGlite)
SELECT id, name FROM products WHERE name ~* '^apple' ORDER BY id;      -- ~* = case-insens. regex, ids 1, 2, 6
-- MySQL 9.1.0: ILIKE and ~* -> ERROR 1064 syntax error (verified)

-- MySQL ONLY: force case-sensitive with BINARY, regex with REGEXP
SELECT id, name FROM products WHERE name LIKE BINARY 'apple%';         -- id 2 only (verified)
SELECT id, name FROM products WHERE name REGEXP '^apple' ORDER BY id;  -- ids 1, 2, 6 (case-insens. by collation)
-- PostgreSQL: LIKE BINARY / REGEXP -> syntax errors (verified in PGlite)

-- Literal % and _ must be escaped
SELECT id, name FROM products WHERE name LIKE '%100\% %';              -- id 5 on MySQL
SELECT id, sku  FROM products WHERE sku  LIKE '%!_%' ESCAPE '!';       -- id 3 (PJ_01) on BOTH engines
-- Backslash is the default LIKE escape char in both engines (both ran fine), but an explicit
-- ESCAPE '!' is the portable form (MySQL's NO_BACKSLASH_ESCAPES mode would change the first one).
-- Both functional indexes below were created successfully (MySQL 9.1.0 and PGlite).

-- Fast contains-search at scale (NOT run here: pg_trgm is not bundled in this PGlite setup):
-- PostgreSQL: CREATE EXTENSION pg_trgm; CREATE INDEX ON products USING gin (name gin_trgm_ops);
-- MySQL:      FULLTEXT index + MATCH(name) AGAINST('apple')
```

---

## ⚠️ Common Mistake

```sql
-- ❌ Wrong: assuming the same LIKE result on both engines
SELECT * FROM products WHERE name LIKE 'apple%';
-- MySQL returns 3 rows, PostgreSQL returns 1 row -> bug when you migrate databases
-- ✅ State intent: ILIKE (PgSQL) or LOWER(name) LIKE 'apple%' (portable)

-- ❌ Wrong: wrapping the column in a function and expecting the plain index to be used
SELECT * FROM products WHERE LOWER(name) LIKE 'apple%';
-- ✅ PostgreSQL: CREATE INDEX idx_prod_lower ON products (LOWER(name) text_pattern_ops);
-- ✅ MySQL 8+: CREATE INDEX idx_prod_lower ON products ((LOWER(name)));  -- functional index

-- ❌ Wrong: forgetting that NOT LIKE also skips NULL names
```

---

## 🎯 Interview Tip (1 line)
Say: "Prefix LIKE can use a B-tree, but `%term%` can't - for real search I'd use pg_trgm GIN in PostgreSQL or FULLTEXT in MySQL, and I'd remember MySQL's LIKE is case-insensitive by collation while PostgreSQL's isn't."

---

## 🔗 Related Questions
→ Q009 (String functions) | Q003 (NULL handling) | Q005 (IN vs EXISTS) | Q008 (Type casting)
