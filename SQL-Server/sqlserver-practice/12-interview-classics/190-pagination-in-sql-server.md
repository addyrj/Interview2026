---

# Q190. Pagination in SQL Server
# Category: Interview Classics
# Difficulty: ⭐⭐ Medium
# DB: SQL Server 2012+ (MySQL/PostgreSQL use LIMIT n OFFSET m; SQL Server uses OFFSET ... FETCH and requires ORDER BY)

---

## ❓ Question
An Orders API needs paginated results (newest first), page size 4, with a total count for the UI. Show OFFSET/FETCH, explain why deep pages get slow, and show keyset (seek) pagination as the scalable alternative.

---

## 💡 Quick Concept (2 lines only)
OFFSET @skip ROWS FETCH NEXT @size ROWS ONLY requires ORDER BY and still reads and discards the skipped rows. Keyset pagination remembers the last (OrderDate, OrderId) and seeks past it, so cost stays flat on any page.
हिंदी: OFFSET-FETCH में ORDER BY ज़रूरी है और skipped rows भी पढ़ी जाती हैं। Keyset में last row की key से आगे seek करते हैं, इसलिए deep page भी तेज़ रहता है।

---

## ✅ Answer / Solution

```sql
-- ============================================
-- SETUP
-- ============================================
CREATE TABLE Orders (
    OrderId    INT IDENTITY(1,1) PRIMARY KEY,
    CustomerId INT NOT NULL,
    OrderDate  DATE NOT NULL,
    Total      DECIMAL(10,2) NOT NULL
);

-- 12 orders: OrderId 1..12, OrderDate = 2024-01-01 + (OrderId / 2) days, Total = OrderId * 10
-- (two orders per day on most days, so the date alone is NOT unique)
INSERT INTO Orders (CustomerId, OrderDate, Total) VALUES
 (2,'2024-01-01',10),(3,'2024-01-02',20),(4,'2024-01-02',30),(1,'2024-01-03',40),
 (2,'2024-01-03',50),(3,'2024-01-04',60),(4,'2024-01-04',70),(1,'2024-01-05',80),
 (2,'2024-01-05',90),(3,'2024-01-06',100),(4,'2024-01-06',110),(1,'2024-01-07',120);
GO

-- Supporting index for the sort:
CREATE INDEX IX_Orders_OrderDate_OrderId ON Orders (OrderDate DESC, OrderId DESC);
GO

-- ============================================
-- 1) OFFSET / FETCH  (page 2, size 4)
-- ============================================
DECLARE @Page INT = 2, @Size INT = 4;

SELECT OrderId, OrderDate, Total
FROM Orders
ORDER BY OrderDate DESC, OrderId DESC          -- OrderId = unique tiebreaker
OFFSET (@Page - 1) * @Size ROWS
FETCH NEXT @Size ROWS ONLY;

-- Output (equivalent LIMIT 4 OFFSET 4 on SQLite; not executed on SQL Server):
-- OrderId | OrderDate  | Total
-- 8       | 2024-01-05 | 80
-- 7       | 2024-01-04 | 70
-- 6       | 2024-01-04 | 60
-- 5       | 2024-01-03 | 50

-- ============================================
-- 2) TOTAL COUNT for the pager (one round trip)
-- ============================================
SELECT OrderId, OrderDate, Total,
       COUNT(*) OVER () AS TotalRows           -- 12 on every row
FROM Orders
ORDER BY OrderDate DESC, OrderId DESC
OFFSET 4 ROWS FETCH NEXT 4 ROWS ONLY;
-- TotalRows = 12 -> 3 pages of 4

-- ============================================
-- 3) KEYSET PAGINATION (next page after the last row seen: 2024-01-05, OrderId 9)
-- ============================================
DECLARE @LastDate DATE = '2024-01-05', @LastId INT = 9;

SELECT TOP (4) OrderId, OrderDate, Total
FROM Orders
WHERE OrderDate < @LastDate
   OR (OrderDate = @LastDate AND OrderId < @LastId)
ORDER BY OrderDate DESC, OrderId DESC;

-- Output (hand-checked against the full sorted list 12,11,10,9,8,7,6,5,...):
-- 8, 7, 6, 5  -> same rows as OFFSET page 2, but an index seek instead of skipping 4 rows
```

---

## 🔍 Why This Works (3 lines max)
OFFSET/FETCH is the standard ANSI form (SQL Server 2012+) and is simple, but page N costs O(N x size) because skipped rows are still produced. Keyset turns the skip into a WHERE on the sort key, which the (OrderDate, OrderId) index seeks directly. The unique OrderId tiebreaker stops rows from repeating or vanishing between pages.
हिंदी: OFFSET में skip की गई rows भी process होती हैं। Keyset में WHERE से seek होता है। Unique tiebreaker (OrderId) के बिना pages में rows repeat या गायब हो सकती हैं।

---

## ⚡ Alternative Solution

```sql
-- Pre-2012 / still seen in legacy code: ROW_NUMBER wrapper
WITH Paged AS (
    SELECT OrderId, OrderDate, Total,
           ROW_NUMBER() OVER (ORDER BY OrderDate DESC, OrderId DESC) AS rn
    FROM Orders
)
SELECT OrderId, OrderDate, Total
FROM Paged
WHERE rn BETWEEN 5 AND 8;      -- same rows as page 2

-- Node.js (mssql) with parameters, never string concatenation:
-- const r = await pool.request()
--   .input('skip', sql.Int, (page - 1) * size)
--   .input('size', sql.Int, size)
--   .query(`SELECT OrderId, OrderDate, Total FROM Orders
--           ORDER BY OrderDate DESC, OrderId DESC
--           OFFSET @skip ROWS FETCH NEXT @size ROWS ONLY`);
```

---

## ⚠️ Common Mistake

```sql
-- ❌ Wrong: OFFSET without ORDER BY -> syntax error in SQL Server (ORDER BY is mandatory)
-- ❌ Wrong: ORDER BY a non-unique column only (OrderDate) -> rows can duplicate or skip across pages
-- ✅ Always add a unique tiebreaker (OrderId)

-- ❌ Wrong: TOP / LIMIT habit — SQL Server has no LIMIT keyword
-- ❌ Wrong: running a separate COUNT(*) on a huge filtered table for every page request
-- ✅ Cache the count, use COUNT(*) OVER() on small sets, or drop exact totals ("load more" UI)

-- ❌ Wrong: keyset with ORDER BY on one column but WHERE on another
-- ✅ The WHERE comparison must match the exact ORDER BY columns and direction
```

---

## 🎯 Interview Tip (1 line)
Say: "OFFSET/FETCH for admin screens and small tables; keyset for infinite scroll and large tables, because it stays flat on page 10,000 — the trade-off is you can't jump to an arbitrary page. In both cases I order by a unique key and back it with an index." (Details: Q147, Q083.)

---

## 🔗 Related Questions
→ Q002 (TOP WITH TIES and OFFSET FETCH) | Q083 (Pagination procedure with total count) | Q147 (OFFSET vs keyset performance) | Q110 (SARGable predicates)
