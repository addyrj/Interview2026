---

# Q144. Avoid SELECT * and Wide Scans
# Category: Performance Tuning
# Difficulty: ⭐⭐ Medium
# DB: SQL Server (same advice in MySQL/PostgreSQL; INCLUDE columns are SQL Server/PostgreSQL 11+). Plan effects not executed on SQL Server.

---

## ❓ Question
An endpoint lists a customer's pending orders but runs `SELECT * FROM Orders WHERE CustomerId = @id`. The table has a 4000-char `Notes` column. Why is it slow, and what is the fix?

---

## 💡 Quick Concept (2 lines only)
SELECT * defeats covering indexes (forces key lookups), moves unneeded bytes over the network, and breaks when columns are added. Select only needed columns and give the query a narrow covering index.
हिंदी: SELECT * से covering index बेकार हो जाता है, ज़्यादा data network पर जाता है। सिर्फ़ ज़रूरी columns माँगो।

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
  Amount     DECIMAL(10,2) NOT NULL,
  OrderDate  DATE NOT NULL,
  Notes      NVARCHAR(4000) NULL
);

INSERT INTO Orders (OrderId, CustomerId, Status, Amount, OrderDate) VALUES
  (1,1,'Pending',10,'2024-01-01'), (2,1,'Pending',20,'2024-01-02'),
  (3,2,'Shipped',30,'2024-01-03'), (4,1,'Pending',40,'2024-01-04'),
  (5,3,'Pending',50,'2024-01-05'), (6,1,'Pending',60,'2024-01-06'),
  (7,2,'Shipped',70,'2024-01-07'), (8,1,'Pending',80,'2024-01-08'),
  (9,4,'Pending',90,'2024-01-09'), (10,1,'Pending',100,'2024-01-10');

-- ============================================
-- BAD
-- ============================================
SELECT * FROM Orders WHERE CustomerId = 1 AND Status = 'Pending';
-- needs clustered index lookup for every row to fetch Notes etc.

-- ============================================
-- GOOD: narrow column list + covering index
-- ============================================
CREATE INDEX IX_Orders_Customer_Status
  ON Orders (CustomerId, Status)
  INCLUDE (Amount, OrderDate);

SELECT OrderId, Amount, OrderDate
FROM Orders
WHERE CustomerId = 1 AND Status = 'Pending'
ORDER BY OrderDate DESC;

-- EXPECTED OUTPUT (result derived from equivalent query on SQLite; not executed on SQL Server):
-- OrderId | Amount | OrderDate
-- 10      | 100.00 | 2024-01-10
-- 8       | 80.00  | 2024-01-08
-- 6       | 60.00  | 2024-01-06
-- 4       | 40.00  | 2024-01-04
-- 2       | 20.00  | 2024-01-02
-- (OrderId is the clustered key, so it is carried in every nonclustered index)
```

---

## 🔍 Why This Works (3 lines max)
The index holds CustomerId, Status (seek keys), Amount and OrderDate (INCLUDEd), plus the clustered key, so no key lookup is needed. Fewer pages are read and no large NVARCHAR column is sent over the wire.
हिंदी: Covering index = सारे columns index में ही मिल जाते हैं, table तक जाना नहीं पड़ता।

---

## ⚡ Alternative Solution

```sql
-- Measure instead of guessing
SET STATISTICS IO ON;
SELECT * FROM Orders WHERE CustomerId = 1;   -- compare logical reads
SELECT OrderId, Amount FROM Orders WHERE CustomerId = 1;
SET STATISTICS IO OFF;
-- (numbers depend on your data; not executed here)

-- If a query truly needs many columns, return a page (TOP / OFFSET FETCH) not the whole set
```

---

## ⚠️ Common Mistake

```sql
-- ❌ SELECT * inside a view, then SELECT * from the view: schema changes break clients
-- ❌ INSERT INTO t2 SELECT * FROM t1: silently misaligns when a column is added
-- ❌ Putting every column in INCLUDE: index becomes a copy of the table (write cost + size)
-- ❌ Wide scans from a leading-wildcard LIKE '%abc' or a function on the column
```

---

## 🎯 Interview Tip (1 line)
Say: "SELECT * is fine for ad-hoc exploration, never in application code. I list columns, check for key lookups in the plan, and add INCLUDE columns only for hot queries, balancing read gains against index maintenance cost."

---

## 🔗 Related Questions
→ Q103 (Covering index and INCLUDE) | Q107 (Reading an execution plan) | Q108 (STATISTICS IO and TIME) | Q110 (SARGable predicates)
