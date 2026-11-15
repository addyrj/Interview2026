---

# Q017. Dynamic SQL with sp_executesql
# Category: T-SQL FUNDAMENTALS
# Difficulty: ⭐⭐⭐ Hard
# DB: SQL Server (MySQL: PREPARE/EXECUTE; PostgreSQL: EXECUTE ... USING in PL/pgSQL)

---

## ❓ Question
Build an order search where the status and minimum amount are optional filters, using dynamic SQL. Show the safe version with `sp_executesql` and parameters, the unsafe `EXEC(@sql)` string-concatenation version, and how table/column names are handled safely.

---

## 💡 Quick Concept (2 lines only)
`sp_executesql` runs an NVARCHAR string with a typed parameter list, so values are passed as parameters (plan reuse, no injection). Only identifiers (table/column names) cannot be parameters, wrap those with `QUOTENAME()` after whitelisting.
हिंदी: sp_executesql में values parameters बनकर जाती हैं (plan reuse + injection safe)। Table/column नाम parameter नहीं बन सकते, उनके लिए QUOTENAME + whitelist।

---

## ✅ Answer / Solution

```sql
-- ============================================
-- SETUP
-- ============================================

CREATE TABLE Orders (
  OrderId    INT PRIMARY KEY,
  CustomerId INT NOT NULL,
  Status     VARCHAR(20) NOT NULL,
  Amount     DECIMAL(10,2) NOT NULL
);

INSERT INTO Orders (OrderId, CustomerId, Status, Amount) VALUES
  (1, 101, 'Shipped',  500.00),
  (2, 101, 'Pending', 1200.00),
  (3, 102, 'Shipped',  300.00),
  (4, 103, 'Pending',  750.00),
  (5, 104, 'Shipped',   90.00),
  (6, 102, 'Shipped', 2000.00);
GO

-- ============================================
-- SOLUTION: parameterized dynamic SQL
-- ============================================

DECLARE @Status    VARCHAR(20)   = 'Shipped';
DECLARE @MinAmount DECIMAL(10,2) = 300;
DECLARE @sql       NVARCHAR(MAX);

SET @sql = N'SELECT OrderId, CustomerId, Amount FROM dbo.Orders WHERE 1 = 1';

IF @Status IS NOT NULL
    SET @sql += N' AND Status = @pStatus';
IF @MinAmount IS NOT NULL
    SET @sql += N' AND Amount >= @pMinAmount';

SET @sql += N' ORDER BY OrderId;';

EXEC sys.sp_executesql
     @sql,
     N'@pStatus VARCHAR(20), @pMinAmount DECIMAL(10,2)',   -- parameter definitions
     @pStatus    = @Status,
     @pMinAmount = @MinAmount;

-- Output:
-- OrderId | CustomerId | Amount
-- 1       | 101        | 500.00
-- 3       | 102        | 300.00
-- 6       | 102        | 2000.00

-- Result derived from the equivalent parameterized query on SQLite 3.49; not executed on SQL Server.
-- (SQLite shows 500.0 instead of 500.00.)

-- ============================================
-- OUTPUT parameter from dynamic SQL
-- ============================================

DECLARE @Cnt INT;
EXEC sys.sp_executesql
     N'SELECT @c = COUNT(*) FROM dbo.Orders WHERE Status = @s',
     N'@s VARCHAR(20), @c INT OUTPUT',
     @s = 'Shipped',
     @c = @Cnt OUTPUT;
SELECT @Cnt AS ShippedCount;   -- 4 (rows 1, 3, 5, 6; hand-checked)

-- ============================================
-- Identifiers: whitelist + QUOTENAME
-- ============================================

DECLARE @SortCol SYSNAME = 'Amount';
IF @SortCol NOT IN ('OrderId', 'Amount', 'CustomerId')
    THROW 50001, 'Invalid sort column', 1;
SET @sql = N'SELECT OrderId, Amount FROM dbo.Orders ORDER BY ' + QUOTENAME(@SortCol) + N' DESC;';
EXEC sys.sp_executesql @sql;
```

---

## 🔍 Why This Works (3 lines max)
The SQL text stays constant for a given filter combination, so SQL Server caches one plan and reuses it for different parameter values. Values never become part of the statement text, so `'; DROP TABLE ...` is just data. QUOTENAME wraps an identifier in brackets and doubles any `]`, and the whitelist is the real defence.
हिंदी: Query text वही रहता है तो एक ही plan cache होता है। Values text का हिस्सा नहीं बनतीं, इसलिए injection नहीं चलता। Identifier के लिए whitelist + QUOTENAME।

---

## ⚡ Alternative Solution

```sql
-- Catch-all static SQL with OPTION (RECOMPILE) - often simpler than dynamic SQL for 2-3 filters:
DECLARE @Status VARCHAR(20) = 'Shipped', @MinAmount DECIMAL(10,2) = NULL;

SELECT OrderId, CustomerId, Amount
FROM Orders
WHERE (@Status IS NULL OR Status = @Status)
  AND (@MinAmount IS NULL OR Amount >= @MinAmount)
OPTION (RECOMPILE);   -- plan is built for the actual values; costs compile time per call
-- Trade-off: dynamic SQL = best cached plans per shape; catch-all = readable, but needs RECOMPILE.
```

---

## ⚠️ Common Mistake

```sql
-- ❌ Wrong: concatenating user input into EXEC(@sql)  (SQL injection)
DECLARE @UserInput VARCHAR(50) = '''; DROP TABLE Orders; --';
DECLARE @bad NVARCHAR(MAX) = N'SELECT * FROM Orders WHERE Status = ''' + @UserInput + N'''';
EXEC (@bad);
-- Becomes: SELECT * FROM Orders WHERE Status = ''; DROP TABLE Orders; --'

-- ❌ Wrong: passing a VARCHAR variable as @stmt (must be NVARCHAR / NCHAR / NVARCHAR(MAX))
-- ❌ Wrong: expecting the dynamic batch to see the caller's local variables or table variables
--           (they are out of scope) - pass them in via the @params list; a #temp table IS visible
-- ❌ Wrong: SET @sql = N'...' + @NullVar  -> whole string becomes NULL, EXEC does nothing silently
-- ✅ Fix: ISNULL on pieces, validate, print @sql while debugging
```

---

## 🎯 Interview Tip (1 line)
Say: "Dynamic SQL only when the query shape changes (optional filters, dynamic sort). Values always go through sp_executesql parameters, identifiers through a whitelist plus QUOTENAME, and I print the generated SQL in dev. For 2-3 optional filters I may prefer the catch-all with OPTION (RECOMPILE)." Mention permissions: dynamic SQL runs with the caller's rights unless the procedure uses EXECUTE AS.

---

## 🔗 Related Questions
→ Q071 (optional filters) | Q078 (dynamic SQL in procedures + injection safety) | Q087 (search procedure with dynamic sorting) | Q137 (SQL injection and parameterization)
