---

# Q003. NULL Handling - IS NULL, COALESCE, IFNULL, NULLIF
# Category: Fundamentals
# Difficulty: ⭐⭐ Medium
# DB: Both (MySQL + PostgreSQL)

---

## ❓ Question
In a `customers` table, find customers with no phone, display "N/A" instead of NULL, treat empty strings as missing, avoid divide-by-zero, and explain why `= NULL` and `NOT IN (..., NULL)` return nothing and how aggregates treat NULL.

---

## 💡 Quick Concept (2 lines only)
NULL means "unknown", so any comparison with it (`= NULL`, `<> x`, `NOT IN (.., NULL)`) yields UNKNOWN and WHERE drops the row; only `IS NULL` / `IS NOT NULL` work. COALESCE(a,b,..) returns the first non-NULL; NULLIF(a,b) returns NULL when a = b.
हिंदी: NULL = unknown, इसलिए `= NULL` कभी true नहीं होता; `IS NULL` use करो। COALESCE पहला non-NULL देता है, NULLIF बराबर होने पर NULL देता है।

---

## ✅ Answer / Solution

```sql
-- ============================================
-- SETUP (run this first)
-- ============================================

CREATE TABLE customers (
  id          INT PRIMARY KEY,
  name        VARCHAR(50),
  phone       VARCHAR(20),
  discount    DECIMAL(5,2),
  referred_by INT
);

INSERT INTO customers VALUES
  (1, 'Asha',   '98100', 10.00, NULL),
  (2, 'Ben',    NULL,     0.00, 1),
  (3, 'Chitra', '',       NULL, 1),      -- empty string, NOT NULL
  (4, 'Dev',    NULL,     NULL, NULL);

-- ============================================
-- SOLUTION
-- ============================================

-- Step 1: find missing phones (IS NULL, never = NULL)
SELECT id, name FROM customers WHERE phone IS NULL;

-- Step 2: show a default for NULL (COALESCE is ANSI: works on both)
SELECT id, name, COALESCE(phone, 'N/A') AS phone_shown, COALESCE(discount, 0) AS disc
FROM customers ORDER BY id;

-- Step 3: treat '' as missing too -> NULLIF turns '' into NULL, COALESCE then defaults it
SELECT id, COALESCE(NULLIF(phone, ''), 'N/A') AS phone_clean
FROM customers ORDER BY id;

-- Step 4: safe division, NULLIF(0,0) -> NULL -> result NULL instead of an error
SELECT 10 / NULLIF(0, 0) AS safe_div;

-- Step 5: aggregates skip NULL
SELECT COUNT(*) AS all_rows, COUNT(phone) AS non_null_phone,
       AVG(discount) AS avg_disc, SUM(discount) AS sum_disc
FROM customers;

-- ============================================
-- EXPECTED OUTPUT
-- ============================================

-- Step 1:  id | name         ->  2 | Ben ,  4 | Dev
-- Step 2:  id | name   | phone_shown | disc
--           1 | Asha   | 98100       | 10.00
--           2 | Ben    | N/A         |  0.00
--           3 | Chitra | (empty)     |  0.00   <- '' is not NULL, so it is NOT replaced
--           4 | Dev    | N/A         |  0.00
--          (PostgreSQL prints disc as 10.00 / 0.00 / 0 / 0 because COALESCE(discount, 0)
--           types differ slightly in display; values are the same)
-- Step 3:  1 | 98100 ;  2 | N/A ;  3 | N/A ;  4 | N/A
-- Step 4:  safe_div = NULL
-- Step 5:  all_rows | non_null_phone | avg_disc            | sum_disc
--                 4 |              2 | 5.000000 (MySQL)    | 10.00
--                 4 |              2 | 5.0000000000000000 (PostgreSQL) | 10.00
--          AVG = 10/2 = 5, NOT 10/4: NULL rows are excluded from the average.
```

---

## 🔍 Why This Works (3 lines max)
SQL uses three-valued logic (TRUE / FALSE / UNKNOWN) and WHERE keeps only TRUE rows. COALESCE and NULLIF are plain expressions that convert between NULL and real values. Aggregates other than COUNT(*) ignore NULL inputs.
हिंदी: SQL में true/false/unknown तीन values हैं और WHERE सिर्फ true रखता है; aggregates NULL को skip करते हैं।

---

## ⚡ Alternative Solution

```sql
-- MySQL-only two-argument shortcut (PostgreSQL: ERROR function ifnull(...) does not exist)
SELECT IFNULL(phone, 'N/A') FROM customers WHERE id = 2;      -- N/A
-- PostgreSQL / portable: COALESCE(phone, 'N/A')

-- NULL-safe equality (find rows "equal to NULL"):
-- MySQL:      WHERE phone <=> NULL                -- ids 2, 4 (verified)
-- PostgreSQL: WHERE phone IS NOT DISTINCT FROM NULL  -- ids 2, 4 (verified in PGlite)
-- MySQL 9.1.0 rejects IS NOT DISTINCT FROM (syntax error); PostgreSQL has no <=> operator.

-- Be careful: the "other" side of <> also drops NULLs
SELECT id, name FROM customers WHERE phone <> '98100';
-- Output: only 3 | Chitra   (Ben and Dev with NULL phone are silently excluded)
-- Fix: WHERE phone IS DISTINCT FROM '98100'  (PgSQL)  |  WHERE NOT (phone <=> '98100') (MySQL)
```

---

## ⚠️ Common Mistake

```sql
-- ❌ Wrong: equality with NULL
SELECT id, name FROM customers WHERE phone = NULL;
-- Output on both engines: 0 rows (comparison is UNKNOWN)
-- ✅ WHERE phone IS NULL

-- ❌ Wrong: NOT IN with a NULL in the list/subquery
SELECT id, name FROM customers WHERE referred_by NOT IN (1, NULL);
-- Output on both engines: 0 rows! (x NOT IN (1, NULL) = x<>1 AND x<>NULL -> never TRUE)
-- ✅ Use NOT EXISTS, or filter NULLs out of the subquery (WHERE col IS NOT NULL)

-- ❌ Wrong: assuming '' and NULL are the same (they are not, on either engine)
-- (Oracle treats them the same; MySQL and PostgreSQL do not)
```

---

## 🎯 Interview Tip (1 line)
Say: "NULL is three-valued logic - I use IS NULL, prefer NOT EXISTS over NOT IN when NULLs are possible, COALESCE for defaults, NULLIF for divide-by-zero, and remember aggregates skip NULL so AVG differs from SUM/COUNT(*)."

---

## 🔗 Related Questions
→ Q005 (IN vs EXISTS) | Q007 (CASE WHEN) | Q002 (DISTINCT) | Q239 (Find duplicates)
