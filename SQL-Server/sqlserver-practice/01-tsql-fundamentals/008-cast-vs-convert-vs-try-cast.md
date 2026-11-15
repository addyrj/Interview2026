---

# Q008. CAST vs CONVERT vs TRY_CAST
# Category: T-SQL Fundamentals
# Difficulty: ⭐⭐ Medium
# DB: SQL Server (TRY_CAST/TRY_CONVERT 2012+; PostgreSQL has ::type, MySQL has CAST/CONVERT with different syntax)

---

## ❓ Question
Explain the difference between `CAST`, `CONVERT` (with style codes) and `TRY_CAST`/`TRY_CONVERT`. Show integer division pitfalls, how decimals truncate when cast to INT, how to safely clean a dirty import column, and what implicit conversion does to performance.

---

## 💡 Quick Concept (2 lines only)
`CAST` is ANSI; `CONVERT(type, value, style)` is T-SQL with style codes for dates/numbers. `TRY_CAST`/`TRY_CONVERT` return NULL instead of raising an error when conversion fails. Implicit conversion follows data type precedence (the lower-precedence side is converted).
हिंदी: CAST fail हो तो query error देती है, TRY_CAST NULL देता है। Dirty data import में TRY_CAST काम आता है।

---

## ✅ Answer / Solution

```sql
-- ============================================
-- SETUP: a dirty staging table from a CSV import
-- ============================================

CREATE TABLE dbo.StagingPayments (
  RowId      INT          NOT NULL PRIMARY KEY,
  AmountText VARCHAR(20)  NOT NULL,
  PaidOnText VARCHAR(20)  NOT NULL
);

INSERT INTO dbo.StagingPayments (RowId, AmountText, PaidOnText) VALUES
  (1, '120.50',  '2024-03-15'),
  (2, 'abc',     '2024-03-16'),
  (3, '99',      '2024-13-45'),     -- invalid date
  (4, '1,250.00','2024-03-17');     -- thousands separator

-- ============================================
-- SOLUTION: clean load with TRY_CAST
-- ============================================

SELECT RowId,
       TRY_CAST(AmountText AS DECIMAL(10,2)) AS Amount,
       TRY_CAST(PaidOnText AS DATE)          AS PaidOn
FROM dbo.StagingPayments
ORDER BY RowId;

-- RowId | Amount | PaidOn
-- 1     | 120.50 | 2024-03-15
-- 2     | NULL   | 2024-03-16
-- 3     | 99.00  | NULL
-- 4     | NULL   | 2024-03-17     (assumed: '1,250.00' with a comma does not convert to DECIMAL)

-- Rows with problems for a reject table:
SELECT RowId FROM dbo.StagingPayments
WHERE TRY_CAST(AmountText AS DECIMAL(10,2)) IS NULL
   OR TRY_CAST(PaidOnText AS DATE) IS NULL;    -- 2, 3, 4

-- ============================================
-- Numeric behaviour
-- ============================================

SELECT 10 / 4                      AS IntDivision,     -- 2   (INT / INT)
       10 / 4.0                    AS DecimalDivision, -- 2.5 (shown with extra scale, e.g. 2.500000)
       CAST(19.99 AS INT)          AS Truncated,       -- 19  (truncates, never rounds)
       CAST(ROUND(19.99, 0) AS INT) AS Rounded;        -- 20

-- CONVERT with style: date <-> string
SELECT CONVERT(VARCHAR(10), CAST('2024-03-15' AS DATE), 103) AS BritishStyle,  -- 15/03/2024
       CONVERT(VARCHAR(10), CAST('2024-03-15' AS DATE), 112) AS Iso8601Basic;  -- 20240315

-- Note: the integer/decimal arithmetic and the 'abc' -> failure case were checked on SQLite
-- (CAST semantics differ there: SQLite never raises an error and returns 0 for CAST('abc' AS INTEGER),
-- which is why the TRY_CAST NULL results and the comma-separated '1,250.00' case are per Microsoft docs
-- and my expectation, not an executed result). Not executed on SQL Server.
```

---

## 🔍 Why This Works (3 lines max)
TRY_CAST catches the conversion failure and returns NULL, so a set-based `INSERT ... SELECT` doesn't abort the whole batch on one bad row. CONVERT's style parameter controls string formatting for dates (e.g. 112 = yyyymmdd, 103 = dd/mm/yyyy), which CAST cannot do.
हिंदी: TRY_CAST = error की जगह NULL। Style code सिर्फ CONVERT में मिलता है।

---

## ⚡ Alternative Solution

```sql
-- TRY_CONVERT with style, plus ISDATE/ISNUMERIC (legacy - unreliable, avoid)
SELECT TRY_CONVERT(DATE, '15/03/2024', 103) AS ParsedDate;   -- 2024-03-15

-- PARSE / TRY_PARSE use .NET culture rules (slow, CLR) - fine for one-off scripts only
SELECT TRY_PARSE('1,250.00' AS DECIMAL(10,2) USING 'en-US') AS Parsed;  -- 1250.00 (per docs)
```

---

## ⚠️ Common Mistake

```sql
-- ❌ Wrong: relying on ISNUMERIC to validate numbers
SELECT ISNUMERIC('$'), ISNUMERIC(',');   -- both return 1, yet neither converts to INT
-- ✅ TRY_CAST(x AS DECIMAL(10,2)) IS NOT NULL

-- ❌ Wrong: integer division when a ratio is expected
SELECT 3 / 4;               -- 0
-- ✅ SELECT 3 * 1.0 / 4;    -- 0.75

-- ❌ Wrong: implicit conversion on an indexed column (performance killer)
DECLARE @id NVARCHAR(10) = N'1001';
SELECT * FROM dbo.Orders WHERE OrderCode = @id;   -- OrderCode is VARCHAR -> column converted -> scan
-- ✅ Match the parameter type to the column type (VARCHAR with VARCHAR)

-- ❌ Wrong: CAST(col AS VARCHAR) inside WHERE/JOIN on large tables -> non-SARGable
-- ❌ Wrong: ambiguous date strings without a style or ISO format.
```

---

## 🎯 Interview Tip (1 line)
Say: "I use TRY_CAST in ETL/staging so bad rows become NULL and get routed to a reject table, CONVERT only when I need a style, and I always match parameter types to column types — mismatched NVARCHAR/VARCHAR parameters from ORMs are a classic cause of implicit-conversion scans, which I spot as CONVERT_IMPLICIT warnings in the plan."

---

## 🔗 Related Questions
→ Q143 (Avoiding implicit conversions) | Q110 (SARGable predicates) | Q021 (Data types) | Q022 (VARCHAR vs NVARCHAR) | Q161 (Parameterized queries from Node)
