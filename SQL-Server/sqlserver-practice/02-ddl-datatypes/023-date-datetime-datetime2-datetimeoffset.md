---

# Q023. DATE, DATETIME, DATETIME2, DATETIMEOFFSET
# Category: DDL + DATA TYPES
# Difficulty: ⭐⭐ Medium
# DB: SQL Server (MySQL: DATETIME/TIMESTAMP; PostgreSQL: timestamp / timestamptz)

---

## ❓ Question
Which date/time type should a new table use for order timestamps? Show the DATETIME rounding quirk, the `BETWEEN` end-of-day trap, and how DATETIMEOFFSET handles time zones, with the size and precision of each type.

---

## 💡 Quick Concept (2 lines only)
DATE = date only (3 bytes). DATETIME is legacy: about 3.33 ms accuracy, range from 1753. DATETIME2(n) is the modern replacement (up to 100 ns, range from year 1, 6-8 bytes); DATETIMEOFFSET adds a UTC offset (8-10 bytes).
हिंदी: नया design = DATETIME2 (या DATE जब time नहीं चाहिए)। DATETIME पुराना है और .999 को round कर देता है। Time zone चाहिए तो DATETIMEOFFSET।

---

## ✅ Answer / Solution

```sql
-- ============================================
-- SETUP
-- ============================================

CREATE TABLE Orders (
  OrderId   INT PRIMARY KEY,
  CreatedAt DATETIME2(3) NOT NULL,          -- millisecond precision, 7 bytes
  ShipDate  DATE         NULL,              -- date only
  PaidAt    DATETIMEOFFSET(0) NULL          -- keeps the offset the client used
);

INSERT INTO Orders (OrderId, CreatedAt) VALUES
  (1, '2024-01-01 09:00:00.000'),
  (2, '2024-01-01 23:59:59.500'),
  (3, '2024-01-02 00:00:00.000'),
  (4, '2024-01-02 10:30:00.000');
GO

-- ============================================
-- SOLUTION: all orders of 1 Jan 2024 - use a half-open range
-- ============================================

SELECT OrderId, CreatedAt
FROM Orders
WHERE CreatedAt >= '2024-01-01' AND CreatedAt < '2024-01-02'
ORDER BY OrderId;

-- Output:
-- OrderId | CreatedAt
-- 1       | 2024-01-01 09:00:00.000
-- 2       | 2024-01-01 23:59:59.500

-- Result derived from the equivalent range predicate on SQLite 3.49 (text timestamps); not executed
-- on SQL Server.

-- The tempting but WRONG version loses order 2:
SELECT OrderId FROM Orders
WHERE CreatedAt BETWEEN '2024-01-01' AND '2024-01-01 23:59:59';
-- Output (equivalent query on SQLite):
-- OrderId
-- 1

-- DATETIME rounds to .000 / .003 / .007 increments:
SELECT CAST('2024-01-01 23:59:59.999' AS DATETIME)    AS AsDatetime,
       CAST('2024-01-01 23:59:59.999' AS DATETIME2(3)) AS AsDatetime2;
-- Output per Microsoft docs (not executed here, no equivalent engine):
-- AsDatetime              | AsDatetime2
-- 2024-01-02 00:00:00.000 | 2024-01-01 23:59:59.999

-- Time zones with DATETIMEOFFSET
SELECT SWITCHOFFSET(CAST('2024-03-10 10:00:00 +05:30' AS DATETIMEOFFSET(0)), '+00:00') AS UtcValue;
-- Output per Microsoft docs (not executed): 2024-03-10 04:30:00 +00:00
```

---

## 🔍 Why This Works (3 lines max)
A half-open range (`>= start AND < next day`) catches every instant regardless of precision and keeps the predicate SARGable. `BETWEEN ... 23:59:59` misses fractional seconds, and with DATETIME the end value `23:59:59.999` itself rounds up to the next day. DATETIMEOFFSET stores the instant plus offset, so converting to UTC is lossless.
हिंदी: Half-open range (>= start AND < next day) हमेशा सही रहती है। BETWEEN ... 23:59:59 fractional seconds खो देता है; DATETIME का .999 अगले दिन में round हो जाता है।

---

## ⚡ Alternative Solution

```sql
-- Store UTC in DATETIME2 and convert at the edge (simple, portable)
INSERT INTO Orders (OrderId, CreatedAt) VALUES (5, SYSUTCDATETIME());

-- Convert a stored UTC value to India time for display (2016+):
SELECT CreatedAt AT TIME ZONE 'UTC' AT TIME ZONE 'India Standard Time' AS LocalTime
FROM Orders WHERE OrderId = 5;

-- Date-only filter from a DATETIME2 column: CAST to DATE is SARGable on modern versions
SELECT OrderId FROM Orders WHERE CAST(CreatedAt AS DATE) = '2024-01-01';

-- Sizes: DATE 3 B | DATETIME 8 B | DATETIME2 6-8 B | SMALLDATETIME 4 B | DATETIMEOFFSET 8-10 B
-- GETDATE() returns DATETIME; SYSDATETIME() returns DATETIME2(7); GETUTCDATE() / SYSUTCDATETIME() are UTC.
```

---

## ⚠️ Common Mistake

```sql
-- ❌ Wrong: BETWEEN for dates on a time-bearing column (misses the last second(s) of the day)
SELECT * FROM Orders WHERE CreatedAt BETWEEN '2024-01-01' AND '2024-01-01 23:59:59';

-- ❌ Wrong: wrapping the column in a function in WHERE (non-SARGable on older patterns)
SELECT * FROM Orders WHERE YEAR(CreatedAt) = 2024 AND MONTH(CreatedAt) = 1;
-- ✅ Use: WHERE CreatedAt >= '2024-01-01' AND CreatedAt < '2024-02-01'

-- ❌ Wrong: language-dependent date literals like '01/02/2024' (Jan 2 or Feb 1?)
-- ✅ Use ISO 'YYYYMMDD' or 'YYYY-MM-DDThh:mm:ss' (the dash format 'YYYY-MM-DD' can still be misread
--    by DATETIME under some SET LANGUAGE/DATEFORMAT settings; DATE/DATETIME2 are safe).

-- ❌ Wrong: DATETIME for new tables (3.33 ms accuracy, 8 bytes, range from 1753)
```

---

## 🎯 Interview Tip (1 line)
Say: "New tables: DATETIME2(n) in UTC (or DATETIMEOFFSET when the original offset matters), DATE when time is irrelevant. I query ranges as `>= start AND < next day`, never BETWEEN, and I use ISO literals." Node note: `mssql` returns DATETIME2 as a JS Date interpreted as UTC unless you set `options.useUTC: false`.

---

## 🔗 Related Questions
→ Q007 (date functions) | Q054 (date-range overlap queries) | Q110 (SARGable predicates) | Q030 (temporal tables)
