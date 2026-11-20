---

# Q178. Stored Procedure vs Function
# Category: Interview Classics
# Difficulty: ⭐⭐ Medium
# DB: SQL Server (PostgreSQL treats both as FUNCTION/PROCEDURE with different rules; MySQL has both but fewer restrictions on side effects inside procedures)

---

## ❓ Question
What is the difference between a stored procedure and a user-defined function in SQL Server? When do you pick which, and why can a scalar function make a query slow?

---

## 💡 Quick Concept (2 lines only)
A procedure is a callable unit that can run any statements (DML, transactions, TRY/CATCH, dynamic SQL), return result sets and OUTPUT params, and is invoked with EXEC. A function must return a value (scalar or table), is used inside queries, and cannot change database state or use transactions or TRY/CATCH.
हिंदी: Procedure = पूरा काम (DML, transaction, कई result sets), EXEC से चलता है। Function = value लौटाता है, query के अंदर use होता है, data बदल नहीं सकता।

---

## ✅ Answer / Solution

```sql
-- ============================================
-- SETUP
-- ============================================
CREATE TABLE dbo.OrderLines (
  OrderId   INT NOT NULL,
  LineNo    INT NOT NULL,
  Qty       INT NOT NULL,
  UnitPrice DECIMAL(10,2) NOT NULL,
  PRIMARY KEY (OrderId, LineNo)
);
INSERT INTO dbo.OrderLines VALUES
  (1, 1, 2, 250.00), (1, 2, 1, 100.00),
  (2, 1, 3,  50.00),
  (3, 1, 1, 900.00), (3, 2, 2,  25.00);
GO

-- ============================================
-- PROCEDURE: does work, returns a result set + OUTPUT parameter
-- ============================================
CREATE PROCEDURE dbo.usp_GetOrderSummary
  @OrderId INT,
  @Total   DECIMAL(12,2) OUTPUT
AS
BEGIN
  SET NOCOUNT ON;
  SELECT @Total = SUM(Qty * UnitPrice) FROM dbo.OrderLines WHERE OrderId = @OrderId;
  SELECT LineNo, Qty, UnitPrice, Qty * UnitPrice AS LineTotal
  FROM dbo.OrderLines WHERE OrderId = @OrderId ORDER BY LineNo;
END;
GO

-- ============================================
-- INLINE TABLE-VALUED FUNCTION: composable, used in FROM / APPLY
-- ============================================
CREATE FUNCTION dbo.fn_OrderTotals ()
RETURNS TABLE
AS
RETURN (
  SELECT OrderId, SUM(Qty * UnitPrice) AS Total
  FROM dbo.OrderLines
  GROUP BY OrderId
);
GO

-- SCALAR FUNCTION: returns one value (see the performance warning below)
CREATE FUNCTION dbo.fn_LineTotal (@Qty INT, @UnitPrice DECIMAL(10,2))
RETURNS DECIMAL(12,2)
AS
BEGIN
  RETURN @Qty * @UnitPrice;
END;
GO

-- ============================================
-- USAGE
-- ============================================
DECLARE @T DECIMAL(12,2);
EXEC dbo.usp_GetOrderSummary @OrderId = 1, @Total = @T OUTPUT;
SELECT @T AS Total;

SELECT o.OrderId, o.Total FROM dbo.fn_OrderTotals() AS o WHERE o.Total > 300 ORDER BY o.OrderId;

-- Result derived by hand-checked arithmetic and an equivalent query on SQLite 3; not executed on SQL Server
-- usp_GetOrderSummary(1): Total = 600.00 ; lines: (1, 2, 250.00, 500.00), (2, 1, 100.00, 100.00)
-- fn_OrderTotals() with Total > 300:
-- OrderId | Total
-- 1       | 600.00
-- 3       | 950.00      (order 2 = 150.00 is filtered out)
```

```javascript
// Node.js (mssql): procedure vs function call styles
const r = await pool.request().input('OrderId', sql.Int, 1)
  .output('Total', sql.Decimal(12, 2)).execute('dbo.usp_GetOrderSummary');   // r.recordset, r.output.Total
const t = await pool.request().query('SELECT OrderId, Total FROM dbo.fn_OrderTotals() WHERE Total > 300');
```

---

## 🔍 Why This Works (3 lines max)
A function must be deterministic enough to sit inside a SELECT, so SQL Server forbids side effects (no INSERT/UPDATE on real tables, no transactions, no TRY/CATCH). Inline table-valued functions are expanded into the calling query like a parameterized view, so the optimizer sees through them. Procedures get their own cached plan and are the right place for transactions and orchestration.
हिंदी: Function में side-effect मना है, इसलिए query में बैठ सकता है। Inline TVF optimizer को दिखता है। Procedure = orchestration + transaction।

---

## ⚡ Alternative Solution

```sql
-- Prefer an inline TVF or plain expression to a scalar UDF in hot queries:
SELECT OrderId, LineNo, Qty * UnitPrice AS LineTotal FROM dbo.OrderLines;      -- no function call
-- Inline TVF for reusable logic:
SELECT l.OrderId, t.Total
FROM dbo.OrderLines AS l
CROSS APPLY (SELECT SUM(Qty * UnitPrice) AS Total FROM dbo.OrderLines WHERE OrderId = l.OrderId) AS t;
-- SQL Server 2019+ can inline some scalar UDFs automatically (Scalar UDF inlining, compat level 150),
-- but only when the function meets restrictions; do not rely on it blindly.
```

---

## ⚠️ Common Mistake

```sql
-- ❌ Wrong: scalar UDF in WHERE or SELECT over millions of rows (pre-2019 or non-inlineable):
SELECT OrderId FROM dbo.OrderLines WHERE dbo.fn_LineTotal(Qty, UnitPrice) > 100;
--   runs row by row, blocks parallelism, and hides cost in plans/statistics.
-- ❌ Wrong: multi-statement TVF for simple logic: the optimizer guesses a fixed row estimate
--    (see Q090). Use an inline TVF.
-- ❌ Wrong: trying to call a procedure inside a SELECT, or to INSERT/UPDATE inside a function.
-- ❌ Wrong: using a function when you need transactions or error handling (TRY/CATCH).
```

---

## 🎯 Interview Tip (5+ YOE level)
Say: "Procedures for operations and API entry points: transactions, permissions via EXECUTE, plan reuse, and a stable contract for Node. Inline table-valued functions for reusable query logic because the optimizer inlines them. I avoid scalar UDFs on large sets unless they are inlineable and I have checked the plan." Add the comparison: a view cannot take parameters, an inline TVF is a parameterized view.

---

## 🔗 Related Questions
→ Q079 (procedure vs function vs view) | Q088 (scalar UDF performance cost) | Q089 (inline table-valued functions) | Q090 (multi-statement TVFs) | Q068 (what is a stored procedure)
