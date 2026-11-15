---

# Q079. Procedure vs Function vs View
# Category: Stored Procedures
# Difficulty: ⭐⭐ Medium
# DB: SQL Server (MySQL: functions/procedures/views similar; PostgreSQL: functions can RETURNS TABLE and do what T-SQL procs + TVFs do)

---

## ❓ Question
When do you use a stored procedure, a user-defined function (scalar / inline TVF) or a view in SQL Server? Show the same "shipped order totals per customer" logic as all three and the key restrictions of each.

---

## 💡 Quick Concept (2 lines only)
View = saved SELECT (no parameters, composable in FROM). Inline TVF = parameterized view (composable, optimizer expands it). Procedure = executable program (DML, transactions, TRY/CATCH, multiple result sets, OUTPUT) but not usable in FROM/WHERE.
हिंदी: View = saved SELECT। Inline TVF = parameter वाला view। Procedure = actions/transactions के लिए, FROM में use नहीं होता।

---

## ✅ Answer / Solution

```sql
-- ============================================
-- SETUP
-- ============================================

CREATE TABLE dbo.Orders (
  OrderId    INT PRIMARY KEY,
  CustomerId INT NOT NULL,
  Status     VARCHAR(20) NOT NULL,
  Amount     DECIMAL(10,2) NOT NULL
);
INSERT INTO dbo.Orders VALUES
  (1,101,'Shipped',250.00),(2,101,'Pending',80.00),(3,102,'Shipped',1200.00),
  (4,103,'Cancelled',45.50),(5,102,'Pending',310.00),(6,104,'Shipped',99.99),(7,101,'Shipped',560.00);
GO

-- ============================================
-- 1) VIEW  (no parameters)
-- ============================================
CREATE OR ALTER VIEW dbo.vw_ShippedTotals
AS
SELECT CustomerId, SUM(Amount) AS Total
FROM dbo.Orders
WHERE Status = 'Shipped'
GROUP BY CustomerId;
GO

-- ============================================
-- 2) INLINE TABLE-VALUED FUNCTION (parameterized, composable)
-- ============================================
CREATE OR ALTER FUNCTION dbo.fn_TotalsByStatus (@Status VARCHAR(20))
RETURNS TABLE
AS
RETURN
(
    SELECT CustomerId, SUM(Amount) AS Total
    FROM dbo.Orders
    WHERE Status = @Status
    GROUP BY CustomerId
);
GO

-- ============================================
-- 3) PROCEDURE (can write data, transaction, OUTPUT, several result sets)
-- ============================================
CREATE OR ALTER PROCEDURE dbo.usp_TotalsByStatus
    @Status VARCHAR(20)
AS
BEGIN
    SET NOCOUNT ON;
    SELECT CustomerId, SUM(Amount) AS Total
    FROM dbo.Orders
    WHERE Status = @Status
    GROUP BY CustomerId;
END;
GO

SELECT CustomerId, Total FROM dbo.vw_ShippedTotals ORDER BY CustomerId;
SELECT CustomerId, Total FROM dbo.fn_TotalsByStatus('Shipped') ORDER BY CustomerId;
EXEC dbo.usp_TotalsByStatus @Status = 'Shipped';
-- All three return (result derived from equivalent GROUP BY query on SQLite; not executed on SQL Server):
-- CustomerId | Total
-- 101        | 810.00
-- 102        | 1200.00
-- 104        | 99.99

-- Composability test: only view and TVF can be joined/filtered directly
SELECT c.CustomerId, c.Total FROM dbo.fn_TotalsByStatus('Shipped') AS c WHERE c.Total > 500;  -- OK
-- SELECT * FROM dbo.usp_TotalsByStatus 'Shipped';   -- NOT valid: procedures cannot be used in FROM
```

---

## 🔍 Why This Works (3 lines max)
Views and inline TVFs are expanded into the calling query, so the optimizer can push predicates and use indexes across them. Procedures are separate execution units with their own plan, which is why they can do DML, transactions and error handling but cannot be composed in a SELECT.
हिंदी: View/Inline TVF query में expand होते हैं (optimizer-friendly)। Procedure अलग program है — DML, transaction और error handling के लिए।

---

## ⚡ Alternative Solution

```sql
-- Scalar UDF: returns one value. Historically a performance trap (row-by-row, blocks parallelism);
-- SQL Server 2019 can inline eligible scalar UDFs (compat level 150). Prefer an inline TVF + CROSS APPLY:
SELECT c.CustomerId, t.Total
FROM (VALUES (101), (102)) AS c (CustomerId)
CROSS APPLY (SELECT SUM(Amount) AS Total FROM dbo.Orders o
             WHERE o.CustomerId = c.CustomerId AND o.Status = 'Shipped') AS t;
-- Quick rule: data modification or workflow -> procedure; reusable read logic -> inline TVF / view;
-- multi-statement TVF only when you truly need procedural logic (estimates are fixed/poor; see Q090).
```

---

## ⚠️ Common Mistake

```sql
-- ❌ Putting a scalar UDF in a WHERE/SELECT over millions of rows without checking it is inlineable.
-- ❌ Functions cannot do side effects: no INSERT/UPDATE/DELETE on permanent tables, no TRY...CATCH,
--    no dynamic SQL (EXEC), no non-deterministic temp-table creation. Trying this = compile error.
-- ❌ Views with ORDER BY: not allowed without TOP/OFFSET and the order is NOT guaranteed anyway.
-- ❌ SELECT * in a view: column list is frozen at creation; new table columns do not appear until
--    sp_refreshview / ALTER VIEW.
-- ❌ Using a procedure when the caller just needs a filterable rowset (forces INSERT...EXEC -- see Q077).
```

---

## 🎯 Interview Tip (1 line)
Say: "Actions and transactions go in procedures; reusable read logic goes in inline TVFs or views because the optimizer can see through them; I avoid scalar and multi-statement TVFs on large sets unless they are inlineable or small." Quote the three-way contrast: side effects, composability, parameters.

---

## 🔗 Related Questions
→ Q068 (What is a stored procedure) | Q077 (INSERT...EXEC) | Q088 (Scalar UDF cost) | Q089 (Inline TVF) | Q091 (Views)
