---

# Q078. Dynamic SQL in Procedures + SQL Injection Safety
# Category: Stored Procedures
# Difficulty: ⭐⭐⭐ Hard
# DB: SQL Server (MySQL: PREPARE/EXECUTE; PostgreSQL: EXECUTE format(... %I ...) USING)

---

## ❓ Question
A procedure must sort by a user-chosen column and direction and optionally filter by status. Table and column names cannot be parameters. Write it with `sp_executesql` so it is injection-safe: parameterize values, whitelist/QUOTENAME identifiers. Show an attack against the unsafe version.

---

## 💡 Quick Concept (2 lines only)
Values go through `sp_executesql` parameters (never string concatenation); identifiers (column/table names, ASC/DESC) cannot be parameters, so validate against a whitelist (`sys.columns`/`IN (...)`) and wrap with `QUOTENAME()`. `EXEC(@sql)` with concatenated user input is the classic injection hole.
हिंदी: Values = `sp_executesql` parameters। Column/table नाम = whitelist + `QUOTENAME`। User input कभी सीधे string में मत जोड़ो।

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
INSERT INTO dbo.Orders VALUES (1,101,'Shipped',250.00),(2,101,'Pending',80.00),(3,102,'Shipped',1200.00);
GO

-- ============================================
-- SOLUTION (safe)
-- ============================================

CREATE OR ALTER PROCEDURE dbo.usp_ListOrders
    @Status    VARCHAR(20) = NULL,
    @SortCol   SYSNAME     = N'OrderId',
    @SortDir   VARCHAR(4)  = 'ASC'
AS
BEGIN
    SET NOCOUNT ON;

    -- 1) whitelist identifiers: column must exist on the table, direction must be ASC/DESC
    IF NOT EXISTS (SELECT 1 FROM sys.columns
                   WHERE object_id = OBJECT_ID(N'dbo.Orders') AND name = @SortCol)
        THROW 50001, 'Invalid sort column.', 1;
    IF @SortDir NOT IN ('ASC', 'DESC')
        THROW 50002, 'Invalid sort direction.', 1;

    -- 2) build SQL: identifiers via QUOTENAME, values stay as parameters
    DECLARE @sql NVARCHAR(MAX) =
        N'SELECT OrderId, CustomerId, Status, Amount FROM dbo.Orders WHERE 1 = 1'
      + CASE WHEN @Status IS NOT NULL THEN N' AND Status = @pStatus' ELSE N'' END
      + N' ORDER BY ' + QUOTENAME(@SortCol) + N' ' + @SortDir;

    -- 3) execute parameterized
    EXEC sys.sp_executesql @sql, N'@pStatus VARCHAR(20)', @pStatus = @Status;
END;
GO

EXEC dbo.usp_ListOrders @Status = 'Shipped', @SortCol = N'Amount', @SortDir = 'DESC';
-- Expected (equivalent ORDER BY Amount DESC on SQLite; not executed on SQL Server):
-- OrderId | CustomerId | Status  | Amount
-- 3       | 102        | Shipped | 1200.00
-- 1       | 101        | Shipped | 250.00

EXEC dbo.usp_ListOrders @SortCol = N'Amount; DROP TABLE dbo.Orders;--';
-- Rejected by the whitelist: no column with that name exists -> THROW 50001 'Invalid sort column.'
```

---

## 🔍 Why This Works (3 lines max)
Parameter values are sent separately from the SQL text, so they can never change the statement structure. Identifiers cannot be parameters, so we only accept names that exist in `sys.columns` and bracket-quote them with `QUOTENAME`, which also escapes a closing bracket.
हिंदी: Values अलग से जाती हैं इसलिए query structure नहीं बदलती। Column नाम whitelist से check होता है और `QUOTENAME` से सुरक्षित बनता है।

---

## ⚡ Alternative Solution

```sql
-- No dynamic SQL for sorting: CASE in ORDER BY (fixed set of columns, one plan, but each CASE branch
-- must have a compatible type, and the optimizer cannot use an index for ordering through CASE)
SELECT OrderId, CustomerId, Status, Amount
FROM dbo.Orders
ORDER BY
    CASE WHEN @SortCol = 'Amount'  AND @SortDir = 'ASC'  THEN Amount END ASC,
    CASE WHEN @SortCol = 'Amount'  AND @SortDir = 'DESC' THEN Amount END DESC,
    OrderId;
```

---

## ⚠️ Common Mistake

```sql
-- ❌ The classic hole:
DECLARE @sql NVARCHAR(MAX) = N'SELECT * FROM dbo.Orders WHERE Status = ''' + @Status + N'''';
EXEC (@sql);
-- Input  @Status = N'x'' OR 1=1; DROP TABLE dbo.Orders;--'
-- becomes: ... WHERE Status = 'x' OR 1=1; DROP TABLE dbo.Orders;--'   -> all rows returned and table dropped
--          (if the caller's permissions allow it).

-- ❌ EXEC (@sql) instead of sp_executesql: no parameterization, and separate plan per literal (plan cache bloat).
-- ❌ QUOTENAME on a value (it is for identifiers; max 128 chars input) -- use parameters for values.
-- ❌ Running dynamic SQL under an over-privileged owner; ownership chaining does NOT apply inside dynamic SQL,
--    so the caller needs permissions on the underlying tables (or use EXECUTE AS -- see Q081).
-- ❌ VARCHAR instead of NVARCHAR for @sql / sp_executesql -> sp_executesql requires NVARCHAR text.
```

---

## 🎯 Interview Tip (1 line)
Say: "Values always travel as `sp_executesql` parameters; identifiers are whitelisted against `sys.columns` or a fixed list and wrapped in `QUOTENAME`; the app account has least privilege. I also remember that dynamic SQL runs in its own scope, so temp tables created inside it vanish and local variables are not visible." Pair it with the Node.js side using `.input()` instead of string templates.

---

## 🔗 Related Questions
→ Q017 (Dynamic SQL with sp_executesql) | Q071 (Optional filters) | Q081 (WITH EXECUTE AS) | Q087 (Search procedure with dynamic filters and sorting)
