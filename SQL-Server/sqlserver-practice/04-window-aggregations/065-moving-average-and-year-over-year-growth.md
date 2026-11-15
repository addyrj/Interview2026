# Q065. Moving Average and Year-over-Year Growth
# Category: WINDOW FUNCTIONS + AGGREGATIONS
# Difficulty: ⭐⭐⭐ Hard
# DB: SQL Server (2012+) — same window syntax in MySQL 8 and PostgreSQL

---

## ❓ Question
`QuarterlyRevenue` has 8 quarters. Return a 3-quarter moving average (fewer rows at the start are fine, but show how many rows were averaged) and the year-over-year % growth versus the same quarter of the previous year.

---

## 💡 Quick Concept (2 lines only)
Moving average = AVG(...) OVER (ORDER BY ... ROWS BETWEEN 2 PRECEDING AND CURRENT ROW). YoY growth = (current - LAG(value, 4)) / LAG(value, 4) for quarterly data (LAG 12 for monthly).
हिंदी: Moving average के लिए ROWS BETWEEN 2 PRECEDING AND CURRENT ROW। YoY के लिए quarterly data में LAG(value, 4)।

---

## ✅ Answer / Solution

```sql
-- ============================================
-- SETUP
-- ============================================
CREATE TABLE QuarterlyRevenue (
    Yr      INT NOT NULL,
    Qtr     INT NOT NULL CHECK (Qtr BETWEEN 1 AND 4),
    Revenue INT NOT NULL,
    CONSTRAINT PK_QuarterlyRevenue PRIMARY KEY (Yr, Qtr)
);

INSERT INTO QuarterlyRevenue (Yr, Qtr, Revenue) VALUES
 (2023, 1, 100), (2023, 2, 120), (2023, 3,  90), (2023, 4, 150),
 (2024, 1, 110), (2024, 2, 150), (2024, 3,  99), (2024, 4, 180);

-- ============================================
-- SOLUTION
-- ============================================
SELECT
    Yr, Qtr, Revenue,
    CAST(AVG(Revenue * 1.0) OVER (ORDER BY Yr, Qtr
                                  ROWS BETWEEN 2 PRECEDING AND CURRENT ROW) AS DECIMAL(10,2)) AS MovingAvg3Q,
    COUNT(*) OVER (ORDER BY Yr, Qtr
                   ROWS BETWEEN 2 PRECEDING AND CURRENT ROW)                                   AS RowsInWindow,
    LAG(Revenue, 4) OVER (ORDER BY Yr, Qtr)                                                    AS SameQtrLastYear,
    CAST(100.0 * (Revenue - LAG(Revenue, 4) OVER (ORDER BY Yr, Qtr))
         / NULLIF(LAG(Revenue, 4) OVER (ORDER BY Yr, Qtr), 0) AS DECIMAL(6,1))                 AS YoYPct
FROM QuarterlyRevenue
ORDER BY Yr, Qtr;

-- EXPECTED OUTPUT (result derived from equivalent query on PostgreSQL (PGlite); not executed on SQL Server):
-- Yr   | Qtr | Revenue | MovingAvg3Q | RowsInWindow | SameQtrLastYear | YoYPct
-- 2023 | 1   | 100     | 100.00      | 1            | NULL            | NULL
-- 2023 | 2   | 120     | 110.00      | 2            | NULL            | NULL
-- 2023 | 3   |  90     | 103.33      | 3            | NULL            | NULL
-- 2023 | 4   | 150     | 120.00      | 3            | NULL            | NULL
-- 2024 | 1   | 110     | 116.67      | 3            | 100             | 10.0
-- 2024 | 2   | 150     | 136.67      | 3            | 120             | 25.0
-- 2024 | 3   |  99     | 119.67      | 3            | 90              | 10.0
-- 2024 | 4   | 180     | 143.00      | 3            | 150             | 20.0
```

---

## 🔍 Why This Works (3 lines max)
The ROWS frame slides over the current row and the two before it, so the average uses up to three quarters; COUNT over the same frame exposes the partial windows at the start. LAG(Revenue, 4) jumps four quarterly rows back, which is the same quarter last year as long as the series has no missing quarters. Multiplying by 1.0 forces decimal math so AVG and the % are not truncated as integers.
हिंदी: ROWS frame = मौजूदा row + पिछली 2 rows। LAG(.., 4) = पिछले साल की वही quarter। 1.0 से गुणा करो वरना integer division।

---

## ⚡ Alternative Solution

```sql
-- Self-join on (Yr - 1, Qtr): robust to missing quarters because it matches on calendar keys, not row position
SELECT c.Yr, c.Qtr, c.Revenue, p.Revenue AS SameQtrLastYear,
       CAST(100.0 * (c.Revenue - p.Revenue) / NULLIF(p.Revenue, 0) AS DECIMAL(6,1)) AS YoYPct
FROM QuarterlyRevenue AS c
LEFT JOIN QuarterlyRevenue AS p ON p.Yr = c.Yr - 1 AND p.Qtr = c.Qtr
ORDER BY c.Yr, c.Qtr;
-- 2024 rows give 100/120/90/150 and 10.0/25.0/10.0/20.0, identical to LAG(,4); 2023 rows are NULL (hand-checked).

-- Strict "only when 3 full rows exist": wrap with CASE WHEN COUNT(*) OVER (same frame) = 3 THEN AVG(...) END
```

---

## ⚠️ Common Mistake

```sql
-- ❌ AVG(Revenue) on an INT column: 103.33 becomes 103 (integer average)
AVG(Revenue) OVER (ORDER BY Yr, Qtr ROWS BETWEEN 2 PRECEDING AND CURRENT ROW)

-- ❌ Default frame instead of ROWS: with ORDER BY only, AVG becomes a running average from the first row, not a 3-row moving average
AVG(Revenue * 1.0) OVER (ORDER BY Yr, Qtr)

-- ❌ LAG(Revenue, 4) when a quarter is missing -> compares against the wrong period (fix: join on Yr-1)
-- ❌ ORDER BY Qtr, Yr or ORDER BY Qtr alone -> windows jump across years
```

---

## 🎯 Interview Tip (1 line)
Say: "Moving averages need an explicit ROWS frame; I expose the window row count so partial windows are visible, and for YoY I either guarantee a gap-free calendar with LAG(n) or join on the prior-year key, which also survives missing periods."

---

## 🔗 Related Questions
→ Q057 (LAG and LEAD) | Q058 (SUM/AVG OVER with frames) | Q048 (Running totals) | Q049 (Gaps and islands)
