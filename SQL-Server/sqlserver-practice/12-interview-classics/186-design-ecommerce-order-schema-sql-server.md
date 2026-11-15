---

# Q186. Design a Schema for an E-Commerce Order System (SQL Server)
# Category: Interview Classics
# Difficulty: ⭐⭐⭐ Hard
# DB: SQL Server (MySQL: AUTO_INCREMENT/ENUM; PostgreSQL: IDENTITY/jsonb)

---

## ❓ Question
Design tables for customers, products, orders, order items and payments. Requirements: money is exact, an order has many items, price at purchase time is preserved, status values are controlled, stock cannot go negative, and the common query "latest 20 orders of a customer" is fast.

---

## 💡 Quick Concept (2 lines only)
Model entities with PK/FK, store money as DECIMAL, snapshot price on the line item, enforce rules with CHECK/FK constraints, and index for the real queries (FK columns + sort column). Use DATETIME2 and an explicit status lookup or CHECK.
हिंदी: Entities के लिए PK/FK, पैसा DECIMAL में, item पर sale-time price। Rules constraints से और index real queries के हिसाब से।

---

## ✅ Answer / Solution

```sql
-- ============================================
-- SCHEMA
-- ============================================
CREATE TABLE dbo.Customers (
  CustomerId INT IDENTITY(1,1) CONSTRAINT PK_Customers PRIMARY KEY,
  Email      NVARCHAR(256) NOT NULL CONSTRAINT UQ_Customers_Email UNIQUE,
  FullName   NVARCHAR(200) NOT NULL,
  CreatedAt  DATETIME2(3)  NOT NULL CONSTRAINT DF_Customers_CreatedAt DEFAULT SYSUTCDATETIME()
);

CREATE TABLE dbo.Products (
  ProductId  INT IDENTITY(1,1) CONSTRAINT PK_Products PRIMARY KEY,
  Sku        VARCHAR(40)   NOT NULL CONSTRAINT UQ_Products_Sku UNIQUE,
  Name       NVARCHAR(200) NOT NULL,
  Price      DECIMAL(10,2) NOT NULL CONSTRAINT CK_Products_Price CHECK (Price >= 0),
  StockQty   INT           NOT NULL CONSTRAINT CK_Products_Stock CHECK (StockQty >= 0),
  RowVer     ROWVERSION                      -- optimistic concurrency token
);

CREATE TABLE dbo.Orders (
  OrderId     BIGINT IDENTITY(1,1) CONSTRAINT PK_Orders PRIMARY KEY,
  CustomerId  INT NOT NULL CONSTRAINT FK_Orders_Customers REFERENCES dbo.Customers(CustomerId),
  Status      VARCHAR(20) NOT NULL CONSTRAINT DF_Orders_Status DEFAULT 'Pending'
              CONSTRAINT CK_Orders_Status CHECK (Status IN ('Pending','Paid','Shipped','Cancelled','Refunded')),
  OrderTotal  DECIMAL(12,2) NOT NULL CONSTRAINT DF_Orders_Total DEFAULT 0,
  CreatedAt   DATETIME2(3) NOT NULL CONSTRAINT DF_Orders_CreatedAt DEFAULT SYSUTCDATETIME()
);

CREATE TABLE dbo.OrderItems (
  OrderId    BIGINT NOT NULL CONSTRAINT FK_OrderItems_Orders REFERENCES dbo.Orders(OrderId) ON DELETE CASCADE,
  LineNo     INT    NOT NULL,
  ProductId  INT    NOT NULL CONSTRAINT FK_OrderItems_Products REFERENCES dbo.Products(ProductId),
  Qty        INT    NOT NULL CONSTRAINT CK_OrderItems_Qty CHECK (Qty > 0),
  UnitPrice  DECIMAL(10,2) NOT NULL,               -- price snapshot at purchase time
  LineTotal  AS (Qty * UnitPrice) PERSISTED,        -- computed column
  CONSTRAINT PK_OrderItems PRIMARY KEY (OrderId, LineNo)
);

CREATE TABLE dbo.Payments (
  PaymentId  BIGINT IDENTITY(1,1) CONSTRAINT PK_Payments PRIMARY KEY,
  OrderId    BIGINT NOT NULL CONSTRAINT FK_Payments_Orders REFERENCES dbo.Orders(OrderId),
  Amount     DECIMAL(12,2) NOT NULL CONSTRAINT CK_Payments_Amount CHECK (Amount > 0),
  Method     VARCHAR(20) NOT NULL,
  PaidAt     DATETIME2(3) NOT NULL CONSTRAINT DF_Payments_PaidAt DEFAULT SYSUTCDATETIME()
);
GO

-- ============================================
-- INDEXES for the real queries
-- ============================================
-- SQL Server does NOT auto-index foreign keys (MySQL InnoDB does; PostgreSQL does not).
CREATE INDEX IX_Orders_Customer_Created ON dbo.Orders (CustomerId, CreatedAt DESC) INCLUDE (Status, OrderTotal);
CREATE INDEX IX_OrderItems_Product      ON dbo.OrderItems (ProductId);
CREATE INDEX IX_Payments_Order          ON dbo.Payments (OrderId);
GO

-- Latest 20 orders of a customer -> index seek on (CustomerId), already ordered, covering
SELECT TOP (20) OrderId, Status, OrderTotal, CreatedAt
FROM dbo.Orders
WHERE CustomerId = 42
ORDER BY CreatedAt DESC;

-- EXPECTED: no rows on an empty schema. DDL/queries parse-checked with sqlglot (tsql); not executed on SQL Server.
-- Plan shape (index seek, no sort) is the expected design intent per Microsoft docs, not captured plan output.
```

---

## 🔍 Why This Works (3 lines max)
DECIMAL avoids float rounding; CHECK/FK constraints put business rules in the database where every client obeys them; the UnitPrice snapshot keeps history correct when product prices change. The composite index (CustomerId, CreatedAt DESC) with INCLUDE serves the hot query with a seek and no sort.
हिंदी: Constraints DB level पर rules enforce करते हैं। UnitPrice snapshot history safe रखता है। (CustomerId, CreatedAt) index से query seek पर चलती है।

---

## ⚡ Alternative Solution

```sql
-- Status as a lookup table instead of CHECK (easier to extend/localize, FK-enforced)
CREATE TABLE dbo.OrderStatuses (StatusCode VARCHAR(20) PRIMARY KEY, Description NVARCHAR(100) NOT NULL);
-- Orders.Status REFERENCES dbo.OrderStatuses(StatusCode)

-- Addresses, shipments, coupons: separate tables (Addresses 1-N Customers, Shipments 1-N Orders)
-- Very high volume: partition Orders by CreatedAt (month) and archive old partitions
```

---

## ⚠️ Common Mistake

```sql
-- Wrong: price FLOAT / MONEY arithmetic       -> rounding surprises (use DECIMAL(p,s))
-- Wrong: only current Products.Price used when reading old orders -> history changes
-- Wrong: DATETIME with local time            -> use DATETIME2 + UTC
-- Wrong: no index on FK columns              -> DELETE/JOIN scans, more blocking
-- Wrong: NVARCHAR(MAX) for everything        -> can't be index key, wasted memory grants
-- Wrong: ON DELETE CASCADE from Customers to Orders -> one delete wipes financial records; cascade only item rows
```

---

## 🎯 Interview Tip (1 line)
Say: "I start from the queries and invariants - exact money, immutable price snapshot, stock >= 0 via CHECK plus an atomic UPDATE ... WHERE StockQty >= @qty, and indexes on FK + sort columns. Then I discuss growth: partitioning, archiving, read replicas, and Azure SQL tier." Draw the ER diagram first and name the cardinalities.

---

## 🔗 Related Questions
→ Q025 (CREATE TABLE) | Q026 (PK/FK) | Q027 (CHECK/DEFAULT) | Q103 (Covering index) | Q029 (Computed columns) | Q127 (rowversion)
