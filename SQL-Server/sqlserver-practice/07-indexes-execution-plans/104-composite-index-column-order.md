---

# Q104. Composite Index Column Order
# Category: Indexes + Execution Plans
# Difficulty: ⭐⭐ Medium
# DB: SQL Server (same leftmost-prefix rule in MySQL and PostgreSQL; SQL Server has no index skip-scan)

---

## ❓ Question
You have an index on `Orders (CustomerId, OrderDate)`. Which of these queries can seek on it: filter by CustomerId; filter by CustomerId and a date range; filter by OrderDate only? How should you choose the column order for a new composite index?

---

## 💡 Quick Concept (2 lines only)
A composite index is sorted by the first column, then the second within each first value, so only a leftmost prefix can be sought. Rule of thumb: equality columns first, then the range/sort column; selectivity matters less than the query shapes you actually run.
हिंदी: Composite index पहली column से sorted होती है, इसलिए सिर्फ left से शुरू होने वाले filters पर seek होता है। Equality columns पहले, range column बाद में।

---

## ✅ Answer / Solution

```sql
-- Not executed on SQL Server (no instance available). Result sets derived from equivalent
-- queries on SQLite; seek/scan behaviour per Microsoft docs.
-- ============================================
-- SETUP
-- ============================================
CREATE TABLE dbo.Orders (
  OrderId    INT PRIMARY KEY,
  CustomerId INT NOT NULL,
  OrderDate  DATE NOT NULL,
  Status     VARCHAR(20) NOT NULL,
  Amount     DECIMAL(10,2) NOT NULL
);
INSERT INTO dbo.Orders VALUES
  (1,101,'2024-01-05','Shipped',120.00),
  (2,101,'2024-02-11','Shipped', 80.00),
  (3,102,'2024-02-15','Pending', 45.50),
  (4,103,'2024-03-02','Shipped',300.00),
  (5,101,'2024-03-20','Pending', 60.00),
  (6,102,'2024-03-25','Cancelled',15.00),
  (7,103,'2024-04-01','Pending', 99.00);
GO
CREATE NONCLUSTERED INDEX IX_Orders_Cust_Date ON dbo.Orders (CustomerId, OrderDate) INCLUDE (Amount);
GO

-- Q1: leading column only -> can SEEK
SELECT OrderId, Amount FROM dbo.Orders WHERE CustomerId = 102 ORDER BY OrderId;
-- OrderId | Amount
-- 3       | 45.50
-- 6       | 15.00

-- Q2: equality on 1st + range on 2nd -> best case: one seek, a contiguous slice
SELECT OrderId, Amount FROM dbo.Orders
WHERE CustomerId = 102 AND OrderDate >= '2024-03-01'
ORDER BY OrderId;
-- OrderId | Amount
-- 6       | 15.00

-- Q3: ONLY the 2nd column -> cannot seek on this index (dates are scattered across every customer);
--     the optimizer scans the index (or table). Same rows, different cost:
SELECT OrderId, Amount FROM dbo.Orders
WHERE OrderDate >= '2024-03-01' AND OrderDate < '2024-04-01'
ORDER BY OrderId;
-- OrderId | Amount
-- 4       | 300.00
-- 5       | 60.00
-- 6       | 15.00

-- If Q3 is also hot, add a second index led by the date:
CREATE NONCLUSTERED INDEX IX_Orders_Date ON dbo.Orders (OrderDate) INCLUDE (CustomerId, Amount);
```

---

## 🔍 Why This Works (3 lines max)
Inside the B-tree, entries are ordered by (CustomerId, OrderDate), so a given customer plus a date range maps to one contiguous run that a single seek can find. Filtering only on OrderDate would have to probe every customer's section, which is a scan. Equality first, range last keeps the seek predicate usable on both columns.
हिंदी: Index (CustomerId, OrderDate) का मतलब है पहले customer, फिर उसके अंदर date। सिर्फ date से ढूँढोगे तो हर customer के हिस्से में देखना पड़ेगा (scan)।

---

## ⚡ Alternative Solution

```sql
-- One index per query shape vs one wide index: check actual workload first.
-- Find unused/duplicate indexes before adding more (DMV counters reset on restart):
SELECT OBJECT_NAME(s.object_id) AS TableName, i.name AS IndexName,
       s.user_seeks, s.user_scans, s.user_lookups, s.user_updates
FROM sys.dm_db_index_usage_stats s
JOIN sys.indexes i ON i.object_id = s.object_id AND i.index_id = s.index_id
WHERE s.database_id = DB_ID() AND s.object_id = OBJECT_ID('dbo.Orders');
-- Not executed here; values depend on your workload.
```

---

## ⚠️ Common Mistake

```sql
-- ❌ Wrong: "put the most selective column first" as an absolute rule.
--    (OrderDate, CustomerId) is more "selective" overall, but WHERE CustomerId = 101 can no longer seek on it.
-- ❌ Wrong: expecting an index on (CustomerId, OrderDate) to help ORDER BY OrderDate without the CustomerId equality filter
SELECT TOP (10) * FROM dbo.Orders ORDER BY OrderDate DESC;   -- needs an index led by OrderDate
-- ❌ Wrong: wrapping the leading column in a function -> index unusable for seek (see Q110)
```

---

## 🎯 Interview Tip (5+ YOE level)
Say: "I design from the query list, not the table: equality predicates first, then the one range or ORDER BY column, then INCLUDE for the rest. One index that serves two or three query shapes via its prefix beats many overlapping ones. SQL Server has no skip scan, so the leading column matters more than in some other engines."

---

## 🔗 Related Questions
→ Q102 (Clustered vs non-clustered) | Q103 (Covering index) | Q110 (SARGable predicates) | Q112 (Missing index DMVs)
