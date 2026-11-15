---

# Q009. String Functions - CONCAT, SUBSTRING, TRIM, UPPER, LOWER
# Category: Fundamentals
# Difficulty: ⭐⭐ Medium
# DB: Both (MySQL + PostgreSQL)

---

## ❓ Question
Clean a `contacts` table: build a full name from messy parts (spaces, NULL middle name), normalise case, extract the email domain, and count characters. Which behaviours differ between MySQL and PostgreSQL (NULL in CONCAT, `||`, negative SUBSTRING, LENGTH on Unicode)?

---

## 💡 Quick Concept (2 lines only)
CONCAT / CONCAT_WS / TRIM / UPPER / LOWER / SUBSTRING / REPLACE / LEFT / RIGHT exist in both engines, but NULL handling and indexing rules differ. CONCAT with a NULL gives NULL in MySQL but ignores the NULL in PostgreSQL; `||` is concatenation only in PostgreSQL.
हिंदी: ज़्यादातर string functions दोनों में हैं, पर NULL का व्यवहार अलग है: MySQL CONCAT में NULL आए तो NULL, PostgreSQL उसे छोड़ देता है।

---

## ✅ Answer / Solution

```sql
-- ============================================
-- SETUP (run this first)
-- ============================================

CREATE TABLE contacts (
  id         INT PRIMARY KEY,
  first_name VARCHAR(30),
  last_name  VARCHAR(30),
  email      VARCHAR(80),
  middle     VARCHAR(30)
);

INSERT INTO contacts VALUES
  (1, '  aditya ', 'RANJAN', 'Aditya.Ranjan@Example.COM', NULL),   -- padded name, no middle
  (2, 'meera',     'Iyer',   'meera@corp.in',             'K');

-- ============================================
-- SOLUTION
-- ============================================

-- Step 1: CONCAT_WS skips NULL parts and takes a separator (works on both engines)
SELECT id, CONCAT_WS(' ', TRIM(first_name), middle, last_name) AS full_name
FROM contacts ORDER BY id;

-- Step 2: TRIM + case functions
SELECT id, UPPER(TRIM(first_name)) AS up, LOWER(email) AS low_email FROM contacts ORDER BY id;

-- Step 3: domain = text after '@'  (POSITION + SUBSTRING is portable)
SELECT id, LOWER(SUBSTRING(email, POSITION('@' IN email) + 1)) AS domain
FROM contacts ORDER BY id;

-- Step 4: length before / after TRIM
SELECT id, LENGTH(first_name) AS len_raw, LENGTH(TRIM(first_name)) AS len_trim
FROM contacts ORDER BY id;

-- ============================================
-- EXPECTED OUTPUT (identical on MySQL 9.1.0 and PGlite)
-- ============================================

-- Step 1: 1 | aditya RANJAN      2 | meera K Iyer
-- Step 2: 1 | ADITYA | aditya.ranjan@example.com     2 | MEERA | meera@corp.in
-- Step 3: 1 | example.com        2 | corp.in
-- Step 4: 1 | 9 | 6              2 | 5 | 5
```

---

## 🔍 Why This Works (3 lines max)
TRIM strips leading and trailing spaces so the padded name becomes `aditya`; CONCAT_WS drops the NULL middle name without producing a double space or NULL result. `POSITION('@' IN email)` finds the separator and SUBSTRING takes the rest of the string. Functions on a column stop plain-index use, so normalise on write or add a functional index.
हिंदी: TRIM किनारे के spaces हटाता है, CONCAT_WS NULL को छोड़ देता है, और POSITION + SUBSTRING से `@` के बाद का हिस्सा मिलता है।

---

## ⚡ Alternative Solution

```sql
-- Engine-specific domain extraction:
SELECT SUBSTRING_INDEX(email, '@', -1) FROM contacts;   -- MySQL only; PGlite: ERROR function does not exist
SELECT SPLIT_PART(email, '@', 2)       FROM contacts;   -- PostgreSQL only; MySQL: ERROR 1305 FUNCTION SPLIT_PART does not exist
-- Output (case preserved): Example.COM / corp.in

-- CONCAT vs CONCAT_WS with NULL (middle is NULL for id 1):
SELECT id, CONCAT(TRIM(first_name), ' ', middle, ' ', last_name) AS c1 FROM contacts;
--  MySQL:      id 1 -> NULL            | id 2 -> meera K Iyer
--  PostgreSQL: id 1 -> 'aditya  RANJAN' (NULL ignored, double space left) | id 2 -> meera K Iyer

-- Pipe operator: PostgreSQL concatenation. In MySQL (default mode) || means logical OR!
SELECT first_name || ' ' || last_name FROM contacts;
--  PostgreSQL: '  aditya  RANJAN' / 'meera Iyer'      MySQL 9.1.0: 0 / 0   (no error, wrong result)

-- Title Case: INITCAP('iyer') exists only in PostgreSQL (MySQL ERROR 1305). MySQL has no built-in.

-- Negative start in SUBSTRING:
SELECT SUBSTRING(email, -3) FROM contacts;
--  MySQL: last 3 chars ('COM', '.in')    PostgreSQL: returns the WHOLE string (start < 1 is clamped)
--  Portable: RIGHT(email, 3)  -> 'COM', '.in' on both engines (RIGHT(last_name, 2) was run on both)
```

---

## ⚠️ Common Mistake

```sql
-- ❌ Wrong: LENGTH() on non-ASCII text in MySQL counts BYTES
SELECT LENGTH('नमस्ते'), CHAR_LENGTH('नमस्ते');
--  MySQL 9.1.0: 18 | 6        PostgreSQL: 6 | 6
-- ✅ Use CHAR_LENGTH() everywhere when you mean characters

-- ❌ Wrong: WHERE LOWER(email) = 'x' expecting an index on email to be used
-- ✅ PostgreSQL: CREATE INDEX ON contacts (LOWER(email));   MySQL 8+: CREATE INDEX i ON contacts ((LOWER(email)));
--    (MySQL's default collation is already case-insensitive, so LOWER() is often unnecessary there)

-- ❌ Wrong: CONCAT(a, ' ', b) with a nullable column and assuming a result - MySQL gives NULL
-- ✅ CONCAT_WS(' ', a, b) or COALESCE(col, '')
```

---

## 🎯 Interview Tip (1 line)
Say: "String functions on a filtered column kill index use, so I normalise at write time or add a functional index, I use CONCAT_WS to be NULL-safe, and I remember `||` and byte-vs-char LENGTH differ between MySQL and PostgreSQL."

---

## 🔗 Related Questions
→ Q004 (LIKE vs ILIKE) | Q003 (NULL handling) | Q008 (Type casting) | Q239 (Find duplicates)
