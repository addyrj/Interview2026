---

# Q077. INSERT...EXEC and Capturing Results
# Category: Stored Procedures
# Difficulty: ⭐⭐⭐ Hard
# DB: SQL Server (MySQL: procedures cannot be SELECTed from; PostgreSQL: use functions RETURNS TABLE and SELECT * FROM fn())

---

## ❓ Question
You have a procedure `dbo.usp_CustomerTotals` that returns a result set. How do you capture that result into a table to filter/join it further? What are the limitations (nesting, column match), and what are cleaner alternatives?

---

## 💡 Quick Concept (2 lines only)
`INSERT INTO #t (cols) EXEC dbo.proc @p = 1;` stores the procedure's result set in a table whose columns match exactly in count and compatible types. A procedure cannot be used in FROM, so INSERT...EXEC (or OUTPUT params, or converting to an inline TVF) is the bridge.
हिंदी: `INSERT INTO #t EXEC proc` से procedure का result table में आ जाता है। Columns की संख्या/type match होनी चाहिए।

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

CREATE OR ALTER PROCEDURE dbo.usp_CustomerTotals
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

-- ============================================
-- SOLUTION
-- ============================================

CREATE TABLE #Totals (CustomerId INT, Total DECIMAL(12,2));

INSERT INTO #Totals (CustomerId, Total)
EXEC dbo.usp_CustomerTotals @Status = 'Shipped';

SELECT CustomerId, Total FROM #Totals WHERE Total > 100 ORDER BY CustomerId;
-- Full #Totals content (derived from equivalent INSERT...SELECT ... GROUP BY on SQLite; not executed on SQL Server):
-- CustomerId | Total
-- 101        | 810.00
-- 102        | 1200.00
-- 104        | 99.99
-- After the Total > 100 filter: rows 101 and 102 only.

DROP TABLE #Totals;
```

---

## 🔍 Why This Works (3 lines max)
The procedure's first result set is streamed into the target table, and from then on it is ordinary data you can filter, join or index. Column positions (not names) are matched, so the target must have the same number of columns with implicitly convertible types.
हिंदी: Result set position के हिसाब से columns में जाता है — इसलिए count और type मिलना ज़रूरी है।

---

## ⚡ Alternative Solution

```sql
-- 1) OUTPUT parameters for scalar results (no table needed) -- see Q069.
-- 2) Convert the logic to an INLINE TABLE-VALUED FUNCTION: composable, usable directly in FROM/APPLY.
CREATE OR ALTER FUNCTION dbo.fn_CustomerTotals (@Status VARCHAR(20))
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
SELECT CustomerId, Total FROM dbo.fn_CustomerTotals('Shipped') WHERE Total > 100;

-- 3) OPENROWSET/OPENQUERY loopback to call a proc in FROM -- avoid: needs ad hoc distributed queries enabled,
--    is a security risk, and is fragile.
-- 4) sp_describe_first_result_set @tsql = N'EXEC dbo.usp_CustomerTotals ''Shipped''' tells you the columns for the table.
```

---

## ⚠️ Common Mistake

```sql
-- ❌ Nesting: an INSERT...EXEC cannot call a procedure that itself does INSERT...EXEC
--    ("INSERT EXEC statement cannot be nested" error, per Microsoft docs).
-- ❌ Column count mismatch: procedure returns 2 columns, #t has 3 -> error. Always list target columns explicitly.
-- ❌ Procedure returns MULTIPLE result sets -> INSERT...EXEC only supports a single, consistent result set.
-- ❌ Using INSERT...EXEC inside a transaction in a procedure that is later called via INSERT...EXEC by someone else.
-- ❌ Procedure result shape changes (a column added) -> every INSERT...EXEC consumer silently breaks at runtime.
```

---

## 🎯 Interview Tip (1 line)
Say: "INSERT...EXEC works but couples the caller to the procedure's column list and cannot nest — so for reusable logic I prefer an inline table-valued function, and keep procedures for actions." Show you know `sp_describe_first_result_set` to generate the temp-table schema.

---

## 🔗 Related Questions
→ Q079 (Procedure vs function vs view) | Q089 (Inline table-valued functions) | Q016 (Temp tables vs table variables) | Q070 (RETURN codes vs OUTPUT vs result sets)
