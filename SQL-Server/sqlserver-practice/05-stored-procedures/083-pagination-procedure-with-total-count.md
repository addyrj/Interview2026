---

# Q083. Pagination Procedure with Total Count
# Category: Stored Procedures
# DB: SQL Server (2012+ for OFFSET/FETCH) (MySQL: LIMIT/OFFSET + SQL_CALC_FOUND_ROWS removed in 8.0.17; PostgreSQL: LIMIT/OFFSET + COUNT(*) OVER())
# Difficulty: ⭐⭐⭐ Hard

---

## ❓ Question
Write `dbo.usp_GetOrdersPage @PageNumber, @PageSize` for a grid in a Node.js/React app that returns the page rows AND the total row count (to draw page numbers). Use `OFFSET ... FETCH`, a deterministic order and one pass over the data. Mention keyset pagination for deep pages.

---

## 💡 Quick Concept (2 lines only)
`ORDER BY ... OFFSET (@Page-1)*@Size ROWS FETCH NEXT @Size ROWS ONLY` gives the page; `COUNT(*) OVER()` adds the total in the same query. ORDER BY must be deterministic (add a unique tiebreaker such as the primary key), otherwise rows can repeat or skip between pages.
हिंदी: `OFFSET/FETCH` से page, `COUNT(*) OVER()` से total। ORDER BY में unique tiebreaker ज़रूर रखो।

---

## ✅ Answer / Solution

```sql
-- ============================================
-- SETUP
-- ============================================

CREATE TABLE dbo.Orders (
  OrderId    INT           NOT NULL PRIMARY KEY,
  CustomerId INT           NOT NULL,
  Amount     DECIMAL(10,2) NOT NULL,
  OrderDate  DATE          NOT NULL
);
INSERT INTO dbo.Orders (OrderId, CustomerId, Amount, OrderDate) VALUES
  (1,101, 250.00,'2024-01-05'),(2,101,  80.00,'2024-02-10'),(3,102,1200.00,'2024-02-14'),
  (4,103,  45.50,'2024-03-01'),(5,102, 310.00,'2024-03-09'),(6,104,  99.99,'2024-03-15'),
  (7,101, 560.00,'2024-04-02');
GO
CREATE INDEX IX_Orders_OrderDate ON dbo.Orders (OrderDate DESC, OrderId DESC);
GO

-- ============================================
-- SOLUTION
-- ============================================

CREATE OR ALTER PROCEDURE dbo.usp_GetOrdersPage
    @PageNumber INT = 1,
    @PageSize   INT = 20
AS
BEGIN
    SET NOCOUNT ON;

    IF @PageNumber < 1 SET @PageNumber = 1;
    IF @PageSize NOT BETWEEN 1 AND 100 SET @PageSize = 20;      -- cap: protect the server from huge pages

    SELECT
        OrderId, CustomerId, Amount,
        COUNT(*) OVER () AS TotalRows                           -- total matching rows, repeated on each row
    FROM dbo.Orders
    ORDER BY OrderDate DESC, OrderId DESC                       -- deterministic: unique tiebreaker
    OFFSET (@PageNumber - 1) * @PageSize ROWS
    FETCH NEXT @PageSize ROWS ONLY;
END;
GO

EXEC dbo.usp_GetOrdersPage @PageNumber = 2, @PageSize = 3;
-- Expected (result derived from equivalent LIMIT 3 OFFSET 3 query on SQLite; not executed on SQL Server):
-- OrderId | CustomerId | Amount  | TotalRows
-- 4       | 103        | 45.50   | 7
-- 3       | 102        | 1200.00 | 7
-- 2       | 101        | 80.00   | 7

EXEC dbo.usp_GetOrdersPage @PageNumber = 1, @PageSize = 3;
-- 7 | 101 | 560.00 | 7
-- 6 | 104 | 99.99  | 7
-- 5 | 102 | 310.00 | 7
-- Page 3 would return 1 row (OrderId 1). TotalPages = CEILING(7 / 3.0) = 3 is computed in the app.
```

---

## 🔍 Why This Works (3 lines max)
The window `COUNT(*) OVER ()` is evaluated before OFFSET/FETCH trims the rows, so one query returns both the page and the full count without a second scan. The ORDER BY on date plus unique id makes page boundaries stable between calls.
हिंदी: Window count OFFSET से पहले चलता है इसलिए एक ही query में total मिल जाता है। Order stable रखने के लिए id जोड़ो।

---

## ⚡ Alternative Solution

```sql
-- Keyset (seek) pagination: constant cost for deep pages, no OFFSET scan. The client sends the last row's key.
CREATE OR ALTER PROCEDURE dbo.usp_GetOrdersAfter
    @LastOrderDate DATE = NULL,
    @LastOrderId   INT  = NULL,
    @PageSize      INT  = 20
AS
BEGIN
    SET NOCOUNT ON;
    SELECT TOP (@PageSize) OrderId, CustomerId, Amount, OrderDate
    FROM dbo.Orders
    WHERE @LastOrderDate IS NULL
       OR OrderDate < @LastOrderDate
       OR (OrderDate = @LastOrderDate AND OrderId < @LastOrderId)
    ORDER BY OrderDate DESC, OrderId DESC;
END;
GO
-- Trade-off: no "jump to page 57", no cheap total count -- good for infinite scroll / APIs.
-- Separate-count variant: run SELECT COUNT(*) once (cache it) when the count is expensive on filtered big tables.
```

---

## ⚠️ Common Mistake

```sql
-- ❌ OFFSET/FETCH without ORDER BY -> syntax error (ORDER BY is required).
-- ❌ ORDER BY a non-unique column only (OrderDate): ties make rows duplicate/skip across pages.
-- ❌ Deep OFFSET (e.g. page 50,000): SQL Server still reads and discards all skipped rows -> slow. Use keyset.
-- ❌ FETCH NEXT @PageSize with unvalidated client value -> someone requests 10,000,000 rows.
-- ❌ Using ROW_NUMBER() subquery on SQL Server 2008-era habit, plus a separate COUNT(*) query, when
--    OFFSET/FETCH (2012+) is simpler.
-- ❌ Empty page (beyond last page): TotalRows is NOT returned because zero rows come back -- handle in the app.
```

---

## 🎯 Interview Tip (1 line)
Say: "OFFSET/FETCH with a deterministic ORDER BY and `COUNT(*) OVER()` for grid UIs, a capped page size, and keyset pagination for deep or infinite-scroll lists — and I mention that the empty-page case loses the total, so the API returns it separately when needed." Index the ORDER BY columns to avoid a sort.

---

## 🔗 Related Questions
→ Q002 (TOP WITH TIES and OFFSET FETCH) | Q056 (ROW_NUMBER, RANK, DENSE_RANK) | Q087 (Search procedure with dynamic filters and sorting) | Q110 (SARGable predicates)
