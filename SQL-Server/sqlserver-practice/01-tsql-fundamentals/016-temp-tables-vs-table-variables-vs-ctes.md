---

# Q016. Temp Tables (#temp) vs Table Variables (@t) vs CTEs
# Category: T-SQL FUNDAMENTALS
# Difficulty: ⭐⭐ Medium
# DB: SQL Server (MySQL: CREATE TEMPORARY TABLE, no table variables; PostgreSQL: CREATE TEMP TABLE, CTEs can be MATERIALIZED)

---

## ❓ Question
Find customers whose total order value exceeds 1000, and reuse that intermediate result three ways: a CTE, a `#temp` table, and a `@table` variable. When do you pick each one?

---

## 💡 Quick Concept (2 lines only)
A CTE is just a named query inlined into one statement (no storage); `#temp` is a real tempdb table with statistics and indexes, visible for the session; `@t` is a tempdb-backed variable scoped to the batch, with no column statistics.
हिंदी: CTE = सिर्फ एक statement का नाम; #temp = tempdb की असली table (statistics + index); @t = batch-scope variable, statistics नहीं।

---

## ✅ Answer / Solution

```sql
-- ============================================
-- SETUP
-- ============================================

CREATE TABLE Orders (
  OrderId    INT PRIMARY KEY,
  CustomerId INT NOT NULL,
  Amount     DECIMAL(10,2) NOT NULL
);

INSERT INTO Orders (OrderId, CustomerId, Amount) VALUES
  (1, 101,  500.00),
  (2, 101, 1200.00),
  (3, 102,  300.00),
  (4, 103,  750.00),
  (5, 104,   90.00),
  (6, 102, 2000.00),
  (7, 101,  640.00);
GO

-- ============================================
-- 1) CTE - one statement only, re-evaluated per reference
-- ============================================

WITH CustomerTotals AS (
    SELECT CustomerId, SUM(Amount) AS Total, COUNT(*) AS Cnt
    FROM Orders
    GROUP BY CustomerId
)
SELECT CustomerId, Total, Cnt
FROM CustomerTotals
WHERE Total > 1000
ORDER BY Total DESC;

-- ============================================
-- 2) #temp table - materialized once, can be indexed, reusable in the session
-- ============================================

SELECT CustomerId, SUM(Amount) AS Total, COUNT(*) AS Cnt
INTO #CustomerTotals
FROM Orders
GROUP BY CustomerId;

CREATE INDEX IX_CustomerTotals_Total ON #CustomerTotals (Total);

SELECT CustomerId, Total, Cnt FROM #CustomerTotals WHERE Total > 1000 ORDER BY Total DESC;
SELECT COUNT(*) AS BigSpenders FROM #CustomerTotals WHERE Total > 1000;  -- second use: no recompute

DROP TABLE #CustomerTotals;   -- optional; auto-dropped when the session ends

-- ============================================
-- 3) @table variable - batch scoped, no statistics, not affected by ROLLBACK
-- ============================================

DECLARE @CustomerTotals TABLE (
    CustomerId INT PRIMARY KEY,
    Total      DECIMAL(12,2),
    Cnt        INT
);

INSERT INTO @CustomerTotals (CustomerId, Total, Cnt)
SELECT CustomerId, SUM(Amount), COUNT(*) FROM Orders GROUP BY CustomerId;

SELECT CustomerId, Total, Cnt FROM @CustomerTotals WHERE Total > 1000 ORDER BY Total DESC;

-- Output (identical for all three):
-- CustomerId | Total   | Cnt
-- 101        | 2340.00 | 3
-- 102        | 2300.00 | 2

-- Result derived from an equivalent GROUP BY query on SQLite 3.49 (SQLite prints 2340.0 for
-- REAL; T-SQL shows DECIMAL(10,2) sums as 2340.00); not executed on SQL Server.
```

---

## 🔍 Why This Works (3 lines max)
All three hold the same aggregate; they differ in lifetime and optimizer support. The CTE is expanded into the outer query each time it is referenced, `#temp` is materialized once and gets real statistics so the optimizer estimates well, and `@t` is cheap for tiny row counts but historically estimated as 1 row (deferred compilation in 2019+ / compat level 150 improves this).
हिंदी: CTE हर reference पर दोबारा चलता है; #temp एक बार बनकर stats के साथ reuse होता है; @t छोटे data के लिए ठीक है पर stats नहीं (2019+ में थोड़ा बेहतर)।

---

## ⚡ Alternative Solution

```sql
-- Pick by rule of thumb:
--  * CTE            : readability, recursion, used once
--  * #temp          : > ~few thousand rows, reused several times, needs an index/stats, big joins
--  * @table variable: tiny sets, inside functions (functions cannot use #temp), no recompiles wanted
--  * Global ##temp  : visible to every session until the last user disconnects (rarely wanted)

-- A table variable keeps its rows after ROLLBACK; a #temp table does not:
DECLARE @Audit TABLE (Msg VARCHAR(50));
CREATE TABLE #Audit (Msg VARCHAR(50));
BEGIN TRAN;
    INSERT INTO @Audit VALUES ('in tran');
    INSERT INTO #Audit VALUES ('in tran');
ROLLBACK;
SELECT (SELECT COUNT(*) FROM @Audit) AS TableVarRows, (SELECT COUNT(*) FROM #Audit) AS TempRows;
-- Expected per Microsoft docs: TableVarRows = 1, TempRows = 0  (not executed on SQL Server)
DROP TABLE #Audit;
```

---

## ⚠️ Common Mistake

```sql
-- ❌ Wrong: using a CTE twice and assuming it runs once
WITH Totals AS (SELECT CustomerId, SUM(Amount) AS Total FROM Orders GROUP BY CustomerId)
SELECT a.CustomerId FROM Totals a JOIN Totals b ON a.Total > b.Total;
-- SQL Server does NOT materialize CTEs: the aggregate may run twice. Use #temp when reused.

-- ❌ Wrong: referencing a CTE in the NEXT statement
WITH Totals AS (SELECT CustomerId FROM Orders)
SELECT * FROM Totals;
SELECT * FROM Totals;   -- Invalid object name 'Totals' (CTE lives for one statement only)

-- ❌ Wrong: big #temp created inside a procedure without a purpose-built index
-- ❌ Wrong: relying on @table variables for 1M rows (poor estimates -> bad join choices)
```

---

## 🎯 Interview Tip (1 line)
Say: "CTE for readability and recursion, #temp when I reuse a large intermediate result or need statistics and indexes, table variable for tiny sets or inside functions. I never assume a CTE is materialized, and I remember a table variable survives ROLLBACK while a #temp table does not."

---

## 🔗 Related Questions
→ Q042 (CTE basics) | Q146 (table variables vs temp tables for performance) | Q149 (tempdb contention) | Q179 (CTE vs temp table vs table variable)
