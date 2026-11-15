---

# Q103. Covering Index and INCLUDE Columns
# Category: Indexes + Execution Plans
# Difficulty: ⭐⭐ Medium
# DB: SQL Server (PostgreSQL has INCLUDE since v11; MySQL covers via composite indexes only)

---

## ❓ Question
A dashboard runs `SELECT OrderDate, Amount FROM Orders WHERE CustomerId = @c ORDER BY OrderDate` thousands of times a minute. A non-clustered index on `CustomerId` still does key lookups for every row. Create a covering index using `INCLUDE`, and explain key columns vs included columns.

---

## 💡 Quick Concept (2 lines only)
A covering index contains every column a query needs, so SQL Server never touches the clustered index (no key lookup). Key columns define sort/seek order; INCLUDE columns are stored only at the leaf level, adding no sorting cost or key-size limit.
हिंदी: Covering index में query की सारी columns होती हैं, इसलिए table तक जाना नहीं पड़ता। INCLUDE columns सिर्फ leaf में रहती हैं, sort में हिस्सा नहीं लेतीं।

---

## ✅ Answer / Solution

```sql
-- Not executed on SQL Server (no instance available). Query result derived from an equivalent
-- query on SQLite; index/plan behaviour per Microsoft docs.
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

-- BEFORE: seek on CustomerId, then one key lookup per row for OrderDate/Amount
CREATE NONCLUSTERED INDEX IX_Orders_Customer ON dbo.Orders (CustomerId);
GO

-- AFTER: key = (CustomerId, OrderDate) gives seek + sorted output; INCLUDE adds Amount
CREATE NONCLUSTERED INDEX IX_Orders_Customer_Date_Inc
  ON dbo.Orders (CustomerId, OrderDate)
  INCLUDE (Amount);
GO

DROP INDEX IX_Orders_Customer ON dbo.Orders;   -- redundant: left-prefix of the new index
GO

SELECT OrderDate, Amount
FROM dbo.Orders
WHERE CustomerId = 101
ORDER BY OrderDate;

-- Output:
-- OrderDate  | Amount
-- 2024-01-05 | 120.00
-- 2024-02-11 | 80.00
-- 2024-03-20 | 60.00
-- (the plan should show an Index Seek on IX_Orders_Customer_Date_Inc and NO Key Lookup,
--  and no Sort operator because the index is already ordered by OrderDate within a customer)
```

---

## 🔍 Why This Works (3 lines max)
The leaf level of the new index already holds CustomerId, OrderDate (the keys) and Amount (included), plus the clustering key, so the query is answered from one structure. Because OrderDate is the second key column, rows for one customer are already sorted and the ORDER BY needs no Sort step. Including Amount instead of keying it keeps the B-tree upper levels small.
हिंदी: Leaf में सब कुछ मौजूद है, इसलिए key lookup नहीं। OrderDate दूसरी key है तो ORDER BY के लिए sort भी नहीं लगता।

---

## ⚡ Alternative Solution

```sql
-- Make the index smaller for a hot subset only (see Q105 filtered indexes):
CREATE NONCLUSTERED INDEX IX_Orders_Open
  ON dbo.Orders (CustomerId, OrderDate) INCLUDE (Amount)
  WHERE Status = 'Pending';

-- Or put Amount in the key (works, but the key is wider and Amount order is useless here):
CREATE NONCLUSTERED INDEX IX_Orders_Wide ON dbo.Orders (CustomerId, OrderDate, Amount);
```

---

## ⚠️ Common Mistake

```sql
-- ❌ Wrong: INCLUDE everything (INCLUDE (Status, Amount, OrderDate, CustomerId ...)) -> index becomes a second copy of the table
-- ❌ Wrong: SELECT * on a table with a covering index -> new columns break the "covering" property and bring back key lookups
SELECT * FROM dbo.Orders WHERE CustomerId = 101;   -- needs Status too -> key lookup returns
-- ❌ Wrong: leaving both IX_Orders_Customer and the new index; the old one is redundant and just costs write time
```

---

## 🎯 Interview Tip (5+ YOE level)
Say: "I look at the actual plan for Key Lookups with high row counts, then add the lookup columns as INCLUDE rather than keys. Key columns = predicates and ORDER BY; INCLUDE = only SELECTed columns. I keep an eye on write cost and size - and before adding, I check sys.dm_db_index_usage_stats for redundant overlap." Don't promise a speedup number; measure with SET STATISTICS IO before and after.

---

## 🔗 Related Questions
→ Q102 (Clustered vs non-clustered) | Q104 (Composite index column order) | Q107 (Reading an execution plan) | Q144 (Avoid SELECT *)
