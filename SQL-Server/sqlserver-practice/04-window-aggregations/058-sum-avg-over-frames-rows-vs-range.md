# Q058. SUM/AVG OVER with Frames (ROWS vs RANGE)
# Category: WINDOW FUNCTIONS + AGGREGATIONS
# Difficulty: ⭐⭐⭐ Hard
# DB: SQL Server (2012+) — PostgreSQL/MySQL 8 share the default RANGE behaviour; PostgreSQL additionally allows RANGE with numeric offsets and GROUPS

---

## ❓ Question
`DailySales` has two sales on 2024-05-02. Compute a running total using `SUM(Amount) OVER (ORDER BY SaleDate)` and explain why the two 2024-05-02 rows show the same total. Then produce a true row-by-row running total and a 2-row moving sum.

---

## 💡 Quick Concept (2 lines only)
When OVER has ORDER BY but no frame, the default is RANGE BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW, which includes all peer rows (same ORDER BY value). ROWS counts physical rows, so it gives a true row-by-row running total.
हिंदी: Frame न दो तो default RANGE होता है — same date वाली सारी rows एक साथ जुड़ती हैं। Row-by-row total के लिए ROWS लिखो।

---

## ✅ Answer / Solution

```sql
-- ============================================
-- SETUP
-- ============================================
CREATE TABLE DailySales (
    SaleId   INT IDENTITY(1,1) PRIMARY KEY,
    SaleDate DATE          NOT NULL,
    Amount   DECIMAL(10,2) NOT NULL
);

SET IDENTITY_INSERT DailySales ON;
INSERT INTO DailySales (SaleId, SaleDate, Amount) VALUES
 (1, '2024-05-01', 100), (2, '2024-05-02', 200), (3, '2024-05-02', 50),
 (4, '2024-05-03', 300), (5, '2024-05-04', 150);
SET IDENTITY_INSERT DailySales OFF;

-- ============================================
-- SOLUTION
-- ============================================
SELECT
    SaleId, SaleDate, Amount,
    SUM(Amount) OVER (ORDER BY SaleDate)                                  AS DefaultRangeTotal,
    SUM(Amount) OVER (ORDER BY SaleDate, SaleId
                      ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW)   AS RowsRunningTotal,
    SUM(Amount) OVER (ORDER BY SaleDate, SaleId
                      ROWS BETWEEN 1 PRECEDING AND CURRENT ROW)           AS Last2RowsSum
FROM DailySales
ORDER BY SaleId;

-- EXPECTED OUTPUT (running totals derived from equivalent query on PostgreSQL (PGlite); Last2RowsSum hand-checked; not executed on SQL Server):
-- SaleId | SaleDate   | Amount | DefaultRangeTotal | RowsRunningTotal | Last2RowsSum
-- 1      | 2024-05-01 | 100.00 | 100.00            | 100.00           | 100.00
-- 2      | 2024-05-02 | 200.00 | 350.00            | 300.00           | 300.00
-- 3      | 2024-05-02 |  50.00 | 350.00            | 350.00           | 250.00
-- 4      | 2024-05-03 | 300.00 | 650.00            | 650.00           | 350.00
-- 5      | 2024-05-04 | 150.00 | 800.00            | 800.00           | 450.00
-- Rows 2 and 3 are peers (same SaleDate) -> RANGE gives both 350.00.
```

---

## 🔍 Why This Works (3 lines max)
RANGE defines the frame by ORDER BY values, so every row with the same SaleDate is a "peer" and enters the frame together. ROWS defines it by physical position; adding SaleId makes the order unique and therefore deterministic. In SQL Server, RANGE only allows UNBOUNDED/CURRENT ROW bounds, while ROWS allows `n PRECEDING / n FOLLOWING`.
हिंदी: RANGE = value के हिसाब से peers साथ, ROWS = गिनती की rows। Unique column ORDER BY में जोड़ो तो result पक्का रहता है।

---

## ⚡ Alternative Solution

```sql
-- Same row-by-row running total with a correlated subquery (works on any version, O(n^2)):
SELECT d.SaleId, d.Amount,
       (SELECT SUM(x.Amount) FROM DailySales AS x
        WHERE x.SaleDate < d.SaleDate
           OR (x.SaleDate = d.SaleDate AND x.SaleId <= d.SaleId)) AS RunningTotal
FROM DailySales AS d
ORDER BY d.SaleId;
-- Same numbers as RowsRunningTotal above (100, 300, 350, 650, 800).

-- Centered moving window: 1 row either side
-- AVG(Amount) OVER (ORDER BY SaleDate, SaleId ROWS BETWEEN 1 PRECEDING AND 1 FOLLOWING)
```

---

## ⚠️ Common Mistake

```sql
-- ❌ Relying on the default frame and a non-unique ORDER BY, expecting a row-by-row running total
SUM(Amount) OVER (ORDER BY SaleDate)             -- ties share one total (350.00, 350.00)

-- ❌ ROWS with a non-unique ORDER BY: totals for tied rows depend on arbitrary physical order -> not repeatable
SUM(Amount) OVER (ORDER BY SaleDate ROWS UNBOUNDED PRECEDING)

-- ❌ RANGE BETWEEN 1 PRECEDING AND CURRENT ROW -> not supported in SQL Server (only UNBOUNDED / CURRENT ROW)
-- ✅ Use ROWS for n-row windows, and a unique tiebreaker column in ORDER BY
```

---

## 🎯 Interview Tip (1 line)
Say: "I always write the frame explicitly. Default RANGE treats ties as one unit and, in practice, the RANGE frame is executed with an on-disk worktable (spool) whereas ROWS can use a lighter in-memory spool — so ROWS is both the correct and usually the faster choice for running totals. I confirm that in the execution plan rather than assume."

---

## 🔗 Related Questions
→ Q048 (Running totals) | Q057 (LAG and LEAD) | Q059 (FIRST_VALUE, LAST_VALUE and the default frame trap) | Q065 (Moving average and YoY) | Q108 (SET STATISTICS IO and TIME)
