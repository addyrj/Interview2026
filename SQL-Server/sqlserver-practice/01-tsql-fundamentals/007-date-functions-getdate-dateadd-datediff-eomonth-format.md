---

# Q007. Date Functions — GETDATE, DATEADD, DATEDIFF, EOMONTH, FORMAT
# Category: T-SQL Fundamentals
# Difficulty: ⭐⭐ Medium
# DB: SQL Server (EOMONTH 2012+, FORMAT 2012+; MySQL: DATE_ADD/DATEDIFF differ, PostgreSQL: interval arithmetic)

---

## ❓ Question
Show how to add days/months to a date, count days between two dates, get the first and last day of a month, format a date for display, and explain why `DATEDIFF(year, '2023-12-31', '2024-01-01')` returns 1. Then write a SARGable "orders in March 2024" filter.

---

## 💡 Quick Concept (2 lines only)
`DATEADD(part, n, date)` shifts a date; `DATEDIFF(part, start, end)` counts BOUNDARIES crossed, not elapsed time. `GETDATE()` returns local DATETIME, `SYSDATETIME()` DATETIME2 with more precision, `SYSUTCDATETIME()` UTC (Azure SQL servers run in UTC).
हिंदी: DATEDIFF boundary गिनता है, पूरा साल/महीना नहीं। Dates पर function लगाकर WHERE मत लिखो।

---

## ✅ Answer / Solution

```sql
-- ============================================
-- SETUP
-- ============================================

CREATE TABLE dbo.Orders (
  OrderId    INT           NOT NULL PRIMARY KEY,
  Amount     DECIMAL(10,2) NOT NULL,
  OrderDate  DATETIME2(0)  NOT NULL
);

INSERT INTO dbo.Orders (OrderId, Amount, OrderDate) VALUES
  (1, 100, '2024-02-29 23:59:59'),
  (2, 250, '2024-03-01 00:00:00'),
  (3, 300, '2024-03-15 10:30:00'),
  (4, 150, '2024-03-31 23:59:59'),
  (5, 400, '2024-04-01 00:00:00');

-- ============================================
-- SOLUTION: the toolbox (fixed dates so output is repeatable)
-- ============================================

SELECT DATEADD(DAY, 10, CAST('2024-03-15' AS DATE))        AS Plus10Days,      -- 2024-03-25
       DATEADD(MONTH, 1, CAST('2024-01-31' AS DATE))       AS Plus1Month,      -- 2024-02-29 (clamped to month end)
       DATEDIFF(DAY, '2024-03-01', '2024-03-15')           AS DaysBetween,     -- 14
       DATEDIFF(YEAR, '2023-12-31', '2024-01-01')          AS YearBoundaries,  -- 1 (only 1 day apart!)
       EOMONTH('2024-02-10')                               AS EndOfFeb,        -- 2024-02-29
       DATEADD(DAY, 1, EOMONTH('2024-02-10', -1))          AS FirstOfFeb,      -- 2024-02-01
       FORMAT(CAST('2024-03-15' AS DATE), 'dd-MMM-yyyy')   AS Display;         -- 15-Mar-2024

-- ============================================
-- SARGable filter: all of March 2024 (half-open range)
-- ============================================

SELECT OrderId, Amount, OrderDate
FROM dbo.Orders
WHERE OrderDate >= '2024-03-01'
  AND OrderDate <  '2024-04-01'
ORDER BY OrderId;

-- OrderId | Amount | OrderDate
-- 2       | 250.00 | 2024-03-01 00:00:00
-- 3       | 300.00 | 2024-03-15 10:30:00
-- 4       | 150.00 | 2024-03-31 23:59:59

-- Note: DATEADD/DATEDIFF/EOMONTH results and the March filter were derived by an
-- equivalent query on SQLite (date() modifiers; julianday difference = 14).
-- FORMAT and the DATEDIFF-year behaviour are NOT executed on any engine here;
-- they follow Microsoft docs. Not executed on SQL Server.
```

---

## 🔍 Why This Works (3 lines max)
A half-open range (`>= start AND < next_start`) is correct for DATE, DATETIME and DATETIME2 alike and lets the optimizer seek an index on OrderDate. `DATEDIFF(YEAR, ...)` simply subtracts the year numbers (2024 - 2023), so use DAY/MONTH diffs or compare dates for real elapsed time and ages.
हिंदी: Range हमेशा `>= start AND < next_start` लिखो। DATEDIFF(year) सिर्फ साल की संख्या घटाता है।

---

## ⚡ Alternative Solution

```sql
-- Same March filter using EOMONTH (fine for DATE columns, WRONG for DATETIME with time parts)
SELECT OrderId FROM dbo.Orders
WHERE CAST(OrderDate AS DATE) BETWEEN '2024-03-01' AND EOMONTH('2024-03-01');
-- CAST(col AS DATE) on a column is OK in modern SQL Server (it is SARGable for DATETIME
-- columns) but is not a pattern to rely on for other conversions.

-- Real age in years (correct):
DECLARE @dob DATE = '1990-06-15', @today DATE = '2024-03-15';
SELECT DATEDIFF(YEAR, @dob, @today)
       - CASE WHEN DATEADD(YEAR, DATEDIFF(YEAR, @dob, @today), @dob) > @today THEN 1 ELSE 0 END AS Age;  -- 33
```

---

## ⚠️ Common Mistake

```sql
-- ❌ Wrong: wrapping the column in a function -> index scan
WHERE YEAR(OrderDate) = 2024 AND MONTH(OrderDate) = 3
-- ✅ WHERE OrderDate >= '2024-03-01' AND OrderDate < '2024-04-01'

-- ❌ Wrong: BETWEEN '2024-03-01' AND '2024-03-31' on a DATETIME/DATETIME2 column
-- misses everything on 2024-03-31 after 00:00:00 (row 4 above, 23:59:59).

-- ❌ Wrong: ambiguous string literals ('03/04/2024') depend on SET DATEFORMAT/language.
-- ✅ Use 'YYYYMMDD' or ISO 'YYYY-MM-DDThh:mm:ss' (for DATETIME prefer 'YYYYMMDD').

-- ❌ Wrong: FORMAT() on millions of rows - CLR-based and slow; format in the app or use CONVERT.
-- ❌ Wrong: GETDATE() when you need UTC (Azure SQL) -> use SYSUTCDATETIME() / SYSDATETIMEOFFSET().
```

---

## 🎯 Interview Tip (1 line)
Say: "I store timestamps as DATETIME2 in UTC (or DATETIMEOFFSET), filter with half-open ranges so indexes can seek, avoid FORMAT in hot paths, and remember DATEDIFF counts boundaries. In Azure SQL the server clock is UTC, so GETDATE() isn't local time."

---

## 🔗 Related Questions
→ Q023 (DATE, DATETIME, DATETIME2, DATETIMEOFFSET) | Q110 (SARGable predicates) | Q054 (Date-range overlap queries) | Q055 (Consecutive login days) | Q143 (Avoiding implicit conversions)
