---

# Q179. CTE vs Temp Table vs Table Variable
# Category: Interview Classics
# Difficulty: ⭐⭐ Medium
# DB: SQL Server (PostgreSQL: CTEs may be materialized, temp tables exist, no table variables; MySQL 8.0 has CTEs and temporary tables, no table variables)

---

## ❓ Question
You need the paid-spend per customer and then several follow-up steps on that result. When do you use a CTE, a `#temp` table, or a `@table` variable in SQL Server, and what are the real differences in storage, statistics, scope and performance?

---

## 💡 Quick Concept (2 lines only)
A CTE is just a named subquery for one statement: nothing is stored, and a CTE referenced twice may be computed twice. `#temp` tables live in tempdb with statistics, indexes and session scope; `@table` variables also use tempdb, have no column statistics (only a fixed or deferred row estimate), and are scoped to the batch.
हिंदी: CTE = सिर्फ एक statement के लिए नाम, store नहीं होता। #temp = tempdb में असली table, statistics के साथ। @table = छोटा, statistics नहीं।

---

## ✅ Answer / Solution

```sql
-- ============================================
-- SETUP
-- ============================================
CREATE TABLE dbo.Orders (
  OrderId    INT PRIMARY KEY,
  CustomerId INT NOT NULL,
  Amount     DECIMAL(10,2) NOT NULL,
  Status     VARCHAR(20) NOT NULL
);
INSERT INTO dbo.Orders VALUES
  (1, 1, 500, 'Paid'), (2, 1, 700, 'Paid'), (3, 2, 300, 'Paid'),
  (4, 2, 200, 'Cancelled'), (5, 3, 900, 'Paid'), (6, 3, 100, 'Paid'), (7, 1, 50, 'Paid');

-- ============================================
-- 1) CTE : one statement, readable, no storage
-- ============================================
WITH Spend AS (
  SELECT CustomerId, SUM(Amount) AS Total, COUNT(*) AS Cnt
  FROM dbo.Orders WHERE Status = 'Paid' GROUP BY CustomerId
)
SELECT CustomerId, Total, Cnt FROM Spend WHERE Total >= 1000 ORDER BY CustomerId;

-- Result derived from equivalent query on SQLite 3; not executed on SQL Server
-- CustomerId | Total  | Cnt
-- 1          | 1250.00| 3
-- 3          | 1000.00| 2

-- ============================================
-- 2) #TEMP TABLE : reuse across statements, can index, has statistics
-- ============================================
SELECT CustomerId, SUM(Amount) AS Total
INTO #Spend
FROM dbo.Orders WHERE Status = 'Paid' GROUP BY CustomerId;

CREATE CLUSTERED INDEX IX_Spend ON #Spend (CustomerId);

SELECT CustomerId, Total FROM #Spend ORDER BY CustomerId;
-- CustomerId | Total
-- 1          | 1250.00
-- 2          | 300.00
-- 3          | 1000.00
-- (same aggregate, checked on SQLite 3)

DROP TABLE #Spend;

-- ============================================
-- 3) TABLE VARIABLE : tiny sets, batch scope, survives ROLLBACK of the outer transaction
-- ============================================
DECLARE @Spend TABLE (CustomerId INT PRIMARY KEY, Total DECIMAL(12,2));
INSERT INTO @Spend
SELECT CustomerId, SUM(Amount) FROM dbo.Orders WHERE Status = 'Paid' GROUP BY CustomerId;
SELECT COUNT(*) AS Customers FROM @Spend;      -- 3
```

```sql
-- Quick comparison (per Microsoft docs and widely documented behaviour)
-- Feature            | CTE              | #temp table        | @table variable
-- Stored             | no               | tempdb             | tempdb
-- Statistics         | n/a (base tables)| yes, auto-updated  | no column stats (deferred compilation helps on 2019+, compat 150)
-- Indexes            | n/a              | any                | only PK/UNIQUE inline (and inline index syntax on 2014+)
-- Scope              | one statement    | session (child procs can see it) | batch / procedure
-- Rolled back by tx  | n/a              | yes                | no
-- Reuse in same batch| re-evaluated     | read many times    | read many times
```

---

## 🔍 Why This Works (3 lines max)
A CTE is inlined into the outer query, so the optimizer plans everything together and each reference may re-run the logic. A temp table is a real object with statistics, so later joins get good estimates and indexes help. Table variables skip statistics and recompilation, which is cheap for a few rows and harmful for thousands.
हिंदी: CTE inline होता है, हर reference पर दोबारा चल सकता है। #temp में statistics, इसलिए बड़े data पर बेहतर plan। @table छोटे data के लिए।

---

## ⚡ Alternative Solution

```sql
-- Recursive logic: only a CTE can be recursive in a single statement
WITH Numbers AS (
  SELECT 1 AS n
  UNION ALL
  SELECT n + 1 FROM Numbers WHERE n < 5
)
SELECT n FROM Numbers;      -- 1,2,3,4,5

-- Pass a set into a procedure: use a table-valued parameter (user-defined table type), not #temp
-- CREATE TYPE dbo.IdList AS TABLE (Id INT PRIMARY KEY);   -- see Q076, Q101
-- Memory-optimized table variables exist for hot paths (Q155).
```

---

## ⚠️ Common Mistake

```sql
-- ❌ Wrong: assuming a CTE is materialized once. If Spend is referenced 3 times, the aggregate
--    can run 3 times. Put a big aggregate in #temp if you use it many times.
-- ❌ Wrong: loading 500k rows into a table variable and joining it: old estimate is 1 row, so the
--    optimizer picks nested loops. Use #temp (or compat level 150+ for deferred compilation).
-- ❌ Wrong: expecting a table variable to roll back with the transaction; it does not.
-- ❌ Wrong: ending the statement before a CTE: the previous statement needs a ';' before WITH.
```

---

## 🎯 Interview Tip (5+ YOE level)
Say: "CTE for readability and recursion, #temp when the intermediate result is large or reused, because statistics and indexes pay off, and table variables for small sets or when I need data to survive a rollback, such as audit logging. I decide by row count and reuse, then confirm from the plan." Mention that #temp creation in procedures can cause recompiles, and that temp object name caching reduces tempdb contention.

---

## 🔗 Related Questions
→ Q016 (temp tables vs table variables vs CTEs) | Q042 (CTE basics) | Q043 (recursive CTE) | Q146 (table variables vs temp tables for performance) | Q149 (tempdb contention)
