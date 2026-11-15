---

# Q087. Search Procedure with Dynamic Filters and Sorting
# Category: Stored Procedures
# Difficulty: ⭐⭐⭐ Hard
# DB: SQL Server (MySQL: PREPARE/EXECUTE with CONCAT; PostgreSQL: format() + EXECUTE ... USING)

---

## ❓ Question
Build `usp_SearchProducts` for a product listing page: optional filters (category, min price), a user-chosen sort column and direction, and paging. It must be fast for every filter combination and safe from SQL injection (the sort column comes from the query string).

---

## 💡 Quick Concept (2 lines only)
Values go through `sp_executesql` parameters (never concatenated); identifiers (sort column) cannot be parameters, so map them from a whitelist. Build only the predicates that are needed so each shape gets its own good plan.
हिंदी: Values = parameters, column names = whitelist। सिर्फ़ ज़रूरी filters जोड़ो ताकि हर combination का अपना सही plan बने।

---

## ✅ Answer / Solution

```sql
-- ============================================
-- SETUP
-- ============================================

CREATE TABLE dbo.Products (
  ProductId INT PRIMARY KEY,
  Name      NVARCHAR(100) NOT NULL,
  Category  NVARCHAR(50)  NOT NULL,
  Price     DECIMAL(10,2) NOT NULL
);

INSERT INTO dbo.Products VALUES
  (1, N'Laptop Pro',   N'Electronics', 1200),
  (2, N'Desk Lamp',    N'Home',          35),
  (3, N'Phone X',      N'Electronics',  800),
  (4, N'Office Chair', N'Home',         150),
  (5, N'Headphones',   N'Electronics',  150),
  (6, N'Tablet',       N'Electronics',  450);
GO

-- ============================================
-- SOLUTION
-- ============================================

CREATE OR ALTER PROCEDURE dbo.usp_SearchProducts
  @Category NVARCHAR(50) = NULL,
  @MinPrice DECIMAL(10,2) = NULL,
  @SortBy   VARCHAR(20)  = 'Name',
  @SortDir  VARCHAR(4)   = 'ASC',
  @PageNo   INT = 1,
  @PageSize INT = 20
AS
BEGIN
  SET NOCOUNT ON;

  -- whitelist: user input never reaches the SQL text
  DECLARE @OrderCol SYSNAME = CASE @SortBy
        WHEN 'Name'  THEN N'Name'
        WHEN 'Price' THEN N'Price'
        ELSE N'ProductId' END;
  DECLARE @Dir VARCHAR(4) = CASE WHEN UPPER(@SortDir) = 'DESC' THEN 'DESC' ELSE 'ASC' END;

  DECLARE @sql NVARCHAR(MAX) = N'
    SELECT ProductId, Name, Price
    FROM dbo.Products
    WHERE 1 = 1';

  IF @Category IS NOT NULL SET @sql = @sql + N' AND Category = @Category';
  IF @MinPrice IS NOT NULL SET @sql = @sql + N' AND Price >= @MinPrice';

  SET @sql = @sql + N' ORDER BY ' + QUOTENAME(@OrderCol) + N' ' + @Dir + N', ProductId'  -- tiebreaker
            + N' OFFSET (@PageNo - 1) * @PageSize ROWS FETCH NEXT @PageSize ROWS ONLY;';

  EXEC sys.sp_executesql @sql,
       N'@Category NVARCHAR(50), @MinPrice DECIMAL(10,2), @PageNo INT, @PageSize INT',
       @Category, @MinPrice, @PageNo, @PageSize;
END;
GO

EXEC dbo.usp_SearchProducts @Category = N'Electronics', @MinPrice = 100,
                            @SortBy = 'Price', @SortDir = 'DESC', @PageSize = 2;
EXEC dbo.usp_SearchProducts @SortBy = 'Name', @PageSize = 3;

-- EXPECTED OUTPUT (generated statements reproduced on SQLite with LIMIT/OFFSET; the
-- dynamic SQL/sp_executesql path is not executed on SQL Server):
-- ProductId | Name       | Price
-- 1         | Laptop Pro | 1200.00
-- 3         | Phone X    | 800.00
--
-- ProductId | Name       | Price
-- 2         | Desk Lamp  | 35.00
-- 5         | Headphones | 150.00
-- 1         | Laptop Pro | 1200.00
```

Node.js (`mssql`):

```javascript
const r = await pool.request()
  .input('Category', sql.NVarChar(50), req.query.category ?? null)
  .input('MinPrice', sql.Decimal(10, 2), req.query.minPrice ?? null)
  .input('SortBy', sql.VarChar(20), req.query.sortBy ?? 'Name')
  .input('SortDir', sql.VarChar(4), req.query.dir ?? 'ASC')
  .execute('dbo.usp_SearchProducts');
```

---

## 🔍 Why This Works (3 lines + Hindi 1 line)
Filter values travel as typed parameters, so there is no injection path and plans are reused per shape. The sort column is chosen from a fixed list and wrapped in QUOTENAME as a second defence. Adding only the needed predicates avoids the one-plan-fits-all problem of catch-all queries.
हिंदी: Values parameter से, sort column whitelist + QUOTENAME से। जितने filter चाहिए बस उतने जोड़ो, हर shape का अलग cached plan।

---

## ⚡ Alternative Solution

```sql
-- Catch-all (no dynamic SQL) with OPTION (RECOMPILE): simpler, fresh plan per call, costs compile CPU.
SELECT ProductId, Name, Price
FROM dbo.Products
WHERE (@Category IS NULL OR Category = @Category)
  AND (@MinPrice IS NULL OR Price >= @MinPrice)
ORDER BY CASE WHEN @SortBy = 'Price' THEN Price END DESC,   -- CASE per direction needed
         Name
OPTION (RECOMPILE);
-- Without RECOMPILE the cached plan from the first call is reused for all shapes (parameter sniffing).
```

---

## ⚠️ Common Mistake

```sql
-- ❌ Wrong: concatenating user input
SET @sql = N'... WHERE Category = ''' + @Category + N'''';      -- SQL injection
SET @sql = @sql + N' ORDER BY ' + @SortBy;                            -- injection through the column name

-- ❌ Wrong: ORDER BY without a unique tiebreaker + OFFSET -> rows duplicate/skip across pages.
-- ❌ Wrong: using EXEC(@sql) instead of sp_executesql -> no parameters, poor plan reuse.
-- ✅ Whitelist identifiers, parameterize values, add ProductId tiebreaker.
```

---

## 🎯 Interview Tip (1 line)
Say: "Dynamic search is the legitimate use of dynamic SQL: parameterized with sp_executesql, identifiers whitelisted and QUOTENAMEd, only needed predicates appended, deterministic ORDER BY for paging. I also ensure the proc runs under limited permissions (ownership chaining does not apply inside dynamic SQL), and compare with OPTION (RECOMPILE) when traffic is low."

---

## 🔗 Related Questions
→ Q017 (Dynamic SQL with sp_executesql) | Q071 (Optional filters, catch-all) | Q078 (Dynamic SQL + injection safety) | Q083 (Pagination procedure) | Q114 (Parameter sniffing)
