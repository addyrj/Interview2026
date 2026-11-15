---

# Q008. Type Casting - CAST vs :: (PgSQL)
# Category: Fundamentals
# Difficulty: ⭐⭐ Medium
# DB: Both (MySQL + PostgreSQL)

---

## ❓ Question
Convert strings to numbers and dates, numbers to text, and avoid integer-division surprises. Compare `CAST(x AS type)`, the PostgreSQL `x::type` shorthand and MySQL's `CONVERT`. What happens on `'10abc'`, and which target type names does each engine accept?

---

## 💡 Quick Concept (2 lines only)
`CAST(x AS type)` is ANSI SQL; `x::type` is PostgreSQL-only shorthand for the same thing. MySQL only allows a fixed list of CAST targets (SIGNED, UNSIGNED, DECIMAL, CHAR, DATE, DATETIME, JSON...) and is lenient (implicit conversion with warnings), while PostgreSQL is strict and raises errors.
हिंदी: `CAST` हर जगह चलता है, `::` सिर्फ PostgreSQL में; MySQL ढीला है (warning देकर चलता है), PostgreSQL सख्त है (error देता है)।

---

## ✅ Answer / Solution

```sql
-- ============================================
-- SETUP: no tables needed, literals are enough
-- ============================================

-- ============================================
-- SOLUTION
-- ============================================

-- Step 1: string -> integer
-- MySQL:
SELECT CAST('123' AS SIGNED) AS n;           -- 123
-- PostgreSQL:
SELECT CAST('123' AS INTEGER) AS n;          -- 123
SELECT '123'::INTEGER AS n;                  -- 123 (shorthand)

-- Step 2: string -> date (works in BOTH engines with CAST)
SELECT CAST('2024-03-15' AS DATE) AS d;      -- 2024-03-15
-- PostgreSQL only: SELECT '2024-03-15'::DATE;

-- Step 3: decimal rounding - cast to fewer decimals ROUNDS (does not truncate)
SELECT CAST(12.567 AS DECIMAL(10,1)) AS dec1;   -- 12.6 on both engines

-- Step 4: decimal -> integer also rounds
-- MySQL:      SELECT CAST(12.567 AS SIGNED);    -- 13
-- PostgreSQL: SELECT CAST(12.567 AS INTEGER);   -- 13

-- Step 5: number -> text
-- MySQL:      SELECT CAST(123 AS CHAR);         -- '123'
-- PostgreSQL: SELECT CAST(123 AS VARCHAR(10));  -- '123'   (or AS TEXT)

-- Step 6: integer division
SELECT 7 / 2;
-- MySQL:      3.5000   (/ is always decimal division; use 7 DIV 2 for 3)
-- PostgreSQL: 3        (int / int = int; use 7 / 2.0 or 7::numeric / 2 for 3.5)

-- ============================================
-- EXPECTED OUTPUT (what I actually saw)
-- ============================================

-- MySQL 9.1.0:  CAST('123' AS SIGNED)=123 | CAST('2024-03-15' AS DATE)=2024-03-15
--               CAST(12.567 AS DECIMAL(10,1))=12.6 | CAST(12.567 AS SIGNED)=13 | 7/2=3.5000
-- PGlite:       CAST('123' AS INTEGER)=123 | '123'::INTEGER=123 | CAST('2024-03-15' AS DATE)=2024-03-15
--               12.6 | CAST(12.567 AS INTEGER)=13 | 7/2=3 | 7/2.0=3.5000000000000000
```

---

## 🔍 Why This Works (3 lines max)
CAST tells the engine to convert using the target type's input rules; `::` is the same operation with PostgreSQL's operator syntax. MySQL silently coerces mixed-type expressions, PostgreSQL requires an explicit cast when types do not match. Casting a decimal to a narrower decimal or integer rounds to nearest.
हिंदी: CAST target type के rules से convert करता है; MySQL mismatch पर चुपचाप convert करता है, PostgreSQL में explicit cast चाहिए।

---

## ⚡ Alternative Solution

```sql
-- MySQL-only: CONVERT(expr, type)
SELECT CONVERT('42', SIGNED);               -- 42 on MySQL; PGlite: ERROR column "signed" does not exist

-- Target-type names differ - both of these FAIL on the other engine (verified):
-- MySQL 9.1.0: CAST('123' AS INTEGER)       -> ERROR 1064;  CAST(123 AS VARCHAR(10)) / AS TEXT -> ERROR 1064
-- PGlite:      CAST('123' AS SIGNED)        -> ERROR: type "signed" does not exist
-- Portable-ish choice: CAST(x AS DECIMAL(p,s)) and CAST(x AS DATE) work in both.

-- Safe cast for dirty data (no TRY_CAST in either engine; SQL Server has it):
-- MySQL 9.1.0 (verified, returns NULL):
SELECT CASE WHEN '10abc' REGEXP '^[0-9]+$' THEN CAST('10abc' AS SIGNED) END;
-- PostgreSQL: use the same guard on a COLUMN, e.g.
--   SELECT CASE WHEN code ~ '^[0-9]+$' THEN code::INT END FROM t;
-- (With a constant literal PGlite still raised the error, because the planner folds the
--  constant cast before CASE runs - so test guards against real columns, not literals.)
-- Newer PostgreSQL (16+) has pg_input_is_valid(text, type) for validating a cast.
```

---

## ⚠️ Common Mistake

```sql
-- ❌ Wrong: trusting MySQL's implicit conversion
SELECT '10abc' + 5;     -- MySQL 9.1.0: returns 15 (with a truncation warning!)
SELECT 'abc' = 0;       -- MySQL 9.1.0: returns 1 (TRUE) - 'abc' silently becomes 0
-- PostgreSQL (PGlite): ERROR: invalid input syntax for type integer: "10abc"
-- ✅ Cast explicitly and validate input; consider STRICT sql_mode in MySQL

-- ❌ Wrong: CAST(123 AS CHAR) in PostgreSQL
SELECT CAST(123 AS CHAR);     -- PGlite returned '1'  (CHAR = CHAR(1)! it truncates)
-- ✅ Use VARCHAR / TEXT in PostgreSQL:  CAST(123 AS TEXT)

-- ❌ Wrong: expecting 3.5 from 7/2 in PostgreSQL (returns 3). ✅ 7/2.0 or 7::numeric/2
-- ❌ Wrong: comparing '10' < '9' as text (true: string order) when you wanted numeric
```

---

## 🎯 Interview Tip (1 line)
Say: "I use CAST for portability and `::` only in PostgreSQL-only code; I never rely on implicit conversion - MySQL hides bad data with warnings, PostgreSQL fails loudly - and I watch integer division and CAST AS CHAR(1) traps."

---

## 🔗 Related Questions
→ Q003 (NULL handling) | Q010 (Date/time functions) | Q006 (BETWEEN edge cases) | Q009 (String functions)
