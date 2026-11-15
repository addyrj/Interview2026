---

# Q110. SARGable Predicates
# Category: Indexes + Execution Plans
# Difficulty: ⭐⭐ Medium
# DB: SQL Server (the same principle applies to MySQL and PostgreSQL; functional indexes can rescue it there)

---

## ❓ Question
These queries all return March 2024 orders, but only one can seek on an index over `OrderDate`. Identify which and rewrite the non-SARGable ones: `WHERE YEAR(OrderDate) = 2024 AND MONTH(OrderDate) = 3`, `WHERE CONVERT(VARCHAR(10), OrderDate, 120) LIKE '2024-03%'`, `WHERE DATEADD(DAY, 7, OrderDate) > GETDATE()`, and `WHERE Name LIKE '%son'`.

---

## 💡 Quick Concept (2 lines only)
SARGable = Search ARGument ABLE: the column stands alone on one side of the comparison so the engine can seek the B-tree. Functions or arithmetic on the column, leading wildcards and implicit conversions force a scan.
हिंदी: Column को अकेला रखो, calculation दूसरी तरफ ले जाओ। Column पर function लगाया तो index का seek बंद हो जाता है।

---

## ✅ Answer / Solution

```sql
-- Not executed on SQL Server (no instance available). Result rows derived from the equivalent
-- range query on SQLite; seek vs scan behaviour per Microsoft docs.
-- ============================================
-- SETUP
-- ============================================
CREATE TABLE dbo.Orders (
  OrderId INT PRIMARY KEY, CustomerId INT NOT NULL, OrderDate DATE NOT NULL,
  Status VARCHAR(20) NOT NULL, Amount DECIMAL(10,2) NOT NULL
);
INSERT INTO dbo.Orders VALUES
  (1,101,'2024-01-05','Shipped',120.00),
  (2,101,'2024-02-11','Shipped', 80.00),
  (3,102,'2024-02-15','Pending', 45.50),
  (4,103,'2024-03-02','Shipped',300.00),
  (5,101,'2024-03-20','Pending', 60.00),
  (6,102,'2024-03-25','Cancelled',15.00),
  (7,103,'2024-04-01','Pending', 99.00);
CREATE NONCLUSTERED INDEX IX_Orders_Date ON dbo.Orders (OrderDate) INCLUDE (Amount);
GO

-- ❌ NON-SARGABLE: function wraps the column -> must evaluate for every row (index scan)
SELECT OrderId, Amount FROM dbo.Orders
WHERE YEAR(OrderDate) = 2024 AND MONTH(OrderDate) = 3;

-- ✅ SARGABLE: half-open range, column untouched -> index seek
SELECT OrderId, Amount
FROM dbo.Orders
WHERE OrderDate >= '2024-03-01' AND OrderDate < '2024-04-01'
ORDER BY OrderId;

-- Output (same rows as the YEAR/MONTH version):
-- OrderId | Amount
-- 4       | 300.00
-- 5       | 60.00
-- 6       | 15.00

-- ❌ DATEADD on the column            ->  ✅ move the math to the constant side
-- WHERE DATEADD(DAY, 7, OrderDate) > GETDATE()
-- WHERE OrderDate > DATEADD(DAY, -7, GETDATE())

-- ❌ CONVERT(VARCHAR(10), OrderDate, 120) LIKE '2024-03%'  ->  ✅ the range above
-- ❌ Name LIKE '%son'   (leading wildcard: cannot seek)    ->  ✅ Name LIKE 'Ran%'   (prefix is seekable)
--    For suffix search: persisted computed column on REVERSE(Name) + index, or Full-Text Search.
-- ❌ Amount * 1.1 > 100  ->  ✅ Amount > 100 / 1.1

-- Using DATETIME2/DATETIME columns? Same idea: use [start, next_start) ranges, never BETWEEN '...' AND '...23:59:59'.
```

---

## 🔍 Why This Works (3 lines max)
An index is sorted by the raw column value, so a range on the raw value maps to one contiguous slice. `YEAR(OrderDate) = 2024` hides that ordering, so SQL Server must compute the function for each row. The half-open range `>= start AND < next_start` is precise for DATE, DATETIME and DATETIME2 alike.
हिंदी: Index raw value पर sorted है, function के result पर नहीं। इसलिए range predicate seek करता है, function वाला scan।

---

## ⚡ Alternative Solution

```sql
-- If you cannot change the query (legacy code / ORM): index a computed column
ALTER TABLE dbo.Orders ADD OrderYm AS (YEAR(OrderDate) * 100 + MONTH(OrderDate)) PERSISTED;
CREATE NONCLUSTERED INDEX IX_Orders_Ym ON dbo.Orders (OrderYm);
-- SQL Server can use it when the query expression matches the computed column definition (verify in the plan).
```

---

## ⚠️ Common Mistake

```sql
-- ❌ Wrong: implicit conversion on the column side (silent non-SARGable): CustomerId is INT, N'101' is NVARCHAR
SELECT * FROM dbo.Orders WHERE CustomerId = N'101';   -- INT wins precedence -> constant converted, usually OK
-- But VARCHAR column compared to an NVARCHAR parameter (typical from Node `mssql` defaults) converts the COLUMN:
--   WHERE VarcharCol = @p  with @p NVARCHAR  -> CONVERT_IMPLICIT on the column -> scan (see Q143)
-- ❌ Wrong: BETWEEN '2024-03-01' AND '2024-03-31' on DATETIME -> drops March 31 after midnight
-- ❌ Wrong: ISNULL(col, 0) = 0 in WHERE; write (col = 0 OR col IS NULL)
```

---

## 🎯 Interview Tip (5+ YOE level)
Say: "First thing I check in a slow query is whether the predicate is SARGable: no functions on the column, ranges instead of YEAR/MONTH, no leading wildcards, matching parameter types. In Node, I explicitly set `sql.VarChar` for VARCHAR columns so the driver does not send NVARCHAR and trigger implicit conversion." Prove it with the plan (Seek vs Scan) and logical reads.

---

## 🔗 Related Questions
→ Q007 (Date functions) | Q009 (LIKE and wildcard pitfalls) | Q143 (Avoiding implicit conversions) | Q161 (Parameterized queries from Node)
