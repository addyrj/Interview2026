---

# Q004. NULL Handling — ISNULL, COALESCE, NULLIF, IIF
# Category: T-SQL Fundamentals
# Difficulty: ⭐⭐ Medium
# DB: SQL Server (ISNULL is T-SQL only; MySQL has IFNULL, PostgreSQL uses COALESCE)

---

## ❓ Question
A `Customers` table has NULL phones, NULL discounts and an empty-string phone. Show a display phone ('N/A' when missing), a discount defaulting to 0, convert empty strings to NULL, avoid divide-by-zero, and find rows with no discount. Explain ISNULL vs COALESCE.

---

## 💡 Quick Concept (2 lines only)
Any comparison with NULL is UNKNOWN, so `= NULL` never matches; use `IS NULL`. `ISNULL(a,b)` takes exactly 2 args and returns the TYPE of `a`; `COALESCE(a,b,c...)` is ANSI, takes many args and follows data type precedence.
हिंदी: NULL = NULL भी true नहीं होता, हमेशा IS NULL लिखो। ISNULL = 2 args, COALESCE = कई।

---

## ✅ Answer / Solution

```sql
-- ============================================
-- SETUP
-- ============================================

CREATE TABLE dbo.Customers (
  CustomerId  INT           NOT NULL PRIMARY KEY,
  FullName    NVARCHAR(100) NOT NULL,
  Phone       VARCHAR(20)   NULL,
  DiscountPct INT           NULL,
  CreditLimit INT           NULL
);

INSERT INTO dbo.Customers (CustomerId, FullName, Phone, DiscountPct, CreditLimit) VALUES
  (1, N'Anita Rao',    '98100-11111', 10,   5000),
  (2, N'Bikram Sen',   NULL,          NULL, 0),
  (3, N'Chitra Nair',  '',            5,    2000),   -- empty string, NOT NULL
  (4, N'Dev Patel',    NULL,          NULL, NULL);

-- ============================================
-- SOLUTION
-- ============================================

SELECT CustomerId,
       ISNULL(Phone, 'N/A')                    AS PhoneDisplay,
       COALESCE(DiscountPct, 0)                AS Discount,
       NULLIF(Phone, '')                       AS PhoneOrNull,
       IIF(CreditLimit IS NULL OR CreditLimit = 0, 'No credit', 'Has credit') AS Credit,
       100000 / NULLIF(CreditLimit, 0)         AS Ratio       -- no divide-by-zero
FROM dbo.Customers
ORDER BY CustomerId;

-- CustomerId | PhoneDisplay | Discount | PhoneOrNull | Credit     | Ratio
-- 1          | 98100-11111  | 10       | 98100-11111 | Has credit | 20
-- 2          | N/A          | 0        | NULL        | No credit  | NULL
-- 3          | (empty)      | 5        | NULL        | Has credit | 50
-- 4          | N/A          | 0        | NULL        | No credit  | NULL

-- Finding NULL discounts:
SELECT CustomerId FROM dbo.Customers WHERE DiscountPct IS NULL;   -- 2, 4
SELECT CustomerId FROM dbo.Customers WHERE DiscountPct = NULL;    -- 0 rows (UNKNOWN)

-- Aggregates ignore NULL: COUNT(*) = 4, COUNT(DiscountPct) = 2, AVG(DiscountPct) = 7 (INT average: 15/2)
-- (SQLite shows 7.5 because it does not do integer AVG; SQL Server AVG of INT returns INT.)

-- Note: values derived from equivalent query on SQLite (IFNULL for ISNULL, CASE for IIF);
-- not executed on SQL Server. The INT-truncated AVG and the ISNULL/COALESCE
-- typing rules are per Microsoft docs.
```

---

## 🔍 Why This Works (3 lines max)
`NULLIF(x, y)` returns NULL when x = y, which turns a would-be divide-by-zero (or an empty string) into NULL that downstream logic handles. `COALESCE` is shorthand for a CASE over its arguments; `ISNULL` is a function with a fixed output type taken from the first argument, so a short first argument can truncate the replacement value.
हिंदी: NULLIF(x,0) divide-by-zero बचाता है। ISNULL का result type पहले argument जैसा रहता है।

---

## ⚡ Alternative Solution

```sql
-- ISNULL truncation trap: type comes from the FIRST argument
DECLARE @short VARCHAR(3) = NULL;
SELECT ISNULL(@short, 'Unknown')   AS WithIsNull,    -- 'Unk'  (truncated to VARCHAR(3))
       COALESCE(@short, 'Unknown') AS WithCoalesce;   -- 'Unknown'

-- Same logic written with CASE (portable to any DB):
SELECT CASE WHEN Phone IS NULL OR Phone = '' THEN 'N/A' ELSE Phone END AS PhoneDisplay
FROM dbo.Customers;
```

---

## ⚠️ Common Mistake

```sql
-- ❌ Wrong: = NULL / <> NULL
SELECT * FROM dbo.Customers WHERE DiscountPct = NULL;   -- always empty
-- ✅ WHERE DiscountPct IS NULL

-- ❌ Wrong: NOT IN with a NULL in the list returns nothing
SELECT * FROM dbo.Customers WHERE CustomerId NOT IN (1, NULL);   -- 0 rows
-- ✅ Use NOT EXISTS, or filter NULLs out of the subquery.

-- ❌ Wrong: assuming '' is NULL (that is Oracle, not SQL Server)
SELECT ISNULL(Phone, 'N/A') FROM dbo.Customers WHERE CustomerId = 3;  -- returns '' not 'N/A'
-- ✅ ISNULL(NULLIF(Phone, ''), 'N/A')

-- ❌ Wrong: ISNULL with a column that is NOT NULL is pointless noise; also ISNULL in WHERE
-- on an indexed column (WHERE ISNULL(Col, 0) = 0) makes the predicate non-SARGable.
```

---

## 🎯 Interview Tip (1 line)
Say: "I default to COALESCE for portability and multi-arg fallbacks, and know ISNULL's first-argument typing behaviour and that it's evaluated once while COALESCE can re-evaluate subqueries. I use NULLIF for divide-by-zero and empty-string cleanup, and I'm careful with three-valued logic in NOT IN."

---

## 🔗 Related Questions
→ Q005 (CASE expressions) | Q053 (Anti-joins, NOT IN trap) | Q062 (Aggregate functions with NULL) | Q041 (EXISTS vs IN vs JOIN)
