---

# Q071. Default Parameters and Optional Filters (Catch-All Query)
# Category: Stored Procedures
# Difficulty: ⭐⭐⭐ Hard
# DB: SQL Server (MySQL/PostgreSQL procedures have DEFAULT params too, but no OPTION (RECOMPILE) — use dynamic SQL or COALESCE there)

---

## ❓ Question
Write `dbo.usp_SearchOrders` with optional filters: `@CustomerId`, `@Status`, `@MinAmount`. If a parameter is not passed (NULL), that filter must be ignored. Make it perform well — the classic `(@p IS NULL OR col = @p)` catch-all has a plan-caching problem. How do you fix it?

---

## 💡 Quick Concept (2 lines only)
Give parameters `= NULL` defaults and write `WHERE (@p IS NULL OR col = @p)`. One cached plan must serve every parameter combination, so it is often bad — add `OPTION (RECOMPILE)` (small/medium tables) or build dynamic SQL with `sp_executesql` (large tables).
हिंदी: Parameter को `= NULL` default दो, `(@p IS NULL OR col=@p)` लिखो। Plan cache की problem के लिए `OPTION (RECOMPILE)` या dynamic SQL।

---

## ✅ Answer / Solution

```sql
-- ============================================
-- SETUP
-- ============================================

CREATE TABLE dbo.Orders (
  OrderId     INT           NOT NULL PRIMARY KEY,
  CustomerId  INT           NOT NULL,
  Status      VARCHAR(20)   NOT NULL,
  Amount      DECIMAL(10,2) NOT NULL,
  OrderDate   DATE          NOT NULL
);
GO

INSERT INTO dbo.Orders (OrderId, CustomerId, Status, Amount, OrderDate) VALUES
  (1, 101, 'Shipped',   250.00,  '2024-01-05'),
  (2, 101, 'Pending',    80.00,  '2024-02-10'),
  (3, 102, 'Shipped',  1200.00,  '2024-02-14'),
  (4, 103, 'Cancelled',  45.50,  '2024-03-01'),
  (5, 102, 'Pending',   310.00,  '2024-03-09'),
  (6, 104, 'Shipped',    99.99,  '2024-03-15'),
  (7, 101, 'Shipped',   560.00,  '2024-04-02');
GO

-- ============================================
-- SOLUTION: catch-all with OPTION (RECOMPILE)
-- ============================================

CREATE OR ALTER PROCEDURE dbo.usp_SearchOrders   -- CREATE OR ALTER: SQL Server 2016 SP1+
    @CustomerId INT           = NULL,
    @Status     VARCHAR(20)   = NULL,
    @MinAmount  DECIMAL(10,2) = NULL
AS
BEGIN
    SET NOCOUNT ON;

    SELECT OrderId, CustomerId, Status, Amount
    FROM dbo.Orders
    WHERE (@CustomerId IS NULL OR CustomerId = @CustomerId)
      AND (@Status     IS NULL OR Status     = @Status)
      AND (@MinAmount  IS NULL OR Amount    >= @MinAmount)
    ORDER BY OrderId
    OPTION (RECOMPILE);   -- optimizer sees actual values, removes the dead "IS NULL" branches
END;
GO

-- ============================================
-- EXEC examples (named params: order does not matter)
-- ============================================

EXEC dbo.usp_SearchOrders @Status = 'Shipped', @MinAmount = 200;
-- Expected output (result derived from equivalent query on SQLite; not executed on SQL Server):
-- OrderId | CustomerId | Status  | Amount
-- 1       | 101        | Shipped | 250.00
-- 3       | 102        | Shipped | 1200.00
-- 7       | 101        | Shipped | 560.00

EXEC dbo.usp_SearchOrders @CustomerId = 101;
-- OrderId | CustomerId | Status  | Amount
-- 1       | 101        | Shipped | 250.00
-- 2       | 101        | Pending | 80.00
-- 7       | 101        | Shipped | 560.00

EXEC dbo.usp_SearchOrders;   -- no params = all 7 rows
```

Note: the plan/RECOMPILE behaviour itself is not executed on SQL Server; it is per Microsoft docs. The filter logic output was verified on SQLite (NULL params bound as NULL).

---

## 🔍 Why This Works (3 lines max)
When a parameter is NULL, `@p IS NULL` is true and the whole OR is true, so the filter is skipped. `OPTION (RECOMPILE)` compiles the statement with the runtime values (parameter embedding), so a NULL branch is folded away and a seek on a useful index becomes possible.
हिंदी: NULL आने पर condition true हो जाती है → filter skip। RECOMPILE से हर call पर नया plan बनता है जो actual values देखता है।

---

## ⚡ Alternative Solution

```sql
-- Dynamic SQL: one cached plan PER shape of query, fully parameterized (safe from injection)
CREATE OR ALTER PROCEDURE dbo.usp_SearchOrders_Dyn
    @CustomerId INT           = NULL,
    @Status     VARCHAR(20)   = NULL,
    @MinAmount  DECIMAL(10,2) = NULL
AS
BEGIN
    SET NOCOUNT ON;
    DECLARE @sql NVARCHAR(MAX) = N'SELECT OrderId, CustomerId, Status, Amount FROM dbo.Orders WHERE 1 = 1';

    IF @CustomerId IS NOT NULL SET @sql += N' AND CustomerId = @CustomerId';
    IF @Status     IS NOT NULL SET @sql += N' AND Status = @Status';
    IF @MinAmount  IS NOT NULL SET @sql += N' AND Amount >= @MinAmount';
    SET @sql += N' ORDER BY OrderId';

    EXEC sys.sp_executesql @sql,
         N'@CustomerId INT, @Status VARCHAR(20), @MinAmount DECIMAL(10,2)',
         @CustomerId, @Status, @MinAmount;
END;
GO
-- Best for big tables: each combination gets its own reusable plan, no compile cost per call.
-- MySQL/PostgreSQL: same idea with PREPARE/EXECUTE or format()/EXECUTE USING.
```

---

## ⚠️ Common Mistake

```sql
-- ❌ Catch-all WITHOUT RECOMPILE on a big table:
--   first call EXEC ... @CustomerId = 101 caches a plan built for that value/shape;
--   next call with only @Status reuses the same plan -> scan or bad seek, random slowness.
-- ❌ Using ISNULL(col, '') = ISNULL(@p, '') -> wraps the column in a function (non-SARGable) and
--    changes meaning for rows where col is really NULL.
-- ❌ Concatenating @Status into the SQL string -> SQL injection (see Q078).
-- ✅ Use OPTION (RECOMPILE) or parameterized sp_executesql.
```

---

## 🎯 Interview Tip (1 line)
Say: "Catch-all is a parameter-sniffing trap — I use `OPTION (RECOMPILE)` for low-frequency search screens and parameterized `sp_executesql` for hot paths, and I verify with Query Store which plans exist." Mention that `OPTION (RECOMPILE)` costs CPU per call, so it is wrong for a procedure called thousands of times per second.

---

## 🔗 Related Questions
→ Q069 (Input and OUTPUT parameters) | Q078 (Dynamic SQL + injection) | Q080 (Recompile and parameter sniffing) | Q087 (Search procedure with dynamic filters)
