---

# Q185. Normalization vs Denormalization
# Category: Interview Classics
# Difficulty: ⭐⭐ Medium
# DB: SQL Server (same concepts in MySQL/PostgreSQL; syntax differs only in IDENTITY vs AUTO_INCREMENT)

---

## ❓ Question
An `OrdersFlat` table stores customer name, city and product name on every order row. Normalize it to 3NF, then show one case where you would deliberately denormalize for read performance (an order total stored on the order).

---

## 💡 Quick Concept (2 lines only)
Normalization removes redundancy so each fact is stored once (no update/insert/delete anomalies). Denormalization re-adds controlled redundancy (copied columns, summary columns, indexed views) to avoid joins on hot read paths.
हिंदी: Normalization = हर fact एक ही जगह, anomalies नहीं। Denormalization = read speed के लिए सोच-समझकर duplicate data।

---

## ✅ Answer / Solution

```sql
-- ============================================
-- SETUP: the un-normalized table
-- ============================================
CREATE TABLE dbo.OrdersFlat (
  OrderId      INT PRIMARY KEY,
  CustomerName VARCHAR(100),
  City         VARCHAR(50),
  ProductName  VARCHAR(100),
  UnitPrice    DECIMAL(10,2),
  Qty          INT
);
INSERT INTO dbo.OrdersFlat VALUES
  (1, 'Asha',  'Pune',   'Keyboard', 50.00, 2),
  (2, 'Asha',  'Pune',   'Mouse',    20.00, 1),
  (3, 'Bala',  'Delhi',  'Keyboard', 50.00, 1);
GO
-- Anomaly: if Asha moves to Mumbai you must update many rows; miss one and data disagrees.

-- ============================================
-- 3NF design
-- ============================================
CREATE TABLE dbo.Customers (
  CustomerId INT IDENTITY(1,1) PRIMARY KEY,
  Name       VARCHAR(100) NOT NULL,
  City       VARCHAR(50)  NOT NULL
);
CREATE TABLE dbo.Products (
  ProductId  INT IDENTITY(1,1) PRIMARY KEY,
  Name       VARCHAR(100) NOT NULL UNIQUE,
  UnitPrice  DECIMAL(10,2) NOT NULL
);
CREATE TABLE dbo.Orders (
  OrderId    INT PRIMARY KEY,
  CustomerId INT NOT NULL REFERENCES dbo.Customers(CustomerId),
  OrderTotal DECIMAL(12,2) NULL            -- deliberate denormalization (see below)
);
CREATE TABLE dbo.OrderItems (
  OrderId    INT NOT NULL REFERENCES dbo.Orders(OrderId),
  ProductId  INT NOT NULL REFERENCES dbo.Products(ProductId),
  Qty        INT NOT NULL,
  UnitPrice  DECIMAL(10,2) NOT NULL,       -- price AT TIME OF SALE (a snapshot, not redundancy)
  PRIMARY KEY (OrderId, ProductId)
);
GO

-- Denormalized read: total without joining/aggregating OrderItems each time
SELECT OrderId, OrderTotal FROM dbo.Orders WHERE CustomerId = 1;

-- Keep it correct: recompute on write (or use an indexed view / trigger)
UPDATE o SET OrderTotal = x.Total
FROM dbo.Orders o
JOIN (SELECT OrderId, SUM(Qty * UnitPrice) AS Total FROM dbo.OrderItems GROUP BY OrderId) x
  ON x.OrderId = o.OrderId;

-- EXPECTED: OrderTotal for order 1 (2 x 50.00) = 100.00 ; order 2 (1 x 20.00) = 20.00 ; order 3 = 50.00
-- Arithmetic hand-checked; the UPDATE ... FROM syntax is T-SQL and was only parse-checked, not executed on SQL Server.
-- MySQL/PgSQL: UPDATE ... JOIN (MySQL) / UPDATE ... FROM (PgSQL) differ in syntax.
```

---

## 🔍 Why This Works (3 lines max)
Customer city depends only on the customer, product price on the product, so each moves to its own table keyed by that entity (3NF: non-key columns depend on the key, the whole key, nothing but the key). OrderItems keeps the sale-time price, which is history, not duplication. OrderTotal is a conscious copy that trades write cost for fast reads.
हिंदी: City customer पर depend करती है, इसलिए Customers table में। Sale-time price history है। OrderTotal जानबूझकर duplicate है।

---

## ⚡ Alternative Solution

```sql
-- Instead of a stored OrderTotal column: computed via an indexed view (SQL Server keeps it in sync automatically)
CREATE VIEW dbo.vOrderTotals WITH SCHEMABINDING AS
SELECT OrderId, SUM(Qty * UnitPrice) AS Total, COUNT_BIG(*) AS Cnt
FROM dbo.OrderItems
GROUP BY OrderId;
GO
CREATE UNIQUE CLUSTERED INDEX IX_vOrderTotals ON dbo.vOrderTotals(OrderId);
-- Rules: SCHEMABINDING, two-part names, COUNT_BIG(*), and SUM over a NOT NULL expression are required.
-- Parse-checked only; not executed on SQL Server.
```

---

## ⚠️ Common Mistake

```sql
-- Wrong: over-normalizing (a table per attribute) -> 8-way joins for a simple screen
-- Wrong: denormalizing with no plan to keep it in sync (total drifts from items)
-- Wrong: "normalization is always right" - OLTP likes 3NF, reporting/analytics (star schema) deliberately denormalizes
-- Wrong: storing the current product price only; historical orders then change when the price changes
```

---

## 🎯 Interview Tip (1 line)
Say: "I normalize to 3NF for the OLTP core, then denormalize only where I can measure a hot read path - and I state how the copy stays consistent (computed on write, trigger, indexed view). Reporting goes to a star schema or read replica." Give the order-total and sale-price examples.

---

## 🔗 Related Questions
→ Q035 (Normalization in practice) | Q092 (Indexed views) | Q026 (PK/FK) | Q186 (E-commerce schema) | Q029 (Computed columns)
