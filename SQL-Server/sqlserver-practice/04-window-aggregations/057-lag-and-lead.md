# Q057. LAG and LEAD
# Category: WINDOW FUNCTIONS + AGGREGATIONS
# Difficulty: ⭐⭐ Medium
# DB: SQL Server (2012+) — MySQL 8.0+ and PostgreSQL have identical LAG/LEAD syntax

---

## ❓ Question
`MonthlySales` has one row per region per month. For each row show the previous month's revenue, the next month's revenue, the month-over-month change and the % change. Use a default of 0 where there is no earlier row, and make sure the first month of each region does not divide by zero.

---

## 💡 Quick Concept (2 lines only)
LAG(col, offset, default) reads a value from a previous row in the window order; LEAD reads from a following row. Both need ORDER BY in OVER and return NULL (or your default) when the row does not exist.
हिंदी: LAG = पिछली row की value, LEAD = अगली row की value। PARTITION BY से हर region अलग रहता है।

---

## ✅ Answer / Solution

```sql
-- ============================================
-- SETUP
-- ============================================
CREATE TABLE MonthlySales (
    Region     VARCHAR(10)   NOT NULL,
    MonthStart DATE          NOT NULL,
    Revenue    DECIMAL(10,2) NOT NULL,
    CONSTRAINT PK_MonthlySales PRIMARY KEY (Region, MonthStart)
);

INSERT INTO MonthlySales (Region, MonthStart, Revenue) VALUES
 ('North', '2024-01-01', 1000), ('North', '2024-02-01', 1200),
 ('North', '2024-03-01',  900), ('North', '2024-04-01', 1500),
 ('South', '2024-01-01',  800), ('South', '2024-02-01',  800),
 ('South', '2024-03-01', 1100);

-- ============================================
-- SOLUTION
-- ============================================
SELECT
    Region,
    MonthStart,
    Revenue,
    LAG(Revenue)          OVER (PARTITION BY Region ORDER BY MonthStart) AS PrevRev,
    LEAD(Revenue)         OVER (PARTITION BY Region ORDER BY MonthStart) AS NextRev,
    LAG(Revenue, 2, 0)    OVER (PARTITION BY Region ORDER BY MonthStart) AS Prev2OrZero,
    Revenue - LAG(Revenue) OVER (PARTITION BY Region ORDER BY MonthStart) AS Diff,
    CAST(100.0 * (Revenue - LAG(Revenue) OVER (PARTITION BY Region ORDER BY MonthStart))
         / NULLIF(LAG(Revenue) OVER (PARTITION BY Region ORDER BY MonthStart), 0)
         AS DECIMAL(6,1)) AS PctChange
FROM MonthlySales
ORDER BY Region, MonthStart;

-- EXPECTED OUTPUT (result derived from equivalent query on PostgreSQL (PGlite); not executed on SQL Server):
-- Region | MonthStart | Revenue | PrevRev | NextRev | Prev2OrZero | Diff    | PctChange
-- North  | 2024-01-01 | 1000.00 | NULL    | 1200.00 | 0.00        | NULL    | NULL
-- North  | 2024-02-01 | 1200.00 | 1000.00 |  900.00 | 0.00        |  200.00 |  20.0
-- North  | 2024-03-01 |  900.00 | 1200.00 | 1500.00 | 1000.00     | -300.00 | -25.0
-- North  | 2024-04-01 | 1500.00 |  900.00 | NULL    | 1200.00     |  600.00 |  66.7
-- South  | 2024-01-01 |  800.00 | NULL    |  800.00 | 0.00        | NULL    | NULL
-- South  | 2024-02-01 |  800.00 |  800.00 | 1100.00 | 0.00        |    0.00 |   0.0
-- South  | 2024-03-01 | 1100.00 |  800.00 | NULL    | 800.00      |  300.00 |  37.5
-- (PG printed Prev2OrZero as 0; on SQL Server the column keeps the DECIMAL(10,2) type, so 0.00)
```

---

## 🔍 Why This Works (3 lines max)
The window is "rows of the same Region sorted by MonthStart", so LAG/LEAD just move one (or N) rows inside that ordered list, with no self-join. The first row of each partition has no previous row, so LAG returns NULL — NULLIF(prev, 0) also protects the % calculation from divide-by-zero. The third argument is only used for the missing row, not for a NULL stored in the column.
हिंदी: LAG/LEAD self-join की जगह लेते हैं। Default value सिर्फ तब मिलती है जब row exist ही न करे, NULL data पर नहीं।

---

## ⚡ Alternative Solution

```sql
-- Pre-2012 style (no LAG): correlated CROSS APPLY with TOP 1 — works but is slower and noisier
SELECT s.Region, s.MonthStart, s.Revenue, p.Revenue AS PrevRev
FROM MonthlySales AS s
OUTER APPLY (
    SELECT TOP (1) m.Revenue
    FROM MonthlySales AS m
    WHERE m.Region = s.Region AND m.MonthStart < s.MonthStart
    ORDER BY m.MonthStart DESC
) AS p
ORDER BY s.Region, s.MonthStart;
-- Same PrevRev values as above (OUTER APPLY keeps first-month rows with NULL).
-- Not executed on SQL Server; APPLY has no direct equivalent engine here (PostgreSQL: LEFT JOIN LATERAL).

-- Calendar-gap safe version: LAG works on ROW position, not on calendar months.
-- If a month is missing, LAG returns the month BEFORE the gap. Join to a calendar table to be exact.
```

---

## ⚠️ Common Mistake

```sql
-- ❌ Forgetting PARTITION BY: South's first row "sees" North's last row
SELECT Region, MonthStart, Revenue,
       LAG(Revenue) OVER (ORDER BY Region, MonthStart) AS PrevRev   -- South Jan -> 1500.00 (North Apr!)
FROM MonthlySales;

-- ❌ Omitting ORDER BY inside OVER -> syntax error in T-SQL (LAG/LEAD require ORDER BY)
-- ❌ Using LAG(Revenue, 1, 0) and then dividing by it -> divide-by-zero error; use NULLIF or leave default NULL
-- ❌ Assuming LAG(Revenue, 12) means "same month last year" when months can be missing
```

---

## 🎯 Interview Tip (1 line)
Say: "LAG/LEAD are positional, so I partition by the entity, order by a unique column, and guard the % math with NULLIF. If the series can have gaps I join a calendar/date table first — and for 2022+ I know LAG supports IGNORE NULLS to carry the last non-null value."

---

## 🔗 Related Questions
→ Q056 (ROW_NUMBER, RANK, DENSE_RANK, NTILE) | Q058 (SUM/AVG OVER frames) | Q065 (Moving average and YoY) | Q048 (Running totals) | Q049 (Gaps and islands)
